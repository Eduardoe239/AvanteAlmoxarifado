# DATABASE.md — Schema atual (baseline V1)

Extraído diretamente de `backend/models.py` e da cadeia de migrations em `backend/alembic/versions/` (F0-07). Este é o modelo **antigo** (item = catálogo + unidade fundidos), que a Fase 2 do plano vai substituir — este documento existe para servir de referência exata do "antes" na hora do backfill.

## Tabelas

### `setores`
| Coluna | Tipo | Constraints |
|---|---|---|
| id | Integer | PK |
| nome | String(100) | UNIQUE, NOT NULL |

Lista fixa, seedada via migration `034489a950b0` — não editável pela aplicação.

### `usuarios`
| Coluna | Tipo | Constraints |
|---|---|---|
| id | Integer | PK |
| username | String(100) | UNIQUE, NOT NULL, indexado |
| hashed_password | String(255) | NOT NULL |
| nome_completo | String(150) | nullable |
| email | String(255) | UNIQUE, nullable |
| setor_id | Integer | FK → setores.id, nullable |
| is_admin | Boolean | default False |
| ativo | Boolean | default True |

### `itens`
| Coluna | Tipo | Constraints |
|---|---|---|
| id | Integer | PK |
| nome | String(150) | NOT NULL |
| patrimonio | String(50) | UNIQUE, nullable |
| codigo_qr | String(120) | UNIQUE, nullable, indexado |
| area | String(120) | nullable |
| setor_atual_id | Integer | FK → setores.id, nullable |
| quantidade_total | Integer | NOT NULL |
| quantidade_disponivel | Integer | NOT NULL |
| status | String(20) | default "ATIVO" — **livre, sem enum** |

> Catálogo (tipo do item) e unidade física continuam fundidos nesta tabela — é o gap central já registrado na auditoria (seção 2 do relatório).

### `emprestimos`
| Coluna | Tipo | Constraints |
|---|---|---|
| id | Integer | PK |
| item_id | Integer | FK → itens.id, NOT NULL |
| usuario_id | Integer | FK → usuarios.id, **ON DELETE SET NULL**, nullable (histórico preservado mesmo se o usuário for excluído) |
| quantidade | Integer | default 1 |
| data_retirada | DateTime | default now(UTC) |
| dias_solicitados | Integer | NOT NULL |
| data_devolucao_prevista | DateTime | NOT NULL |
| data_limite_tolerancia | DateTime | NOT NULL |
| data_devolucao_real | DateTime | nullable |
| status | String(20) | default "EM_ANDAMENTO" — **livre, sem enum** |
| emails_enviados | Boolean | default False — controla lembrete de "falta 1 dia" (envio único) |
| ultimo_alerta_atraso | DateTime | nullable — throttle do alerta de atraso (no máx. 1x/dia) |

## Cadeia de migrations (Alembic)

Verificada por leitura direta de `revision`/`down_revision` em todos os arquivos — cadeia linear, sem branches, sem gaps:

```
bcc0d229b7e7  schema inicial                                          (down: None — raiz)
   ↓
034489a950b0  seed setores fixos
   ↓
5dc55278ec99  adicionar data_devolucao_real
   ↓
4de75c5386aa  adicionar email e permitir exclusão de usuário
              preservando histórico
   ↓
5e66d94ccf2e  adicionar quantidade e email tracking a empréstimos
   ↓
7a1c3f9d2b04  adicionar ultimo_alerta_atraso
   ↓
8b7e6a1c2d90  adicionar identificação QR e área aos itens            (head atual)
```

**STATUS: NÃO VERIFICADO** — a cadeia foi validada por leitura estática dos arquivos (`revision`/`down_revision` batem par a par, sem duplicidade nem gap). Não foi executado `alembic upgrade head` nem `alembic downgrade` de fato, porque este ambiente de auditoria não tem PostgreSQL disponível (ver relatório de execução). Recomendo rodar `alembic upgrade head` seguido de `alembic downgrade -1` uma vez em ambiente com Docker antes de confiar 100% na reversibilidade de cada migration.
