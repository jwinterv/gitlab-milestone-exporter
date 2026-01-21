"""
Gera documentação Markdown versionada a partir de milestones e issues do GitLab.

Requisitos:
- Python 3.8+
- requests

Variáveis de ambiente obrigatórias:
- GITLAB_TOKEN
- GITLAB_PROJECT_ID
Opcional:
- GITLAB_BASE_URL (default: https://gitlab.com/api/v4)
"""

import os
import requests
from datetime import datetime
from pathlib import Path
from slugify import slugify
from dotenv import load_dotenv

# Carrega variáveis do .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
PROJECT_ID = os.getenv("GITLAB_PROJECT_ID")
BASE_URL = os.getenv("GITLAB_BASE_URL", "https://gitlab.com/api/v4")

DOCS_DIR = Path("../docs/milestones")

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


# ==========================================================
# EXTRAÇÃO DE DADOS
# ==========================================================

def get_milestones():
    return api_get(
        f"/projects/{PROJECT_ID}/milestones",
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

# ==========================================================
# GERAÇÃO DE MARKDOWN
# ==========================================================

def generate_markdown(milestone, issues):
    total = len(issues)
    closed = sum(1 for i in issues if i["state"] == "closed")
    progress = int((closed / total) * 100) if total > 0 else 0

    issues_md = "\n".join(
        f"- #{i['iid']} {i['title']} ({i['state']})"
        for i in issues
    ) or "_Nenhuma issue associada_"

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

## Observações
_Documentação gerada automaticamente via API do GitLab._
"""


# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================

def main():
    print("📥 Buscando milestones...")
    milestones = get_milestones()

    if not milestones:
        print("⚠️ Nenhum milestone encontrado.")
        return

    for milestone in milestones:
        print(f"📝 Gerando doc: {milestone['title']}")

        issues = get_issues_for_milestone(milestone["title"])
        markdown = generate_markdown(milestone, issues)

        filename = f"{slugify(milestone['title'])}.md"
        filepath = DOCS_DIR / filename

        filepath.write_text(markdown, encoding="utf-8")

    print("✅ Documentação gerada com sucesso.")


if __name__ == "__main__":
    main()
