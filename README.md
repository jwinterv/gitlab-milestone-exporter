# 📌 GitLab Milestones & Issues Exporter (com Imagens)

Este projeto tem como objetivo **exportar milestones e issues de um projeto GitLab para arquivos Markdown**, criando uma **documentação navegável local**, organizada por milestones e issues, ideal para uso no **VS Code**, estudo offline e versionamento.

O resultado final funciona como uma **wiki local sincronizada com o GitLab**.

---

## 🎯 Objetivos

- **Exportação Completa:** Milestones, Issues e seus respectivos comentários.
- **Gestão de Mídia:** Download automático de imagens anexadas.
- **Limpeza de Markdown:** Remoção de metadados de redimensionamento do GitLab (ex: `{width=...}`).
- **Navegação Real:** Links diretos entre os `README.md` para transição imediata entre páginas no VS Code.
- **Portabilidade:** Documentação pronta para ser versionada ou convertida em site estático.

---

## 📁 Estrutura Gerada

```text
docs/
└── nome-do-projeto/
    └── nome-da-milestone/
        ├── README.md              # Sumário com links diretos
        ├── images/                # Imagens da Milestone
        └── issue-123-titulo/
            ├── README.md          # Conteúdo da Issue com navegação
            └── images/            # Imagens da Issue e comentários

```

---

## 🔧 Pré-requisitos

* Python **3.9+**
* Conta no GitLab
* **Personal Access Token (PAT)** com escopo `read_api`.

---

## 🔐 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
GITLAB_TOKEN=seu_token_pessoal_aqui
GITLAB_BASE_URL=[https://gitlab.com/api/v4](https://gitlab.com/api/v4)

```

---

## 📦 Dependências

Instale as dependências necessárias via pip:

```bash
pip install -r requirements.txt

```

---

## ▶️ Como Executar

1. Certifique-se de que o `.env` está configurado.
2. Execute o script:

```bash
python generate_milestone_docs.py

```

3. Informe o(s) **ID(s) do(s) projeto(s)** quando solicitado (ex: `123, 456`).
4. A documentação será gerada na pasta `docs/`.

---

## 🧭 Visualização no VS Code (Recomendado)

Para que a navegação funcione corretamente como uma Wiki, é altamente recomendado o uso de uma extensão dedicada:

### 1. Extensão Necessária

Instale a extensão **Markdown All in One** através do Marketplace do VS Code. Ela melhora significativamente o suporte a links relativos entre arquivos.

### 2. Modo Preview

A navegação (clicar no link e trocar de página) só ocorre dentro do modo de visualização renderizada:

1. Abra o arquivo `README.md` principal da milestone ou de uma issue.
2. Use o atalho `Ctrl + Shift + V` (Windows/Linux) ou `Cmd + Shift + V` (Mac).
3. **Navegação:** No painel de Preview, clique nos links. O VS Code carregará o novo arquivo na mesma janela.

---

## 🛠️ Soluções Técnicas Aplicadas

* **Download Blindado:** O script utiliza o endpoint `/projects/:id/uploads/...` da API para garantir que o token de acesso seja aceito, evitando redirecionamentos para tela de login.
* **Regex Inteligente:** Identifica links de imagens e remove atributos extras que poluem o visual.
* **Caminhos Relativos:** Todos os links apontam diretamente para arquivos `.md` específicos, permitindo navegação fluida dentro do Preview.

---

## 📈 Possíveis Melhorias Futuras

* Implementar suporte ao **MkDocs** para gerar sites estáticos profissionais.
* Exportação para PDF consolidado.
* Filtragem de issues por labels específicas.



