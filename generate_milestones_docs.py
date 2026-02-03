'''
Variáveis de ambiente obrigatórias:
- GITLAB_TOKEN
- GITLAB_PROJECT_ID
Opcional:
- GITLAB_BASE_URL (default: https://gitlab.com/api/v4)
'''
import os
import requests
from datetime import datetime
from pathlib import Path
from slugify import slugify
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
PROJECT_ID = os.getenv("GITLAB_PROJECT_ID")
BASE_URL = os.getenv("GITLAB_BASE_URL", "https://gitlab.com/api/v4")

DOCS_DIR = BASE_DIR / "docs" / "milestones"

HEADERS = {
    "PRIVATE-TOKEN": GITLAB_TOKEN
}

if not GITLAB_TOKEN or not PROJECT_ID:
    raise RuntimeError("Defina GITLAB_TOKEN e GITLAB_PROJECT_ID como variáveis de ambiente.")

DOCS_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def api_get(endpoint, params=None):
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()


def format_date(date_str):
    if not date_str:
        return "—"
    return datetime.fromisoformat(date_str.replace("Z", "")).strftime("%d/%m/%Y")

def sort_issues_by_status(issues):
    return sorted(
        issues,
        key=lambda i: 0 if i["state"] == "opened" else 1
    )

# ==========================================================
# EXTRAÇÃO DE DADOS
# ==========================================================

def get_milestones():
    return api_get(
        f"/projects/{PROJECT_ID}/milestones",
        params={"per_page": 100}
    )

def get_issue_details(issue_iid):
    return api_get(f"/projects/{PROJECT_ID}/issues/{issue_iid}")

def get_issue_notes(issue_iid):
    return api_get(
        f"/projects/{PROJECT_ID}/issues/{issue_iid}/notes",
        params={"per_page": 100}
    )

def get_issues_for_milestone(milestone_title):
    return api_get(
        f"/projects/{PROJECT_ID}/issues",
        params={
            "milestone": milestone_title,
            "per_page": 100
        }
    )
def issue_link(issue):
    slug = f"issue-{issue['iid']}-{slugify(issue['title'])}"
    return f"[#{issue['iid']} {issue['title']}]({slug}/)"


# ==========================================================
# GERAÇÃO DE MARKDOWN
# ==========================================================

def generate_markdown(milestone, issues):
    total = len(issues)
    closed = sum(1 for i in issues if i["state"] == "closed")
    progress = int((closed / total) * 100) if total > 0 else 0

    open_issues = [i for i in issues if i["state"] == "opened"]
    closed_issues = [i for i in issues if i["state"] == "closed"]

    issues_md = "## Sumário de Issues\n\n"

    if open_issues:
        issues_md += "### 🔴 Abertas\n"
        issues_md += "\n".join(
            f"- {issue_link(i)}"
            for i in open_issues
        )
        issues_md += "\n\n"

    if closed_issues:
        issues_md += "### 🟢 Fechadas\n"
        issues_md += "\n".join(
            f"- {issue_link(i)}"
            for i in closed_issues
        )

    issues_md = issues_md.strip() or "_Nenhuma issue associada_"

    return f"""# Milestone: {milestone['title']}

Período: {format_date(milestone['start_date'])} – {format_date(milestone['due_date'])}  
Status: {milestone['state'].capitalize()}

## Objetivo
{milestone.get('description') or '_Sem descrição_'}

## Issues
{issues_md}

## Métricas
- Total de issues: {total}
- Concluídas: {closed}
- Progresso: {progress}%

"""

def generate_issue_markdown(issue, notes, prev_issue, next_issue):
    nav = []

    if prev_issue:
        prev_slug = f"issue-{prev_issue['iid']}-{slugify(prev_issue['title'])}"
        nav.append(f"← [Issue anterior](../{prev_slug}/)")

    nav.append("↑ [Voltar para a milestone](../)")

    if next_issue:
        next_slug = f"issue-{next_issue['iid']}-{slugify(next_issue['title'])}"
        nav.append(f"→ [Próxima issue](../{next_slug}/)")

    navigation = " | ".join(nav)

    description = issue.get("description") or "_Sem descrição_"

    notes_md = "\n".join(
        f"- **{n['author']['name']}** ({format_date(n['created_at'])}):\n"
        f"  {n['body']}"
        for n in notes
        if not n.get("system")
    ) or "_Sem comentários_"

    labels = ", ".join(issue["labels"]) or "—"
    assignee = issue["assignee"]["name"] if issue["assignee"] else "—"

    return f"""# Issue #{issue['iid']} – {issue['title']}
{navigation}

---

**Status:** {issue['state']}  
**Autor:** {issue['author']['name']}  
**Responsável:** {assignee}  
**Labels:** {labels}  
**Criada em:** {format_date(issue['created_at'])}  
**Atualizada em:** {format_date(issue['updated_at'])}

---

## Descrição
{description}

---

## Comentários
{notes_md}
"""


# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================

def main():
    print("📥 Buscando milestones...")
    milestones = get_milestones()

    for milestone in milestones:
        milestone_slug = slugify(milestone["title"])
        milestone_dir = DOCS_DIR / milestone_slug
        milestone_dir.mkdir(parents=True, exist_ok=True)

        print(f"📁 Milestone: {milestone['title']}")

        issues = sort_issues_by_status(
            get_issues_for_milestone(milestone["title"])
        )

        readme = generate_markdown(milestone, issues)
        (milestone_dir / "README.md").write_text(readme, encoding="utf-8")

        for index, issue in enumerate(issues):
            prev_issue = issues[index - 1] if index > 0 else None
            next_issue = issues[index + 1] if index < len(issues) - 1 else None

            print(f"  📝 Issue #{issue['iid']}")

            issue_slug = f"issue-{issue['iid']}-{slugify(issue['title'])}"
            issue_dir = milestone_dir / issue_slug
            issue_dir.mkdir(parents=True, exist_ok=True)

            images_dir = issue_dir / "images"

            issue_details = get_issue_details(issue["iid"])
            notes = get_issue_notes(issue["iid"])

            issue_md = generate_issue_markdown(
                issue_details,
                notes,
                prev_issue,
                next_issue
            )

            (issue_dir / "README.md").write_text(issue_md, encoding="utf-8")

    print("✅ Documentação por issue gerada com sucesso.")

if __name__ == "__main__":
    main()
