# Avante Almoxarifado

Sistema web de gestão de materiais, estoque, empréstimos e operações do almoxarifado do laboratório.

> **Estado do repositório:** baseline recebida em 03/11/2026. Esta publicação registra o estado atual do código antes da evolução arquitetural. Não representa, por si só, uma versão homologada para produção.

## Stack identificada

- **Frontend:** Next.js 16, React 19, TypeScript.
- **Backend:** Python 3.11–3.12, FastAPI, SQLAlchemy.
- **Banco de dados:** PostgreSQL 16.
- **Migrações:** Alembic.
- **Autenticação:** JWT transportado em cookie `HttpOnly`.
- **Execução atual:** Docker Compose; há instruções históricas para execução local.

## Estrutura

```text
lab_almoxarifado/
├── backend/                  # API, modelos, serviços e testes
├── frontend/                 # Aplicação Next.js
├── .github/workflows/        # Pipeline inicial de CI
├── docker-compose.yml        # Execução atual por Docker
└── docker-compose.test.yml   # Ambiente de testes
```

## Estado de validação

A inspeção estática identificou 37 declarações de rotas na API e 120 funções `test_*` distribuídas em sete arquivos Python. Isso **não significa que 120 testes tenham sido executados ou aprovados nesta preparação**.

O README histórico registra uma execução anterior de testes. Essa evidência precisa ser reproduzida no ambiente atual. Build, testes integrados, migrações em banco real, comportamento multiusuário e instalação em dispositivos precisam de homologação atualizada.

## Execução

Consulte os arquivos de configuração e instruções existentes no projeto. Antes de executar migrations em banco com dados importantes, faça backup e comprove a restauração.

## Direção

A evolução do produto deverá preservar a integridade dos dados, segurança, compatibilidade e operação do laboratório. A arquitetura e o processo de implantação devem ser validados antes de remover a infraestrutura atual.
