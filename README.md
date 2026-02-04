# 📌 GitLab Milestones & Issues Exporter

Este projeto tem como objetivo **exportar milestones e issues de um projeto GitLab para arquivos Markdown**, criando uma **documentação navegável local**, organizada por milestones e issues, ideal para uso no **VS Code**, estudo offline e versionamento.

O resultado final funciona como uma **wiki local sincronizada com o GitLab**.

---

## 🎯 Objetivos

* **Exportação Completa:** Milestones, Issues e seus respectivos comentários.
* **Gestão de Mídia:** Download automático de imagens anexadas.
* **Limpeza de Markdown:** Remoção de metadados de redimensionamento do GitLab (ex: `{width=...}`).
* **Estrutura Navegável:** Links relativos de "Anterior", "Próximo" e "Voltar" entre documentos.
* **Portabilidade:** Documentação pronta para ser versionada ou convertida em site estático.

---

## 📁 Estrutura Gerada

```text
docs/
└── nome-do-projeto/
    └── nome-da-milestone/
        ├── README.md
        ├── images/                # Imagens da Milestone
        └── issue-123-titulo/
            ├── README.md
            └── images/            # Imagens específicas da Issue e comentários

```

* **Milestone README:** Resumo, período, progresso e lista de issues.
* **Issue README:** Status, autor, responsável, labels, descrição completa e histórico de comentários.

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
GITLAB_BASE_URL=https://gitlab.com/api/v4

```

---

## 📦 Dependências

Instale as dependências necessárias via pip:

```bash
pip install -r requirements.txt

```

---

## ▶️ Como Executar

1. Certifique-ce de que o `.env` está configurado.
2. Execute o script:
```bash
python generate_milestone_docs.py

```


3. Informe o(s) **ID(s) do(s) projeto(s)** quando solicitado (ex: `123, 456`).
4. A documentação será gerada na pasta `docs/`.

---

## 🧭 Visualização no VS Code (Recomendado)

Para uma experiência de wiki real, utilize o motor de renderização do VS Code:

1. Abra qualquer arquivo `README.md` gerado.
2. Use o atalho `Ctrl + Shift + V` (Windows/Linux) ou `Cmd + Shift + V` (Mac).
3. **Navegação:** Clique nos links das issues ou nos botões de navegação para saltar entre os arquivos.

---

## 🛠️ Soluções Técnicas Aplicadas

* **Download Blindado:** O script utiliza o endpoint `/projects/:id/uploads/...` da API para garantir que o token de acesso seja aceito, evitando redirecionamentos para tela de login.
* **Regex Inteligente:** Identifica links de imagens mesmo com formatações complexas e limpa atributos de largura/altura que poluem o texto puro.
* **Sanitização de Nomes:** Utiliza `python-slugify` para garantir que pastas e arquivos sejam compatíveis com todos os sistemas operacionais (evitando espaços e caracteres especiais).

---

## 📈 Possíveis Melhorias Futuras

* Implementar suporte ao **MkDocs** para gerar sites estáticos profissionais.
* Exportação de anexo em PDF único.
* Filtragem de issues por labels específicas.


