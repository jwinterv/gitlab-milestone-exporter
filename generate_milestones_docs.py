'''
Variáveis de ambiente obrigatórias:
- GITLAB_TOKEN
- GITLAB_BASE_URL (default: https://gitlab.com/api/v4)
'''
import os
import requests
import re
from datetime import datetime
from pathlib import Path
from slugify import slugify
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(".env")

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
API_URL = os.getenv("GITLAB_BASE_URL", "https://gitlab.com/api/v4").rstrip('/')

DOCS_DIR = BASE_DIR / "docs"

HEADERS = {
    "PRIVATE-TOKEN": GITLAB_TOKEN
}

if not GITLAB_TOKEN:
    raise RuntimeError("Defina GITLAB_TOKEN como variável de ambiente.")

DOCS_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================================
# FUNÇÕES DE DOWNLOAD
# ==========================================================

def download_uploads(content, target_dir, project_id):
    if not content:
        return content
    
    # Regex atualizada para capturar o link e ignorar o bloco de tamanho {width...}
    pattern = r'(!\[.*?\])\((.*?(?:/uploads/)([0-9a-f]+)/([^\s\)]+))\)(\s*\{.*?\})?'
    
    images_dir = target_dir / "images"
    
    def replace_match(match):
        alt_text = match.group(1)
        secret = match.group(3)
        filename = match.group(4).split('?')[0]
        
        api_download_url = f"{API_URL}/projects/{project_id}/uploads/{secret}/{filename}"
        local_path = images_dir / filename
        
        try:
            images_dir.mkdir(parents=True, exist_ok=True)
            with requests.get(api_download_url, headers=HEADERS, stream=True, allow_redirects=True) as r:
                if r.status_code == 200:
                    with open(local_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"    ✅ Imagem baixada: {filename}")
                    return f"{alt_text}(images/{filename})"
                else:
                    return match.group(0)
        except Exception as e:
            return match.group(0)

    return re.sub(pattern, replace_match, content)

# ==========================================================
# API E AUXILIARES
# ==========================================================

def api_get(endpoint, params=None):
    url = f"{API_URL}{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def format_date(date_str):
    if not date_str: return "—"
    return datetime.fromisoformat(date_str.replace("Z", "")).strftime("%d/%m/%Y")

def sort_issues_by_status(issues):
    return sorted(issues, key=lambda i: 0 if i["state"] == "opened" else 1)

def get_project(project_id): return api_get(f"/projects/{project_id}")
def get_milestones(project_id): return api_get(f"/projects/{project_id}/milestones", params={"per_page": 100})
def get_issue_details(project_id, issue_iid): return api_get(f"/projects/{project_id}/issues/{issue_iid}")
def get_issue_notes(project_id, issue_iid): return api_get(f"/projects/{project_id}/issues/{issue_iid}/notes", params={"per_page": 100})
def get_issues_for_milestone(project_id, milestone_title): return api_get(f"/projects/{project_id}/issues", params={"milestone": milestone_title, "per_page": 100})

def issue_link(issue):
    slug = f"issue-{issue['iid']}-{slugify(issue['title'])}"
    # Ajustado: caminho relativo direto ao arquivo para o VS Code Preview navegar
    return f"[#{issue['iid']} {issue['title']}]({slug}/README.md)"

# ==========================================================
# GERAÇÃO DE MARKDOWN
# ==========================================================

def generate_markdown(milestone, issues, project_id, milestone_dir):
    total = len(issues)
    closed = sum(1 for i in issues if i["state"] == "closed")
    progress = int((closed / total) * 100) if total > 0 else 0

    desc = download_uploads(milestone.get('description', ''), milestone_dir, project_id)

    issues_md = "## Sumário de Issues\n\n"
    open_issues = [i for i in issues if i["state"] == "opened"]
    closed_issues = [i for i in issues if i["state"] == "closed"]

    if open_issues:
        issues_md += "### 🔴 Abertas\n" + "\n".join(f"- {issue_link(i)}" for i in open_issues) + "\n\n"
    if closed_issues:
        issues_md += "### 🟢 Fechadas\n" + "\n".join(f"- {issue_link(i)}" for i in closed_issues)

    return f"""# Milestone: {milestone['title']}
Período: {format_date(milestone['start_date'])} – {format_date(milestone['due_date'])}  
Status: {milestone['state'].capitalize()}

## Objetivo
{desc or '_Sem descrição_'}

## Issues
{issues_md or '_Nenhuma issue_'}

## Métricas
- Total: {total} | Concluídas: {closed} | Progresso: {progress}%
"""

def generate_issue_markdown(issue, notes, prev_issue, next_issue, project_id, issue_dir):
    description_fixed = download_uploads(issue.get("description", ""), issue_dir, project_id)

    processed_notes = []
    for n in notes:
        if not n.get("system"):
            note_body = download_uploads(n['body'], issue_dir, project_id)
            processed_notes.append(f"- **{n['author']['name']}** ({format_date(n['created_at'])}):\n  {note_body}")

    notes_md = "\n".join(processed_notes) or "_Sem comentários_"
    
    # Ajustado: links de navegação relativos apontando diretamente para README.md
    nav = ["↑ [Voltar para a milestone](../README.md)"]
    if prev_issue:
        prev_slug = f"issue-{prev_issue['iid']}-{slugify(prev_issue['title'])}"
        nav.insert(0, f"← [Issue anterior](../{prev_slug}/README.md)")
    if next_issue:
        next_slug = f"issue-{next_issue['iid']}-{slugify(next_issue['title'])}"
        nav.append(f"→ [Próxima issue](../{next_slug}/README.md)")

    labels = ", ".join(issue["labels"]) or "—"
    assignee = issue["assignee"]["name"] if issue["assignee"] else "—"

    return f"""# Issue #{issue['iid']} – {issue['title']}
{" | ".join(nav)}

---
**Status:** {issue['state']} | **Autor:** {issue['author']['name']} | **Responsável:** {assignee}
**Labels:** {labels} | **Criada em:** {format_date(issue['created_at'])}

---
## Descrição
{description_fixed}

---
## Comentários
{notes_md}
"""

# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================

def main():
    raw = input("Informe os IDs dos projetos GitLab (separados por vírgula): ")
    project_ids = [p.strip() for p in raw.split(",") if p.strip()]

    for project_id in project_ids:
        print(f"\n📦 Projeto {project_id}")
        
        project = get_project(project_id)
        real_id = project["id"]
        project_dir = DOCS_DIR / slugify(project["path_with_namespace"])
        project_dir.mkdir(parents=True, exist_ok=True)

        print("📥 Processando milestones...")
        milestones = get_milestones(real_id)

        for milestone in milestones:
            m_slug = slugify(milestone["title"])
            m_dir = project_dir / m_slug
            m_dir.mkdir(parents=True, exist_ok=True)

            print(f"  📁 Milestone: {milestone['title']}")
            issues = sort_issues_by_status(get_issues_for_milestone(real_id, milestone["title"]))

            readme = generate_markdown(milestone, issues, real_id, m_dir)
            (m_dir / "README.md").write_text(readme, encoding="utf-8")

            for index, issue in enumerate(issues):
                print(f"    📝 Issue #{issue['iid']}")
                i_slug = f"issue-{issue['iid']}-{slugify(issue['title'])}"
                i_dir = m_dir / i_slug
                i_dir.mkdir(parents=True, exist_ok=True)

                details = get_issue_details(real_id, issue["iid"])
                notes = get_issue_notes(real_id, issue["iid"])
                
                prev_i = issues[index - 1] if index > 0 else None
                next_i = issues[index + 1] if index < len(issues) - 1 else None

                issue_md = generate_issue_markdown(details, notes, prev_i, next_i, real_id, i_dir)
                (i_dir / "README.md").write_text(issue_md, encoding="utf-8")

    print("\n✅ Documentação gerada com sucesso.")

if __name__ == "__main__":
    main()