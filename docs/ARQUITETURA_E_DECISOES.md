# Arquitetura e Registro de Decisões (ADRs) — Avante Almoxarifado

**Versão:** 1.3 · **Data:** 03/11/2026
**Relação:** detalha o §6 do `PLANO_MESTRE_DESENVOLVIMENTO.md` v2.3. A camada visual e de interação está em `ESPECIFICACAO_UI_UX.md`.
**Status das ADRs:** *Proposta* até aprovação no Gate 0. Mudar uma ADR *Aceita* exige nova ADR que a substitua.
**Mudanças da 1.1:** servidor Linux **e** Windows (ADR-002, nova ADR-020); backup trocado para WAL + restic (ADR-012); distribuição `.deb` + `.msi` (ADR-013); formato de QR definido (ADR-011); novas ADR-016 (licenças), ADR-017 (aplicativo/PWA), ADR-018 (tempo real), ADR-019 (branch).
**Mudanças da 1.2:** nova ADR-021 (design system); ADR-016 passa a permitir fontes OFL-1.1.
**Mudanças da 1.3:** versões atualizadas — Ubuntu 26.04 LTS (referência) e 24.04 LTS, Debian 13, Windows 11 em versão suportada (25H2+), PostgreSQL 18, Python 3.14; ADR-014 adiada para a Fase 13; nova ADR-022 (política de versões de plataforma).

---

## 1. Contexto e restrições

| Restrição | Origem |
|---|---|
| Um servidor por instalação: notebook com **Linux ou Windows** | Responsável, 03/11/2026 |
| 1.0 para uso interno da Avante Tech Jr; arquitetura preparada para venda futura com instalação local no cliente | Idem |
| Usado como aplicativo instalável, com interação entre usuários | Idem |
| Acesso por notebooks, celulares e tablets, na rede local e pela internet | Idem |
| Servidor com internet sempre disponível | Idem |
| MVP continua operando na `main`; produto novo na branch `definitivo` do mesmo repositório | Idem |
| Câmera do navegador e instalação PWA exigem HTTPS com certificado confiável | Plataforma web |
| Notebook como servidor: disco único, furto, bateria, tampa, suspensão, atualizações automáticas do SO | Hardware/SO |

## 2. Visão geral

```
                     Internet                                     Rede local do cliente
  ┌──────────────┐                                         ┌────────────────────────────────┐
  │ Aparelho fora│──(VPN WireGuard ou túnel, ADR-007)───┐  │ Notebooks · Celulares · Tablets│
  │ da rede      │                                      │  │ (PWA instalada ou navegador)   │
  └──────────────┘                                      │  └───────────────┬────────────────┘
                                                        ▼          HTTPS (certificado válido)
┌──────────── Notebook-servidor: Ubuntu 26.04 ou 24.04 / Debian 13 / Windows 11 (disco cripto + TPM) ────┐
│  Firewall: nega tudo; 443 só na rede local/VPN                                                           │
│  ┌─────────┐  /            ┌──────────────────────┐   SQL   ┌──────────────┐   WAL ──► restic ───────────┼─► repositório S3
│  │  Caddy  │──────────────►│ SPA/PWA estática     │         │ PostgreSQL 18│                             │   criptografado
│  │  (TLS)  │──/api/v1─────►│ API FastAPI (+ SSE)  │◄───────►│ (sessão UTC) │                             │
│  └─────────┘               └──────────────────────┘         └──────▲───────┘                             │
│                            ┌──────────────────────┐ fila SKIP LOCKED│ LISTEN/NOTIFY                         │
│                            │ Worker de jobs       │─────────────────┘ e-mail · Web Push · OCR · relatórios │
│                            └──────────────────────┘                  · reconciliação · verificações        │
│  CLI `avante` (status, doctor, backup, restore, update, rollback) · logs JSON · alertas                   │
│  Gerenciador de serviços: systemd (Linux) | Serviços do Windows via WinSW (Windows)                       │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 3. Stack

| Camada | Escolha | Justificativa | Alternativa considerada |
|---|---|---|---|
| SO do servidor | Ubuntu 26.04 LTS (referência, até 2031) e 24.04 LTS; Debian 13; Windows 11 Pro em versão suportada (25H2+) | Pedido do responsável; LTS com suporte longo; Windows 10 fora de suporte | macOS (fora de escopo) |
| Banco | PostgreSQL 18 (fim de suporte em nov/2030) | Transações, constraints, `SKIP LOCKED`, `LISTEN/NOTIFY`, `timestamptz`; nativo nos dois sistemas | SQLite (fraco para concorrência e fila) |
| Backend | Python 3.14 (fim de suporte em out/2030; 3.13 como alternativa se alguma dependência não tiver suporte), FastAPI, SQLAlchemy 2 tipado, Alembic, Pydantic v2, psycopg 3 | Continuidade do MVP; ecossistema para XML/PDF/imagem; roda igual em Windows e Linux | Go (empacotamento mais simples, reescrita total — ver `ANALISE_DE_ROTA.md` D-04) |
| Runtime Python | **Embutido no pacote** (python-build-standalone) com dependências travadas | Independe do Python do sistema; mesmo runtime nos dois sistemas | Python do sistema (versões divergentes) |
| Servidor ASGI | Uvicorn com loop asyncio padrão (sem uvloop, indisponível no Windows), vários workers | Comportamento idêntico nos dois sistemas | Gunicorn (não roda no Windows) |
| Senhas | Argon2id (argon2-cffi), mínimo OWASP (m=19 MiB, t=2, p=1), recalibrado no hardware | Recomendação atual | bcrypt |
| Frontend | React 19 + TypeScript estrito + Vite, React Router, TanStack Query, React Hook Form + Zod | App 100% cliente, build estático, sem servidor Node em produção | Next.js com exportação estática |
| UI | Design system próprio: tokens (Style Dictionary) + Tailwind + primitivas Radix UI + Lucide + Storybook (ADR-021) | Acessibilidade de componentes complexos; consistência entre aparelhos | Biblioteca visual pronta |
| PWA | vite-plugin-pwa (Workbox) | Manifest, service worker, atualização controlada, cache para leitura offline | SW manual |
| Leitura de códigos | `BarcodeDetector` + zxing-wasm | Decodificação no aparelho; QR, EAN, Code 128 | Decodificar no servidor |
| Tempo real | SSE + `LISTEN/NOTIFY`; Web Push (VAPID) pelo worker | ADR-018 | WebSocket |
| Proxy/TLS | Caddy (binário único para Linux e Windows) com módulo DNS-01 | HTTPS automático sem porta aberta | Nginx + certbot (pior no Windows) |
| Fila/jobs | Fila no PostgreSQL com `FOR UPDATE SKIP LOCKED` (Procrastinate ou implementação mínima, decidido na Fase 1) | Sem Redis; transacional com o outbox | Redis + Celery (Celery sem suporte oficial no Windows) |
| Backup | `pg_basebackup` + arquivamento contínuo de WAL + restic | ADR-012; multiplataforma | pgBackRest (não roda no Windows) |
| PDF / OCR | pypdfium2 (Apache-2.0/BSD) + pdfminer.six (MIT) + Tesseract (Apache-2.0) | Licenças compatíveis com venda (ADR-016) | PyMuPDF (AGPL-3.0) |
| Testes | pytest, Hypothesis, Vitest, Testing Library, Playwright, axe-core, k6 | Plano §8 | — |
| Qualidade/segurança | ruff, mypy estrito, ESLint (flat config), Prettier, Bandit/Semgrep, pip-audit, OSV-Scanner, gitleaks, CycloneDX, verificação de licenças | Gates automáticos | — |

## 4. Estrutura da branch `definitivo`

```
avante-almoxarifado (branch definitivo)
├── backend/
│   ├── src/avante/
│   │   ├── core/            # config, db, segurança, erros, logging, request_id, idempotência, eventos
│   │   ├── platform/        # ÚNICO lugar com código específico de SO: caminhos, permissões, serviços
│   │   ├── modules/
│   │   │   ├── identity/  organization/  catalog/  inventory/  loans/  documents/
│   │   │   ├── labels/    support/       collaboration/  notifications/  reports/
│   │   │   └── audit/     admin/
│   │   ├── realtime/        # SSE e distribuição de eventos
│   │   ├── worker/
│   │   └── cli/             # comando `avante`
│   ├── migrations/
│   └── tests/{unit,integration,concurrency,migrations,platform}/
├── frontend/
│   ├── src/{app,features/<módulo>,components/ui,lib/{api(gerado),i18n,dates,scanner,realtime}}/
│   └── tests/{unit,e2e}/
├── packaging/
│   ├── linux/               # .deb, unidades systemd, regras ufw, logind
│   ├── windows/             # .msi (WiX), WinSW, regras de firewall, powercfg
│   └── common/              # Caddyfile, configuração do PostgreSQL, scripts de backup
├── ops/                     # runbooks, monitoramento, roteiros de recuperação
├── docs/
└── .github/workflows/       # disparam só para a branch definitivo e suas PRs
```

Cada módulo tem `router.py`, `schemas.py`, `service.py`, `repository.py` e `models.py`. Módulos conversam por serviços, nunca acessando tabelas uns dos outros diretamente.

---

## 5. ADRs

### ADR-001 — Produto novo; MVP congelado
**Status:** Proposta
**Decisão:** construir o produto do zero na branch `definitivo` (ADR-019), reaproveitando ideias e trechos validados do MVP (envelope de erro com request_id, regras de devolução, heurísticas de leitura, telas aprovadas), sempre com testes novos. Todas as funções do MVP são preservadas e melhoradas (`MATRIZ_FUNCIONALIDADES_MVP.md`). O MVP não é modificado; seus dados entram só por importador (Fase 10).

### ADR-002 — Servidor nativo em Linux e Windows
**Status:** Proposta (substitui a ADR-002 da v1.0, que era só Linux)
**Decisão:** mesmos serviços nos dois sistemas, nativos, sem Docker em produção.

| Aspecto | Linux (Ubuntu 26.04 e 24.04 / Debian 13) | Windows 11 |
|---|---|---|
| Gerenciador de serviços | systemd com sandbox (`NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome`, `PrivateTmp`, `ReadWritePaths` mínimos, `MemoryMax`) | Serviços do Windows via WinSW (MIT), conta virtual de serviço dedicada, início automático atrasado, reinício em falha |
| Usuário de serviço | `avante`, sem shell | `NT SERVICE\Avante*`, sem login interativo |
| Programas | `/opt/avante` | `%ProgramFiles%\Avante` |
| Configuração e segredos | `/etc/avante` (`root:avante`, 0640) | `%ProgramData%\Avante\config` com ACL restrita à conta de serviço e Administradores |
| Dados e arquivos | `/var/lib/avante` | `%ProgramData%\Avante\data` (ACL restrita) |
| Logs | journald (JSON) | Arquivos JSON rotacionados em `%ProgramData%\Avante\logs` + Log de Eventos para erros críticos |
| PostgreSQL | Pacote PGDG | Binários oficiais embutidos, registrados com `pg_ctl register` |
| Firewall | ufw/nftables: nega tudo, 443 só LAN/VPN | Windows Defender Firewall: regra só no perfil Privado e na interface da VPN |
| Energia/tampa | `logind.conf` (ignorar tampa), máscara de `sleep.target`, desligamento ordenado com bateria crítica (UPower) | `powercfg`: nunca suspender na tomada, tampa sem ação, desligamento ordenado com bateria crítica |
| Atualizações do SO | unattended-upgrades com janela de reinício | Windows Update com horário ativo e reinício fora do expediente |
| Criptografia de disco | LUKS2 + TPM2 (ADR-012) | BitLocker + TPM (Home: "Criptografia do dispositivo", se o hardware suportar; senão, aviso no `avante doctor`) |

### ADR-003 — Docker apenas como ferramenta de CI no Linux
**Status:** Proposta
**Decisão:** PostgreSQL de testes como *service container* nos runners Linux; nos runners Windows, PostgreSQL instalado no próprio runner. Nenhum artefato de produção depende de Docker.

### ADR-004 — SPA React + Vite no mesmo domínio da API
**Status:** Proposta
**Decisão:** SPA estática servida pelo Caddy; API em `/api/v1` no mesmo domínio; sem CORS em produção; cookie `SameSite=Strict`. Reabrir só se surgir necessidade real de SSR.

### ADR-005 — Sessões no servidor, MFA e passkeys
**Status:** Proposta
**Decisão:** token de sessão aleatório de 256 bits guardado só como hash e vinculado ao ID interno; cookie `__Host-avante_session` (`Secure`, `HttpOnly`, `SameSite=Strict`); inatividade e duração absoluta configuráveis; rotação no login e na elevação; revogação imediata em troca de senha, desativação, mudança de papel, logout e "sair de todos"; MFA TOTP obrigatório para papéis privilegiados; reautenticação (step-up) para ações sensíveis; passkeys (Should); limites por conta e por IP guardados no PostgreSQL.

### ADR-006 — Ledger de movimentações como fonte de verdade
**Status:** Proposta
**Decisão:** `movimentacoes` append-only (papel da aplicação sem UPDATE/DELETE); saldos atualizados na mesma transação com `CHECK (quantidade >= 0)` e bloqueio em ordem determinística; quantidades `numeric(18,4)` com unidade de medida; máquina de estados das unidades no serviço e no banco; reconciliação diária; `Idempotency-Key` em toda mutação; concorrência otimista (`version`, ETag/If-Match) em cadastros.

### ADR-007 — Rede, HTTPS válido e acesso remoto sem portas abertas
**Status:** Proposta — decisão final no Gate 0 (DA-01)
**Comum:** nome por cliente (`<cliente>.<dominio-do-produto>`); certificado Let's Encrypt por DNS-01 (sem porta aberta); igual em Linux e Windows.

| Opção | Rede local | Fora da rede | Prós | Contras |
|---|---|---|---|---|
| **A. VPN WireGuard (Tailscale ou Headscale)** | Direto pelo IP local | App de VPN no aparelho | Ponta a ponta; nada exposto; ACL por aparelho | App de VPN em cada aparelho remoto |
| **B. Túnel de saída (ex.: Cloudflare Tunnel) com camada de acesso** | Direto ou pelo túnel | Só navegador | Sem app extra; proteção de borda | TLS termina no provedor; avaliação LGPD |
| C. Porta 443 aberta no roteador | Direto | Direto | Simples | Expõe o notebook; CGNAT; **não recomendado** |

**Recomendação provisória:** A como padrão, B como opção. O spike confirma resolução de nome na LAN (proteção contra *DNS rebinding* de roteadores), câmera, push e procedimento de instalação nos dois sistemas.

### ADR-008 — Arquivos fora do banco
**Status:** Proposta
**Decisão:** fotos, anexos e documentos no diretório de dados da plataforma (ADR-002), com nome por hash; metadados no banco (tipo real detectado, tamanho, dono, hash). Limites de bytes e pixels antes de decodificar; reencodificação sem metadados (EXIF removido); limites por arquivo **e por requisição**; entrega com `Content-Type` correto e `nosniff`. Arquivos entram no backup.

### ADR-009 — Worker separado, outbox e jobs
**Status:** Proposta
**Decisão:** serviço `avante-worker` independente; outbox na mesma transação do evento; e-mails, Web Push, OCR, relatórios grandes, etiquetas em lote, reconciliação e verificações (certificado, backup, disco) rodam só no worker, com timeout e limite de memória; agendamentos com trava contra execução duplicada.

### ADR-010 — Contrato de API
**Status:** Proposta
**Decisão:** `/api/v1`; OpenAPI como contrato; cliente TypeScript gerado no CI; envelope de erro do MVP com códigos de domínio estáveis (`STOCK_INSUFFICIENT`, `QR_UNKNOWN`, `QR_REVOKED`, `QR_FOREIGN_ORG`...); paginação por cursor; datas ISO 8601 com `Z`.

### ADR-011 — Formato do QR Code
**Status:** Proposta (alternativa da v1.0 resolvida)
**Decisão:** conteúdo `https://<endereço-da-organização>/q/<CÓDIGO>`, em que `<CÓDIGO>` = letra do tipo (`U` unidade, `L` local, `I` item a granel, `K` lote, `T` kit, `C` conexão) + 16 caracteres Base32 Crockford (80 bits aleatórios) + 1 verificador. A URL permite que a câmera nativa do celular abra o app direto; o leitor do app ignora o domínio e usa só o código, então as etiquetas sobrevivem a mudança de endereço. Nenhum dado de negócio ou pessoal no QR. Correção de erro nível Q. Detalhes em `ESTRATEGIA_QR_CODE.md`.

### ADR-012 — Backup, recuperação e criptografia
**Status:** Proposta (substitui pgBackRest por WAL + restic)
**Decisão:**
- Disco criptografado: LUKS2 + TPM2 (Linux) ou BitLocker + TPM (Windows), com desbloqueio automático para o servidor voltar sozinho após queda de energia.
- `pg_basebackup` semanal + arquivamento contínuo de WAL (`archive_command` → ferramenta `avante` que copia com verificação de integridade).
- **restic** envia backups base, WAL e diretório de arquivos para repositório local (outro disco/pendrive, opcional) e repositório S3 compatível externo, com criptografia e deduplicação. RPO ≤ 15 min (`archive_timeout` ≤ 5 min + envio a cada 5 min).
- Retenção configurável (ex.: 7 diários, 4 semanais, 12 mensais); verificação `restic check` semanal.
- **Teste de restauração automático mensal** em banco temporário, com alerta se falhar.
- Restauração cruzada suportada: backup feito em Linux restaura em Windows e vice-versa (mesma versão major do PostgreSQL), testada no Gate 9.
- A senha do repositório fica com o cliente (cópia impressa/cofre); sem ela, o backup não se recupera.

### ADR-013 — Distribuição, atualização e rollback
**Status:** Proposta
**Decisão:**
- Linux: pacote `.deb` (amd64) com runtime Python embutido, em repositório apt próprio **assinado**.
- Windows: instalador `.msi` (WiX Toolset) **assinado com Authenticode**, instalando todos os serviços e registrando o PostgreSQL.
- Mesmo comando nos dois: `avante update` verifica assinatura → faz backup → para serviços → instala → migra → health check → em falha, volta para a versão anterior.
- Migrations *expand/contract*: a versão N-1 funciona sobre o schema N, permitindo rollback sem restaurar o banco na maioria dos casos.
- Canais `stable` e `beta`; o app avisa os usuários quando o servidor é atualizado (RF-APP-02).

### ADR-014 — Licenciamento do produto
**Status:** Proposta — **implementação adiada para a Fase 13** (pacote comercial); modelo comercial em DA-03. A 1.0 interna da Avante Tech Jr não tem verificação de licença.
**Decisão:** licença JSON assinada com Ed25519, verificada offline; ao expirar, carência e depois modo somente leitura — nunca bloquear o acesso aos dados do próprio cliente nem apagar nada. Sem telemetria obrigatória; diagnóstico só com consentimento.

### ADR-015 — Datas e fuso horário
**Status:** Proposta
**Decisão:** colunas `timestamptz`; sessão do banco fixada em UTC pela aplicação; código só com datetimes com fuso; API emite `Z`; frontend converte para o fuso da organização com uma função única testada; testes de integração com o PostgreSQL configurado em fuso ≠ UTC, nos dois sistemas.

### ADR-016 — Política de licenças de terceiros
**Status:** Proposta
**Contexto:** o produto poderá ser vendido como software fechado, e a escolha de dependências precisa permitir isso desde já (trocar uma biblioteca depois custa caro). O MVP usava PyMuPDF (AGPL-3.0), que obrigaria a abrir o código ou comprar licença comercial.
**Decisão:**
- Permitidas sem análise: MIT, BSD, Apache-2.0, ISC, PostgreSQL, Zlib, PSF; **OFL-1.1 para fontes** (Inter, JetBrains Mono), que podem ser embutidas no produto desde que não sejam vendidas separadamente.
- Permitidas com análise registrada: MPL-2.0, LGPL (só com ligação dinâmica e substituível), EPL. Ferramentas usadas só no desenvolvimento/CI e não distribuídas (ex.: axe-core, MPL-2.0) não entram no produto.
- **Proibidas** em componentes distribuídos sem decisão do responsável: GPL, AGPL, SSPL, licenças "não comerciais".
- Verificação automática no CI (Python e npm) e inventário de licenças (com avisos de atribuição) publicado junto com cada release.
- Substituições já decididas: PyMuPDF → pypdfium2 + pdfminer.six.

### ADR-017 — Aplicativo instalável (PWA) e conexão à organização
**Status:** Proposta
**Decisão:**
- O app é uma PWA servida pelo servidor de cada cliente; "baixar o app" = instalá-lo a partir do endereço da organização (Android, iPhone/iPad pelo Safari, Windows/Linux/macOS pelo Chrome/Edge). Uma página "Instalar" mostra o passo a passo de cada plataforma.
- Entrada: convite por e-mail ou **QR de conexão** (RF-QR-14).
- Atualização controlada pelo service worker: nova versão baixada em segundo plano, aviso ao usuário, recarga sem perder formulário em edição.
- Leitura offline do catálogo, de "meus empréstimos" e das fichas visitadas; ações exigem conexão (sem escrita offline na 1.0).
- Pós-1.0 (RF-APP-08): casca Capacitor publicada nas lojas, com tela "Conectar à organização" que lê o QR de conexão; o código do app é o mesmo.

### ADR-018 — Interação em tempo real
**Status:** Proposta
**Decisão:**
- **SSE** em `/api/v1/events` por sessão autenticada; cada evento é filtrado por permissão **no servidor** antes do envio; reconexão automática com `Last-Event-ID`.
- Distribuição entre processos da API por `LISTEN/NOTIFY` do PostgreSQL (sem Redis); o payload do NOTIFY leva só identificadores, e os dados são lidos com as permissões do usuário.
- **Web Push** (VAPID) enviado pelo worker para notificações com o app fechado; conteúdo mínimo e criptografado.
- Consulta periódica como reserva se o SSE falhar.
- Casos: mensagens de suporte, comentários em empréstimos/solicitações, aprovações, devoluções, alertas, mudanças de saldo exibidas.
**Alternativa descartada:** WebSocket (as ações já vão por HTTP; SSE é mais simples de proxyar e depurar).

### ADR-019 — Branch `definitivo` no repositório do MVP
**Status:** Proposta
**Decisão:**
- Branch **órfã** `definitivo` (sem o histórico e os arquivos do MVP). A `main` continua sendo o MVP.
- Proteção: entra só por PR com CI verde e revisão; sem force-push.
- Trabalho em branches curtas `feat/<ID>-<descricao>` a partir de `definitivo`.
- Workflows disparam só para `definitivo` e PRs contra ela; Dependabot com `target-branch: definitivo`.
- Tags `app-vX.Y.Z`, sem colidir com o MVP.
- Nenhum commit/push sem autorização explícita do responsável (Guia §4).

### ADR-021 — Design system com tokens como fonte da verdade
**Status:** Proposta
**Decisão:**
- Tokens de design (cores, tipografia, espaço, raios, elevação, movimento) em JSON no repositório, em três camadas (primitivos → semânticos → componente), convertidos por Style Dictionary para variáveis CSS e configuração do Tailwind.
- Temas claro e escuro e marca do cliente são conjuntos de tokens; a cor de marca do cliente passa por verificação automática de contraste antes de ser aplicada.
- Componentes sobre primitivas Radix UI, documentados no Storybook com todos os estados; ícones só Lucide.
- No CI: verificação de contraste de todas as combinações de tokens (WCAG 2.2 AA), proibição de cores/tamanhos fora dos tokens, axe em componentes e telas, testes visuais por captura e Lighthouse CI com os orçamentos do RNF-18.
**Consequência:** a identidade (inclusive white-label) muda sem tocar em componentes, e a acessibilidade não regride em silêncio.

### ADR-022 — Política de versões de plataforma
**Status:** Proposta
**Decisão:**
- Cada release fixa versões exatas de PostgreSQL (major), Python, Caddy e bibliotecas, testadas juntas no CI.
- Só entram versões com suporte oficial vigente por pelo menos 3 anos a partir da release (hoje: PostgreSQL 18, Python 3.14, Ubuntu 26.04/24.04, Debian 13, Windows 11 25H2+).
- No Gate 0, reavaliar PostgreSQL 19 (lançamento anunciado para outubro de 2026): adotar só depois da segunda versão de correção, se trouxer benefício real.
- Atualizações de versão major do PostgreSQL são feitas pelo `avante update` com `pg_upgrade`, backup prévio e rollback, testadas nos dois sistemas.
- O `avante doctor` e a página de saúde avisam quando o SO, o PostgreSQL ou o Python saem do suporte.

### ADR-020 — Camada de plataforma
**Status:** Proposta
**Decisão:** todo código que depende do sistema operacional fica em `backend/src/avante/platform/` e em `packaging/`. A aplicação usa só interfaces (caminhos, controle de serviço, permissões de arquivo, informações de disco/energia/criptografia para o `avante doctor`). Regras: `pathlib` sempre; nenhum caminho fixo; nada de `fork`, sinais POSIX ou permissões Unix fora da camada; testes da camada rodam nos dois sistemas no CI.

---

## 6. Segurança — modelo de ameaças inicial (STRIDE)

| Ameaça | Exemplo | Mitigações |
|---|---|---|
| **S**poofing | Credencial roubada, força bruta, sessão reaproveitada | Argon2id, MFA obrigatório para privilégios, limites, sessões revogáveis, passkeys |
| **T**ampering | Alterar saldo ou histórico | Ledger append-only, auditoria encadeada por hash, papéis de banco sem UPDATE/DELETE |
| **R**epudiation | "Não fui eu que dei baixa" | Auditoria com ator, dispositivo, IP e request_id |
| **I**nformation disclosure | Vazamento de dados pessoais; backup ou notebook roubado; evento em tempo real para quem não pode ver | Criptografia de disco, backup criptografado, mínimo de dados pessoais, autorização por escopo, filtragem de eventos SSE no servidor, logs sem dados sensíveis |
| **D**enial of service | Upload gigante, OCR pesado, enxurrada de requisições, muitas conexões SSE | Limites antes do processamento, jobs no worker com timeout, rate limiting, limite de conexões por sessão, limites de corpo no Caddy |
| **E**levation of privilege | Membro em rota de gestor; IDOR; serviço com privilégio demais no SO | RBAC com escopo no serviço, testes horizontais/verticais por rota, step-up, serviços sem privilégio (systemd sandbox / conta virtual no Windows) |

**Controles transversais:** CSP estrita sem `unsafe-inline`; HSTS; `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` (câmera só no próprio domínio), `frame-ancestors 'none'`; CSRF por token + verificação de `Origin`; XML sem entidades externas; templates com escape automático; SSH só por chave (Linux) / RDP desativado ou restrito à VPN (Windows); papéis PostgreSQL separados (migração × aplicação × relatórios somente leitura); PostgreSQL ouvindo só em `localhost`.

## 7. Observabilidade

- Logs JSON com `request_id`, ID do usuário (nunca senha ou token), rota, status e latência; retenção configurada nos dois sistemas.
- Métricas: latência, erros, conexões SSE, fila de jobs, idade do último backup e do último teste de restauração, validade do certificado, disco, bateria/energia.
- Alertas ao Proprietário (e-mail/push): backup falho, restauração de teste falha, disco > 85%, certificado < 14 dias, divergência de reconciliação, jobs falhando, servidor em bateria.
- `avante doctor`: verifica serviços, portas, firewall, criptografia de disco, energia, certificado, backup e versão, com mensagens acionáveis.
