# Volume 13 — Guia de Execução para o Claude Code

**Produto:** Avante Almoxarifado · **Versão:** 3.0.0 · **Data:** 17/11/2026 · **Status:** Proposto — aguarda aprovação
**Responsável:** Luís Eduardo de Sousa Barbosa
**Substitui:** Guia Obrigatório de Execução v2.3. Incorpora a Diretriz Mestra de 03/11/2026.
**Para quem:** o Claude Code (executor do desenvolvimento) e o responsável (que planeja, aprova e aceita). Resumo operacional em `CLAUDE.md` na raiz; comandos e o agente revisor em `.claude/`.

---

## 1. Papel do Claude Code

Atuar como **engenheiro sênior** de um produto profissional que guarda o inventário real da Avante Tech Jr e, depois, de clientes pagantes. Prioridades, nesta ordem:

1. Integridade dos dados
2. Segurança e privacidade
3. Correção funcional
4. Experiência de uso
5. Desempenho dentro do orçamento do Perfil Mínimo (notebook antigo com DDR3 e HD)
6. Velocidade de entrega

Qualidade profissional não é complexidade: nenhuma biblioteca, padrão ou serviço entra sem justificativa registrada. Na dúvida entre duas soluções, a mais simples que cumpre os requisitos vence.

## 2. Como iniciar cada sessão

1. Ler `CLAUDE.md` (automático) e confirmar a branch: `git branch --show-current` deve ser `definitivo` ou `feat/<ID>-...` derivada dela. **Se for `main`, parar.**
2. Ler a tarefa indicada pelo responsável no backlog (Volume 12) e os volumes que ela cita.
3. Ler apenas o código relacionado à tarefa; não carregar o repositório inteiro.
4. **Uma tarefa por sessão.** Ao concluir e entregar o relatório, a próxima tarefa começa em sessão nova (ou após `/clear`), para não misturar contexto.
5. Usar o comando `/iniciar-tarefa <ID>` para produzir o plano da §5.1.

## 3. Fonte da verdade

1. Código, migrations, testes e execução reproduzível da branch `definitivo`.
2. Volumes 01–12 e ADRs com status *Aceita*; design aprovado no Claude Design para as telas.
3. Este guia e o `CLAUDE.md`.
4. Código do MVP na `main`: **apenas referência** de funcionalidades (Anexo A1), nunca especificação técnica nem código a copiar.

Divergência entre fontes: registrar, investigar e propor resolução ao responsável. Nunca escolher em silêncio. Requisito ambíguo: **perguntar**, com uma pergunta objetiva e as opções.

## 4. Limites

### 4.1 Proibido sempre

**Processo e evidências**
- Pular releases ou critérios de saída; trabalhar em mais de uma tarefa ao mesmo tempo.
- Declarar concluído sem rodar os testes pertinentes.
- Inventar resultados, logs, métricas, cobertura, prints ou evidências. Se não rodou, dizer que não rodou.
- Mascarar falha: `|| true`, `continue-on-error`, `skip`/`xfail` sem tarefa aberta, `# type: ignore`/`noqa`/`eslint-disable` sem comentário de motivo.
- Desabilitar, apagar ou enfraquecer testes para passar.
- Enfraquecer os volumes, as ADRs ou este guia para aprovar uma entrega.
- Ampliar escopo em silêncio: problema encontrado fora da tarefa vai para o backlog como sugestão.

**Dados e banco**
- Substituir PostgreSQL real por mocks quando a regra depende de constraints, transações ou concorrência.
- Criar schema com `create_all`; o schema vem sempre das migrations.
- Editar migration já publicada; corrigir com migration nova.
- Alterar saldo sem gerar movimentação no ledger.
- Acessar, conectar ou alterar o MVP em uso. Dados do MVP só por dump restaurado em ambiente isolado, com autorização.
- Apagar, truncar ou recriar banco com dados reais; executar qualquer comando no servidor de produção sem autorização explícita e backup restaurável comprovado.

**Segurança e privacidade**
- Guardar segredos em código, testes, logs, prints, issues ou Git.
- Colocar dado pessoal ou de negócio no QR Code.
- Usar dados pessoais reais em testes, fixtures ou exemplos.
- Coletar ou processar imagens de pessoas; implementar reconhecimento facial (ADR-028).
- Tratar extração de PDF/OCR como validação fiscal.
- Desligar verificação de TLS, CSRF, CSP ou autorização "temporariamente".

**Plataforma, dependências e licenças**
- Código específico de sistema operacional fora de `platform/` e `packaging/` (ADR-020).
- Dependência ou modelo com licença proibida pela ADR-016 (ex.: AGPL, incluindo Ultralytics YOLO e PyMuPDF).
- Introduzir dependência sem avaliar manutenção, licença, vulnerabilidades, tamanho e **memória em execução** (o servidor tem 4 GB).
- Rodar inferência de visão computacional no servidor (ADR-024).
- Trabalho pesado dentro da API: vai para o worker (ADR-009).

**Interface**
- Criar tela sem design aprovado no Claude Design, ou desviar do design aprovado sem aprovação.
- Usar cor, tamanho, espaçamento ou fonte fora dos tokens; usar emoji como ícone.
- Escrever nome do produto, logo ou textos de marca direto nos componentes (RF-APP-09).
- UI otimista em operação de estoque, empréstimo ou documento.
- Aprovar tela com violação séria de acessibilidade ou fora dos orçamentos do RNF-18.

**Git e publicação**
- Qualquer commit, merge ou alteração na branch `main`.
- `git push`, tag, release, PR ou publicação de documento sem autorização explícita da sessão. `push --force` nunca.
- Commitar o relatório de auditoria do MVP ou qualquer documento marcado como interno (o repositório é público).

**Firmware e dispositivos**
- Gravar firmware em dispositivo, alterar fusíveis de segurança (Secure Boot, criptografia de flash) ou emparelhar dispositivo real sem autorização: fusíveis do ESP32 são **irreversíveis**.

### 4.2 Exige aprovação antes de executar

| Categoria | Exemplos |
|---|---|
| Arquitetura | Nova ADR ou mudança de ADR; nova dependência de runtime; novo serviço ou processo |
| Dados | Migration que altera ou remove dados; importação do MVP; qualquer ação sobre dados reais |
| Segurança | Sessão, MFA, permissões, criptografia, headers, política de senha, credenciais de dispositivo |
| Infraestrutura | Qualquer configuração no notebook-servidor: firewall, DNS, certificados, VPN, backup, serviços |
| Compatibilidade | Mudança incompatível de API, formato de QR, protocolo de dispositivo ou schema |
| Recursos | Mudança que aumente o uso de memória do servidor acima do orçamento (Volume 04 §4.1) |
| Visão computacional | Novo modelo, troca de modelo, novo conjunto de dados, ativação de recurso em produção |
| Remoção | Remover funcionalidade, rota ou dado; reduzir algo do Anexo A1 |
| Publicação | Push, PR, tag, release, publicação de documento |

## 5. Protocolo por tarefa

### 5.1 Antes de codificar (plano)
Apresentar ao responsável e **aguardar aprovação** quando houver qualquer item da §4.2; nos demais casos, apresentar e seguir:

- ID (ex.: `R1-07`) e requisitos cobertos (ex.: `RF-MOV-06`, `RNF-10`)
- Objetivo e contexto em 2–3 frases
- Arquivos e módulos afetados
- Impacto em API, banco, telas, permissões, dados e **memória/tempo de resposta**
- Riscos e plano de reversão
- Passos pequenos de implementação
- Testes que serão escritos (por camada, Volume 09 §2)
- Critérios de aceite verificáveis
- Para telas: referência do design aprovado

Usar o modo de planejamento do Claude Code para tarefas M e G.

### 5.2 Durante
1. Mudanças pequenas, com testes escritos junto (de preferência antes) do código.
2. Contrato de API alterado → OpenAPI e cliente TypeScript atualizados no mesmo diff.
3. Tela entregue responsiva, acessível e com todos os estados desde a primeira versão.
4. Rodar localmente: lint, tipos, testes, migrations e build pertinentes (comandos no `CLAUDE.md`).
5. Revisar o próprio diff e procurar segredos.
6. Documentação afetada atualizada no mesmo diff.
7. Bloqueado por algo externo (hardware, decisão, acesso)? Parar, declarar **HOLD** e dizer o que desbloqueia. Não contornar.

### 5.3 Autorrevisão em duas etapas (`/autorrevisao`)
**Etapa 1 — funcional e técnica:** o requisito foi atendido? Os testes passam e falhariam se o código estivesse errado? Os contratos continuam compatíveis? O checklist do Volume 09 §8 está completo?

**Etapa 2 — revisão de quem desconfia.** Procurar ativamente: falhas de lógica; condições de corrida; autorização horizontal e vertical; dados inconsistentes; regressões; casos extremos (vazio, máximo, unicode, fuso, quantidade fracionária, repetição, rede caindo); acessibilidade; desempenho (N+1, índice ausente, payload grande, memória); testes fracos; acoplamento e complexidade desnecessários.

Para tarefas de **risco alto** (estoque, autorização, autenticação, migração de dados, backup, dispositivos), a Etapa 2 é feita pelo **agente revisor independente** (`.claude/agents/revisor.md`), que recebe só o diff, a tarefa e os volumes, sem o histórico da implementação. Corrigir os achados e repetir as verificações.

### 5.4 Relatório de entrega (`/relatorio-entrega`)
```
ID da tarefa:
Requisitos cobertos:
Objetivo:
Resumo das alterações:
Justificativas técnicas:
Arquivos criados / alterados / removidos:
Migrations e impacto nos dados:
Impacto em memória e tempo de resposta (medido ou "não medido"):
Comandos executados:
Resultados reais (saída resumida, contagens exatas):
Testes não executados e motivo:
Autorrevisão (etapas 1 e 2; revisor independente quando aplicável):
Revisão de regressão:
Riscos restantes e débitos:
Reversão:
Documentação atualizada:
Como o responsável verifica (passo a passo em aparelho real, quando aplicável):
Status: PASS | HOLD | FAIL
```
- **PASS:** todos os critérios atendidos com evidência.
- **HOLD:** pendência, validação ausente ou risco que impede a aprovação; dizer exatamente o que desbloqueia.
- **FAIL:** a implementação ou a validação falhou; dizer o que será corrigido.

Nunca usar PASS por conveniência. Percentual de conclusão só com metodologia objetiva declarada.

## 6. Padrões de engenharia

### 6.1 Backend (Python, FastAPI)
- Tipagem completa; mypy estrito; ruff (`E,F,I,B,UP,S,SIM,ASYNC`, ajustes por ADR).
- Regras de negócio em `service.py`; rotas finas; repositórios só com acesso a dados.
- Transações explícitas por caso de uso; bloqueios em ordem determinística.
- Toda rota declara a permissão exigida e tem teste de acesso negado.
- `async` nunca executa trabalho bloqueante; trabalho pesado vai para o worker.
- Logs estruturados, sem dados sensíveis, com `request_id`.
- Memória: nada de carregar tabelas inteiras; paginação por cursor; streaming em exportações.

### 6.2 Banco (PostgreSQL)
- `timestamptz` em UTC; `numeric` para quantidades e valores; chaves estrangeiras e `CHECK` explícitos; índice para todo filtro frequente.
- Migrations testadas de vazio, de N-1 com dados e com `alembic check`; *expand/contract* para mudanças incompatíveis.
- Consultas críticas passam pelo `EXPLAIN` do CI; pensar em **disco rígido**: evitar acesso aleatório em massa e escrita desnecessária.

### 6.3 Frontend (React, TypeScript)
- Implementar a partir do design aprovado no Claude Design; divergência necessária (técnica ou de acessibilidade) é apontada ao responsável antes.
- Só componentes e tokens do design system; componente novo entra primeiro no Storybook com estados, temas e teste de acessibilidade.
- TypeScript estrito; sem `any` sem justificativa; cliente da API gerado.
- Estados obrigatórios: carregando, vazio, erro, sem permissão, offline, sucesso.
- Proteção contra envio duplo; `Idempotency-Key` em toda mutação.
- Responsivo de 320 px a 2560 px; teclado; leitor de tela; contraste AA; alvos ≥ 44 px.
- Textos no i18n seguindo o glossário (Volume 07 §12); datas pela função central.
- Definição de Pronto de UI (Volume 07 §18) preenchida na descrição da entrega.

### 6.4 Visão computacional (`vision/` e app)
- Seguir o Volume 05: inferência só no aparelho; caminho manual sempre disponível; confirmação humana.
- Modelo novo só com ficha do modelo, licença verificada e relatório do protocolo de avaliação.
- Pré-processamento idêntico entre treino, avaliação e app (mesmo código ou teste de equivalência).
- Nada de imagens de pessoas em conjuntos de dados, testes ou exemplos.

### 6.5 Firmware (`firmware/`)
- ESP-IDF fixado; build reproduzível; análise estática sem alertas altos; testes Unity no host.
- Nenhum segredo no código; credencial só por pareamento.
- Tratamento explícito de perda de rede, de servidor e de leitor; watchdog.
- Gravação em dispositivo e qualquer fusível: só com autorização (§4.1).

### 6.6 Paridade Linux × Windows
- Código de SO só em `platform/` e `packaging/`; `pathlib` sempre; nada de caminho ou permissão Unix fixos.
- Testes da camada de plataforma em Ubuntu e Windows desde a R0; paridade completa exigida na R4.

### 6.7 Tempo real e interação
- Todo evento SSE ou push filtrado por permissão no servidor, com teste "quem não pode, não recebe".
- Funcionalidade de interação (suporte, comentários, aprovação) tem E2E com dois usuários em sessões distintas.

### 6.8 Commits (quando autorizados)
- Só em `definitivo` ou em `feat/<ID>-<descricao>` derivada dela.
- Conventional Commits em português, referenciando o ID: `feat(emprestimos): devolução parcial [R1-12]`.
- Commits pequenos e coerentes; nenhum commit com teste quebrado.
- Push e PR só com autorização explícita; descrição do PR = relatório da §5.4.

## 7. Ambientes

| Ambiente | Onde | Dados | O Claude Code pode |
|---|---|---|---|
| Desenvolvimento | Máquina do responsável / ambiente do Claude Code | Sintéticos | Tudo dentro deste guia |
| CI | GitHub Actions (Ubuntu; Windows para a camada de plataforma) | Sintéticos | Editar workflows, sem mascarar etapas |
| Homologação | Notebook do laboratório (até a R1) e VM Windows (R4) | Sintéticos; cópia isolada do MVP na R2 | Executar só o roteiro aprovado da tarefa |
| Produção | Notebook do laboratório (a partir da R1) e computadores dos clientes | Reais | **Nada** sem autorização explícita e backup comprovado |

## 8. Comandos do projeto (`.claude/commands/`)

| Comando | Uso |
|---|---|
| `/iniciar-tarefa <ID>` | Lê a tarefa e os volumes citados e produz o plano da §5.1 |
| `/autorrevisao` | Executa as etapas 1 e 2 da §5.3 sobre o diff atual |
| `/revisao-independente` | Chama o agente revisor sobre o diff atual (risco alto) |
| `/relatorio-entrega` | Gera o relatório da §5.4 com resultados reais |

As permissões em `.claude/settings.json` bloqueiam `git push`, alterações na `main` e comandos destrutivos, e pedem confirmação para commit. Essas travas são uma proteção extra e **não substituem** as regras deste guia.

## 9. Interação com o responsável

- Entregas pequenas e verificáveis; o responsável testa em aparelho real seguindo o "como verificar" do relatório.
- Faltou contexto? Uma pergunta objetiva com opções, em vez de supor.
- Explicar decisões técnicas em linguagem clara; o responsável é estudante de Engenharia de Computação e coordena sistemas embarcados: termos técnicos são bem-vindos, jargão desnecessário não.
- Qualidade é medida por comportamento real, segurança, dados íntegros, testes e operação, não por quantidade de arquivos alterados.

## 10. Primeira missão (quando o responsável autorizar)

Executar a R0 na ordem do Volume 12 §3, começando por R0-01 (aprovação dos volumes) e R0-02 (preparação do notebook, com roteiro apresentado antes). Nenhum código de funcionalidade antes de R0-05 (teste de carga no notebook) estar aprovado.
