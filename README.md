# 📘 Documentação Versionada de Milestones do GitLab

Este projeto automatiza a **geração de documentação técnica versionada** a partir de **milestones e issues de um projeto no GitLab**, transformando dados operacionais da ferramenta em **artefatos documentais versionados no Git**.

O Git passa a ser a **fonte de verdade da documentação**, enquanto o GitLab permanece como ferramenta de gestão.

---

## 🎯 Objetivo

Resolver problemas comuns em projetos de software:

* ❌ Milestones sem versionamento
* ❌ Histórico dependente apenas do GitLab
* ❌ Falta de rastreabilidade documental
* ❌ Ausência de documentação técnica evolutiva

Com este projeto, cada milestone do GitLab gera um **arquivo Markdown versionado**, preservando histórico, métricas e contexto.

---

## 🧠 Conceito da Solução

Fluxo da arquitetura:

```
GitLab (Milestones + Issues)
        ↓
   GitLab REST API
        ↓
 Script de extração (Python)
        ↓
 Geração de Markdown
        ↓
 Versionamento no Git
```

📌 A documentação passa a evoluir junto com o código.

---

## 📂 Estrutura do Repositório

```
serpro-project/
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── docs/
│   └── milestones/
└── scripts/
    └── generate_milestones_docs.py
```

* `scripts/` → lógica de extração e geração
* `docs/milestones/` → documentação gerada (versionada)
* `.env` → variáveis sensíveis (não versionado)

---

## 🛠️ Pré-requisitos

* Python 3.8+
* Conta no GitLab
* Projeto com milestones e issues
* Personal Access Token (PAT) com acesso de leitura à API

---

## 🔐 Configuração de Ambiente

### 1️⃣ Criar o arquivo `.env` na raiz do projeto

```env
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxx
GITLAB_PROJECT_ID=123456
GITLAB_BASE_URL=https://gitlab.com/api/v4
```

---

### 2️⃣ Instalar dependências

Recomendado usar ambiente virtual:

```bash
python -m venv .venv
```

Ativar:

**Windows**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

Instalar dependências:

```bash
python -m pip install -r requirements.txt
```

---

## ▶️ Execução do Script

Execute a partir da raiz do projeto:

```bash
python scripts/generate_milestones_docs.py
```

Resultado esperado:

* Um arquivo `.md` para cada milestone
* Arquivos criados em `docs/milestones/`
* Conteúdo padronizado e reprodutível

---

## 📝 Exemplo de Documento Gerado

```markdown
# Milestone: Sprint 01

Período: 01/03/2025 – 14/03/2025  
Status: Concluído

## Objetivo
Implementação da autenticação do sistema

## Issues
- #12 Criar tela de login (closed)
- #15 Backend de autenticação (closed)

## Métricas
- Total de issues: 2
- Concluídas: 2
- Progresso: 100%

## Observações
Documentação gerada automaticamente via API do GitLab.
```

---

## 🔄 Versionamento da Documentação

Após a geração:

```bash
git add docs/milestones/
git commit -m "docs: gera documentação dos milestones"
```

✔️ Histórico preservado
✔️ Alterações auditáveis
✔️ Backup automático

---

## 🤖 Automação (Opcional)

O script pode ser integrado a:

* GitLab CI/CD
* Pipelines agendados
* Execução pós-merge

Exemplo de uso:

```
Merge → Pipeline → Geração de docs → Commit automático
```

---

## 📌 Boas Práticas Adotadas

* ✔️ Milestones como artefato de planejamento
* ✔️ Markdown como documentação técnica
* ✔️ Git como fonte de verdade
* ✔️ Documentação sempre gerada via script
* ❌ Nunca editar os arquivos manualmente

---

## ⚠️ Limitações Conhecidas

* Requer manutenção do script
* Dependente da estrutura do GitLab
* Paginação da API pode exigir ajustes em projetos grandes

📌 Em projetos médios e grandes, os benefícios superam amplamente os custos.

---

## 🚀 Próximos Passos (Evoluções Possíveis)

* Geração de `index.md`
* Integração com MkDocs ou GitLab Pages
* Inclusão de épicos e labels
* Métricas avançadas (lead time, throughput)
* Suporte a GitLab self-hosted

---

## 📄 Licença

Este projeto pode ser adaptado livremente conforme as necessidades da equipe.


