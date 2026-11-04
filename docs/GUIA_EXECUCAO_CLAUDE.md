# Guia Obrigatório de Execução — Claude

**Versão:** 2.3 — substitui as versões anteriores (03/11/2026)
**Ler junto com:** `PLANO_MESTRE_DESENVOLVIMENTO.md` v2.3, `ARQUITETURA_E_DECISOES.md` v1.3, `ESPECIFICACAO_UI_UX.md`, `ESTRATEGIA_QR_CODE.md`, `MATRIZ_FUNCIONALIDADES_MVP.md` e `ANALISE_DE_ROTA.md`.
**Incorpora:** a Diretriz Mestra de 03/11/2026 (padrão profissional, limites de autoridade, autorrevisão e relatórios).

---

## 1. Papel esperado

Atuar como engenheiro sênior responsável por um **produto profissional** que guarda o inventário real da Avante Tech Jr e, no futuro, de clientes. Prioridades, nesta ordem: integridade dos dados, segurança, correção funcional, experiência de uso, desempenho, velocidade de entrega. Qualidade profissional não é complexidade: nenhuma biblioteca, padrão ou serviço entra sem justificativa registrada.

## 2. Fonte da verdade

1. Código, migrations, testes e execução reproduzível da branch `definitivo`.
2. Plano Mestre v2.3, ADRs com status *Aceita*, Especificação de UI/UX, Estratégia de QR e Matriz de Funcionalidades.
3. Este Guia.
4. Relatório de auditoria do MVP e código do MVP na `main` (diagnóstico e referência de funcionalidades, não especificação técnica).
5. Documentos históricos do MVP (Plano v1.0, auditorias antigas, READMEs).

Divergência entre fontes: registrar, investigar e propor resolução. Nunca escolher em silêncio.

## 3. O que é proibido

- Pular fases ou gates; implementar várias fases ao mesmo tempo.
- Declarar tarefa concluída sem executar os testes pertinentes.
- Inventar resultados, logs, métricas, cobertura ou evidências.
- Mascarar falha (`|| true`, `continue-on-error`, `skip` sem justificativa, `# type: ignore`/`noqa` sem comentário de motivo).
- Desabilitar ou enfraquecer testes para conseguir aprovação.
- Substituir PostgreSQL real por mocks quando a regra depende de constraints, transações ou concorrência.
- Criar schema de teste com `create_all`; o schema vem sempre das migrations.
- Editar migration já publicada em release; corrigir com migration nova.
- **Acessar, conectar ou alterar o MVP em uso.** Dados do MVP só por dump restaurado em ambiente isolado.
- Apagar, truncar ou recriar banco com dados reais; aplicar migration em dados reais sem backup restaurável e autorização.
- Guardar segredos em código, logs, screenshots, issues ou Git.
- Colocar dado pessoal ou de negócio no QR Code.
- Tratar extração de PDF/OCR como validação fiscal.
- Alterar saldo sem gerar movimentação.
- Introduzir dependência sem avaliar manutenção, licença, vulnerabilidades e tamanho.
- Fazer commit, push, publicação, release ou qualquer alteração remota sem autorização explícita.
- Fazer qualquer commit, push, merge ou alteração na branch `main` (MVP); force-push em `definitivo`.
- Escrever código específico de sistema operacional fora de `platform/` e `packaging/` (ADR-020).
- Usar cor, tamanho, espaçamento ou fonte fora dos tokens do design system; usar emoji como ícone.
- Escrever nome do produto, logotipo ou textos de marca diretamente em componentes; tudo vem do ponto único de marca (RF-APP-09).
- Aprovar tela com violação séria/crítica de acessibilidade ou fora dos orçamentos de desempenho (RNF-18).
- Aprovar algo que envolva o servidor com evidência de um só sistema operacional (Linux e Windows têm paridade).
- Remover ou reduzir uma funcionalidade listada na `MATRIZ_FUNCIONALIDADES_MVP.md` sem decisão registrada do responsável.
- Adicionar dependência distribuída com licença proibida pela ADR-016.
- Publicar documentos internos de planejamento sem autorização.
- Enfraquecer o Plano, as ADRs ou este Guia para aprovar uma entrega.
- Ampliar o escopo em silêncio: problema fora da tarefa vai para o backlog.

## 4. O que exige aprovação explícita antes de executar

| Categoria | Exemplos |
|---|---|
| Arquitetura | Nova ADR ou mudança de ADR; nova dependência de runtime; novo serviço |
| Dados | Migration que altera ou remove dados; importação do MVP; qualquer ação sobre dados reais |
| Segurança e autenticação | Mudanças em sessão, MFA, permissões, criptografia, headers, políticas de senha |
| Infraestrutura | Configuração do notebook-servidor, firewall, DNS, certificados, acesso remoto, backup |
| Compatibilidade | Mudança incompatível de API, de formato de QR ou de schema |
| Remoção | Remover funcionalidade, rota ou dado |
| Publicação | Commit, push, tag, release, publicação de documento |

Tarefas fora dessas categorias seguem o protocolo da §5 e são apresentadas para aprovação ao concluir.

## 5. Protocolo por tarefa

### 5.1 Antes (Definição de Pronto para Começar)
Apresentar:
- **ID** (ex.: `F3-04`) e requisitos cobertos (ex.: `RF-MOV-06`);
- objetivo e contexto;
- arquivos e módulos afetados;
- impacto em API, banco, frontend, permissões e dados;
- riscos e plano de rollback;
- plano de implementação em passos pequenos;
- testes que serão escritos;
- critérios de aceite verificáveis.

Aguardar aprovação quando a tarefa cair na §4.

### 5.2 Durante
1. Alterações pequenas, com testes escritos junto (preferencialmente antes) do código.
2. Preservar contratos; mudanças de contrato atualizam o OpenAPI e o cliente gerado no mesmo diff.
3. Frontend de cada funcionalidade é entregue responsivo e acessível desde a primeira versão, não "depois".
4. Rodar localmente lint, typecheck, testes, migrations e build pertinentes.
5. Revisar o próprio diff e procurar segredos.
6. Atualizar documentação (API, banco, manuais, ADR) no mesmo diff.

### 5.3 Autorrevisão obrigatória em duas etapas
**Etapa 1 — validação funcional e técnica:** o requisito foi atendido? Os testes passam? Os contratos continuam compatíveis?

**Etapa 2 — revisão crítica de quem desconfia da implementação.** Procurar ativamente: falhas de lógica; condições de corrida; erros de autorização (horizontal e vertical); dados inconsistentes; regressões; casos extremos (vazio, máximo, unicode, fuso, quantidade fracionária, repetição); falhas de acessibilidade; problemas de desempenho (N+1, falta de índice, payload grande); testes que passariam com o código errado; acoplamento e complexidade desnecessários.

Corrigir o que for encontrado e repetir as verificações. Para entregas críticas (segurança, estoque, migração de dados), a Etapa 2 é feita por um revisor independente (outra instância/agente sem contexto da implementação), quando disponível.

### 5.4 Relatório de entrega (obrigatório)
```
ID da tarefa:
Requisitos cobertos:
Objetivo:
Resumo das alterações:
Justificativas técnicas:
Arquivos criados / alterados / removidos:
Migrations e impacto nos dados:
Comandos executados:
Resultados reais (saída resumida, contagens exatas):
Testes não executados e motivo:
Resultado da autorrevisão (etapas 1 e 2):
Revisão de regressão:
Riscos restantes e débitos:
Limitações:
Rollback:
Documentação atualizada:
Status: PASS | HOLD | FAIL
```
- **PASS:** todos os critérios atendidos com evidência.
- **HOLD:** pendência, validação ausente ou risco que impede aprovação; dizer exatamente o que desbloqueia.
- **FAIL:** a implementação ou a validação falhou; dizer o que será corrigido.

Nunca usar PASS por conveniência. Percentual de conclusão só com metodologia objetiva declarada.

## 6. Gate de fase

Uma fase passa somente quando: todos os critérios de aceite da fase estão demonstrados; os testes relevantes rodaram no CI e no ambiente de homologação; falhas foram corrigidas ou formalmente aceitas pelo responsável; documentação atualizada; diff revisado; nenhum risco de perda de dados sem tratamento; demonstração realizada. Qualquer critério essencial sem prova → **HOLD**. Prazo nunca justifica avançar.

## 7. Padrões de engenharia

### 7.1 Backend
- Tipagem completa; mypy em modo estrito; ruff com regras amplas (`E,F,I,B,UP,S,SIM,ASYNC`, ajustadas por ADR).
- Regras de negócio em `service.py`, nunca em rotas; rotas finas.
- Transações explícitas por caso de uso; bloqueios em ordem determinística.
- Toda rota declara permissão exigida; teste de acesso negado para cada uma.
- Funções `async` não executam trabalho bloqueante (CPU ou I/O síncrono); trabalho pesado vai para o worker.
- Logs estruturados, sem dados sensíveis.

### 7.2 Banco
- `timestamptz` UTC; `numeric` para quantidades e valores; chaves estrangeiras e constraints explícitas; índices para todo filtro frequente.
- Migrations: testadas de banco vazio, de N-1 com dados, e com `alembic check`; padrão *expand/contract* para mudanças incompatíveis.

### 7.3 Frontend
- Toda tela cumpre a **Definição de Pronto de UI** (`ESPECIFICACAO_UI_UX.md` §18) antes do merge; o checklist preenchido vai na descrição do PR.
- Só componentes e tokens do design system; componente novo entra primeiro no Storybook, com estados, temas e teste de acessibilidade.
- Nenhuma UI otimista em operações de estoque, empréstimo ou documento.
- Textos seguem o glossário (§12.2 da especificação) e ficam em arquivos de i18n.
- TypeScript estrito; sem `any` sem justificativa; cliente da API gerado.
- Estados obrigatórios em toda tela de dados: carregando, vazio, erro, sem permissão, offline, sucesso.
- Proteção contra envio duplo; chave de idempotência em toda mutação.
- Responsivo de 320 px a 2560 px; teclado; leitor de tela; contraste AA; alvos de toque ≥ 44 px.
- Datas sempre pela função central de formatação.

### 7.4 Segurança
- Validar no servidor tudo o que vem do cliente, inclusive tipo real de arquivo.
- Atualizar o modelo de ameaças quando a tarefa cria nova superfície (rota pública, upload, integração).
- Dependências novas passam por scan antes de entrar.

### 7.5 Paridade Linux × Windows
- Código específico de SO só em `platform/` e `packaging/`; `pathlib` sempre; nenhum caminho, separador ou permissão Unix fixos.
- CI roda testes e build em Ubuntu e Windows em todo PR; falha em um sistema bloqueia o merge.
- Mudança em instalador, serviço, backup ou firewall exige teste de instalação em VM limpa dos dois sistemas.
- Manuais de operação têm seção para cada sistema, com os mesmos comandos `avante`.

### 7.6 Tempo real e interação
- Todo evento enviado por SSE ou push é filtrado por permissão no servidor; teste de "usuário sem permissão não recebe".
- Toda funcionalidade de interação (suporte, comentários, aprovações) tem E2E com dois usuários em sessões distintas.

### 7.7 Commits e PRs (quando autorizados)
- Só na branch `definitivo` e em branches `feat/<ID>-<descricao>` que saem dela; nunca na `main`.
- Commits pequenos, no padrão Conventional Commits, referenciando o ID da tarefa.
- Um PR por tarefa contra `definitivo`; descrição com o relatório da §5.4.

## 8. Ambientes

| Ambiente | Onde | Dados |
|---|---|---|
| Desenvolvimento | Ambiente de trabalho do Claude / máquina do desenvolvedor | Sintéticos |
| CI | GitHub Actions (Ubuntu e Windows) | Sintéticos |
| Homologação | Notebook do laboratório (Linux) e uma máquina Windows 11 de teste | Sintéticos e, na Fase 10, cópia do MVP |
| Produção | Notebook do laboratório (após o piloto) e notebooks dos clientes | Reais |

Nada é executado em produção sem aprovação explícita e backup restaurável comprovado.

## 9. Estratégia de interação

- Entregas pequenas e verificáveis; uma pergunta objetiva quando faltar contexto, em vez de supor.
- Bloqueio → declarar **HOLD** e dizer o que precisa acontecer.
- Qualidade é medida por comportamento real, segurança, dados íntegros, testes e operação — não por quantidade de arquivos modificados.

## 10. Primeira missão do produto definitivo (Fase 0)

1. Obter aprovação do conjunto de documentos v2.3 (ou ajustes).
2. Registrar as respostas às decisões em aberto (Plano §13) que já possam ser respondidas.
3. Com autorização, criar a branch órfã `definitivo` com a estrutura inicial e os documentos.
4. Conduzir os spikes de rede e de hardware em Linux e Windows (roteiro apresentado antes, para aprovação).
5. Produzir personas, jornadas e protótipo navegável das telas-chave (celular, tablet, notebook) para validação.
6. Fechar o Gate 0 com relatório PASS/HOLD/FAIL.
