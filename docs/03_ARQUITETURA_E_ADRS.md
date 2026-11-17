# Volume 03 — Arquitetura e Registro de Decisões (ADRs)

**Produto:** Avante Almoxarifado · **Versão:** 3.0.0 · **Data:** 17/11/2026 · **Status:** Proposto — aguarda aprovação
**Responsável:** Luís Eduardo de Sousa Barbosa
**Relação:** atende o Volume 02. Hardware e capacidade: Volume 04. Visão computacional e embarcados: Volume 05. Segurança: Volume 06. Operação: Volume 10.
**Regra:** ADRs ficam *Propostas* até aprovação na R0. Mudar uma ADR *Aceita* exige nova ADR que a substitua.

---

## 1. Contexto e restrições

| Restrição | Efeito na arquitetura |
|---|---|
| Servidor da Avante = notebook antigo (DDR3, HD, provável ausência de TPM 2.0) | Serviços enxutos e com limite de memória; nada pesado no servidor; disco rígido exige I/O disciplinado (ADR-023) |
| ~30 pessoas com acesso, uso simultâneo baixo | Processo único de API com poucos workers; sem cache distribuído, sem Redis, sem broker |
| Edição Comercial em Linux **e** Windows | Camada de plataforma desde o primeiro dia (ADR-020); Windows entregue na R4 (ADR-002) |
| Visão computacional e estações embarcadas | Inferência no aparelho ou na estação (ADR-024); dispositivos falam HTTPS com o servidor (ADR-025) |
| Acesso pela rede local e pela internet | HTTPS válido sem porta aberta; acesso externo por VPN ou túnel (ADR-007) |
| Um desenvolvedor | Monólito modular, poucas tecnologias, automação forte de testes e entrega |
| Produto vendável | Licenças compatíveis com software fechado (ADR-016); marca centralizada; licença de uso (ADR-014) |

## 2. Visão geral

```
 Celulares · tablets · notebooks (PWA)          Estações embarcadas (Volume 05)
 ┌──────────────────────────────────────┐       ┌───────────────────────────────────────┐
 │ App React + leitura de códigos e     │       │ Leitor de cartão de balcão (ESP32)    │
 │ VISÃO COMPUTACIONAL NO APARELHO      │       │ Estação Avante (comercial): câmera,   │
 │ (contagem, reconhecimento, OCR)      │       │ leitor de cartão, tela, visão local   │
 └───────────────┬──────────────────────┘       └────────────────┬──────────────────────┘
                 │ HTTPS (rede local direta; de fora: VPN ou túnel — ADR-007)
                 ▼                                                ▼
┌──────────── Servidor: notebook (Perfil Mínimo: DDR3, HD, Linux sem interface gráfica) ───────────┐
│ Firewall: nega tudo; 443 só na rede local/VPN                                                     │
│ ┌────────┐  /         ┌──────────────────────────┐  SQL  ┌─────────────────┐ WAL ─► restic ───────┼─► backup externo
│ │ Caddy  │───────────►│ SPA/PWA estática          │       │ PostgreSQL 18   │                     │   criptografado
│ │ (TLS)  │─/api/v1───►│ API FastAPI + SSE         │◄─────►│ (sessão em UTC) │                     │
│ └────────┘            │ (2 processos, limite RAM) │       └───────▲─────────┘                     │
│                       └──────────────────────────┘    fila/LISTEN│                               │
│                       ┌──────────────────────────┐               │                               │
│                       │ Worker (1 tarefa por vez,│───────────────┘ e-mail · push · relatórios ·   │
│                       │ prioridade baixa)        │                 reconciliação · verificações   │
│                       └──────────────────────────┘                                                │
│ CLI `avante` (status, doctor, backup, restore, update, rollback) · logs JSON · SMART · alertas    │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 3. Stack

| Camada | Escolha | Justificativa | Licença |
|---|---|---|---|
| SO do servidor | Edição Avante: Debian 13 ou Ubuntu Server 24.04/26.04 LTS sem interface gráfica · Comercial: + Windows 11 Pro com suporte vigente | Leve para hardware antigo; suporte longo | — |
| Banco | PostgreSQL 18 | Transações, constraints, `SKIP LOCKED`, `LISTEN/NOTIFY`, `timestamptz`; configurável para pouca memória | PostgreSQL |
| Backend | Python 3.14 (3.13 como alternativa), FastAPI, SQLAlchemy 2 tipado, Alembic, Pydantic v2, psycopg 3 | Continuidade do MVP; ecossistema maduro | MIT/BSD |
| Runtime | Python embutido no pacote (python-build-standalone) com dependências travadas | Independe do Python do sistema | MPL-2.0/PSF (análise registrada) |
| Servidor ASGI | Uvicorn, 2 processos no Perfil Mínimo | Comportamento igual em Linux e Windows | BSD |
| Senhas | Argon2id (argon2-cffi), parâmetros calibrados no hardware (mínimo OWASP: 19 MiB, t=2) | Recomendação atual | MIT |
| Fila/jobs | Fila no PostgreSQL com `FOR UPDATE SKIP LOCKED` | Sem Redis; transacional | — |
| PDF/OCR no servidor (só R2, DANFE) | pypdfium2 + pdfminer.six + Tesseract, no worker, com limite de páginas e memória | Licenças compatíveis | Apache/BSD/MIT |
| Proxy/TLS | Caddy com módulo DNS-01 | HTTPS automático sem porta aberta; leve | Apache-2.0 |
| Backup | `pg_basebackup` + WAL + restic | Multiplataforma, criptografado | PostgreSQL/BSD-2 |
| Frontend | React 19 + TypeScript estrito + Vite, React Router, TanStack Query, React Hook Form + Zod | App 100% cliente, build estático | MIT |
| UI | Design system próprio (tokens + Tailwind + Radix UI + Lucide + Storybook) — Volume 07 | Acessibilidade e consistência | MIT/ISC |
| Leitura de códigos | `BarcodeDetector` + zxing-wasm | Decodificação no aparelho | Apache-2.0 |
| **Visão no aparelho** | ONNX Runtime Web (WebAssembly/WebGPU) + OpenCV.js + modelos de licença permissiva (ADR-024) | Inferência local, offline, sem custo de servidor | MIT/Apache-2.0 |
| **Firmware** | ESP-IDF (C) com FreeRTOS para o leitor de cartão | Robusto, OTA nativo, conhecimento do Avante Ponto | Apache-2.0/MIT |
| **Estação Avante** (R4) | Linux embarcado em computador de placa única + câmera + leitor 13,56 MHz + tela; app em modo quiosque | Visão local com mais desempenho | A definir (Volume 05) |
| Testes | pytest, Hypothesis, Vitest, Testing Library, Playwright, axe-core, k6, Unity (firmware) | Volume 09 | MIT/Apache |
| Qualidade/segurança | ruff, mypy estrito, ESLint, Prettier, Bandit/Semgrep, pip-audit, OSV-Scanner, gitleaks, CycloneDX, verificação de licenças | Gates automáticos | Diversas (ferramentas de CI) |

## 4. Estrutura do repositório (branch `definitivo`)

```
avante-almoxarifado (branch definitivo)
├── backend/
│   ├── src/avante/
│   │   ├── core/            # config, db, segurança, erros, logging, request_id, idempotência, eventos
│   │   ├── platform/        # ÚNICO lugar com código específico de SO (ADR-020)
│   │   ├── modules/         # identity, organization, catalog, inventory, loans, documents, labels,
│   │   │                    # support, collaboration, notifications, reports, audit, admin,
│   │   │                    # vision (índice e modelos), devices, automation, data_portability, commercial
│   │   ├── realtime/        # SSE e distribuição de eventos
│   │   ├── worker/
│   │   └── cli/             # comando `avante`
│   ├── migrations/
│   └── tests/{unit,integration,concurrency,migrations,platform,performance}/
├── frontend/
│   ├── src/{app,features/<módulo>,components/ui,lib/{api,i18n,dates,scanner,vision,realtime}}/
│   ├── design-tokens/
│   └── tests/{unit,e2e,visual}/
├── vision/                  # avaliação de modelos, conjuntos de validação (só metadados no Git), conversão ONNX
├── firmware/
│   └── leitor-cartao/       # ESP-IDF: leitor de cartão de balcão
├── packaging/{linux,windows,common}/
├── ops/                     # runbooks, monitoramento, scripts de verificação de hardware
├── brand/
├── docs/
└── .github/workflows/
```

Cada módulo do backend tem `router.py`, `schemas.py`, `service.py`, `repository.py` e `models.py`; módulos conversam por serviços, nunca acessando tabelas uns dos outros diretamente.

---

## 5. ADRs

### ADR-001 — Produto novo, sem código do MVP; MVP congelado
**Status:** Proposta (revisada em 17/11/2026 por decisão do responsável, D-21)
**Decisão:** construir o produto do zero na branch `definitivo` (ADR-019). **Nenhum código do MVP é copiado ou adaptado** — nem backend, frontend, migrations, testes, configurações ou scripts. O MVP serve **apenas como referência de funcionalidades** (Anexo A1) e de defeitos a não repetir (Volume 02 §4): o que ele faz é estudado e reimplementado a partir dos requisitos e do modelo de interface aprovado, com testes novos. Todas as funções do MVP são preservadas e melhoradas. O MVP não é modificado; seus dados entram só pelo importador (R2) e ele é aposentado quando a R2 for aceita (ADR-026).
**Motivo:** o código do MVP foi feito como norte do produto e tem qualidade inferior à exigida; copiá-lo traria junto seus defeitos e adaptações.

### ADR-002 — Servidor nativo; Linux primeiro, Windows na Edição Comercial
**Status:** Proposta (substitui a versão que entregava Linux e Windows juntos)
**Contexto:** o notebook da Avante não atende aos requisitos do Windows 11 (processador anterior à 8ª geração Intel, provável ausência de TPM 2.0), e há um único desenvolvedor. Entregar instalador e operação nos dois sistemas desde a R1 dobraria o esforço sem benefício para a Avante.
**Decisão:**
- Serviços nativos, sem Docker em produção.
- **R1–R3:** Linux (Debian 13 ou Ubuntu Server LTS, sem interface gráfica), que é a plataforma da Avante.
- **Desde a R0:** todo código específico de SO isolado na camada de plataforma (ADR-020), e testes unitários e de integração rodando também em Windows no CI. Assim a adaptação continua real, e não promessa.
- **R4:** instalador `.msi`, serviços do Windows, firewall, energia e backup no Windows, homologados com a mesma bateria de testes do Linux.

| Aspecto | Linux | Windows 11 (R4) |
|---|---|---|
| Serviços | systemd com sandbox (`NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome`, `PrivateTmp`, `ReadWritePaths` mínimos) e limites (`MemoryMax`, `CPUWeight`, `IOWeight`) | Serviços do Windows via WinSW (MIT), conta virtual dedicada, início automático atrasado, reinício em falha, Job Objects com limite de memória |
| Usuário de serviço | `avante`, sem shell | `NT SERVICE\Avante*`, sem login interativo |
| Programas / configuração / dados / logs | `/opt/avante` · `/etc/avante` (0640) · `/var/lib/avante` · journald | `%ProgramFiles%\Avante` · `%ProgramData%\Avante\config` (ACL) · `%ProgramData%\Avante\data` (ACL) · arquivos JSON + Log de Eventos |
| PostgreSQL | Pacote PGDG | Binários oficiais embutidos, `pg_ctl register` |
| Firewall | nftables/ufw: nega tudo, 443 só LAN/VPN | Windows Defender Firewall: perfil Privado e interface da VPN |
| Energia/tampa | `logind.conf` (ignorar tampa), `sleep.target` mascarado, desligamento ordenado com bateria crítica | `powercfg` equivalente |
| Atualizações do SO | unattended-upgrades com janela de reinício | Windows Update com horário ativo |
| Criptografia | ADR-012 | BitLocker + TPM |

### ADR-003 — Docker apenas como ferramenta de CI
**Status:** Proposta
**Decisão:** PostgreSQL de testes como *service container* nos runners Linux; nos runners Windows, PostgreSQL instalado no runner. Nenhum artefato de produção depende de Docker (Docker também pesaria demais no Perfil Mínimo).

### ADR-004 — SPA React + Vite no mesmo domínio da API
**Status:** Proposta
**Decisão:** SPA estática servida pelo Caddy; API em `/api/v1` no mesmo domínio; sem CORS em produção; cookie `SameSite=Strict`. Sem servidor Node em produção (economiza memória e superfície de ataque). Como a página carrega estática e chama a API na mesma origem, links abertos de fora (QR pela câmera nativa, e-mail) funcionam com `SameSite=Strict`.

### ADR-005 — Sessões no servidor, MFA e passkeys
**Status:** Proposta
**Decisão:** token de sessão aleatório de 256 bits guardado só como hash e vinculado ao ID interno; cookie `__Host-avante_session` (`Secure`, `HttpOnly`, `SameSite=Strict`); inatividade e duração absoluta configuráveis; rotação no login e na elevação; revogação imediata em troca de senha, desativação, mudança de papel, logout e "sair de todos"; MFA TOTP obrigatório para papéis privilegiados; reautenticação para ações sensíveis; passkeys (R2); limites por conta e por IP no PostgreSQL.

### ADR-006 — Ledger de movimentações como fonte de verdade
**Status:** Proposta
**Decisão:** `movimentacoes` append-only (papel da aplicação sem UPDATE/DELETE); saldos atualizados na mesma transação com `CHECK (quantidade >= 0)` e bloqueio em ordem determinística; quantidades `numeric(18,4)` com unidade de medida; máquina de estados das unidades no serviço e no banco; reconciliação diária **fora do horário de uso** (RNF-22); `Idempotency-Key` em toda mutação, inclusive as originadas por dispositivos e por visão computacional; concorrência otimista (`version`, ETag/If-Match) em cadastros.

### ADR-007 — Rede, HTTPS válido e acesso remoto sem portas abertas
**Status:** Proposta — decisão final na R0 (validação de rede)
**Comum:** nome por organização (`<organizacao>.<dominio-do-produto>`); certificado Let's Encrypt por desafio DNS-01 (sem porta aberta); **servidor ligado por cabo** à rede, com IP reservado no roteador.

| Opção | Rede local | Fora da rede | Prós | Contras |
|---|---|---|---|---|
| **A. VPN WireGuard (Tailscale ou Headscale)** | Direto pelo IP local | App de VPN no aparelho | Ponta a ponta; nada exposto; leve no servidor | App de VPN em cada aparelho remoto |
| **B. Túnel de saída com camada de acesso** | Direto ou pelo túnel | Só navegador | Sem app extra; proteção de borda | TLS termina no provedor; avaliação LGPD |
| C. Porta 443 aberta no roteador | Direto | Direto | Simples | Expõe o notebook; **não recomendado** |

**Recomendação provisória:** A como padrão; B como opção. A validação na R0 confirma resolução de nome na rede local (proteção contra *DNS rebinding* em roteadores), câmera, push e o consumo de memória do cliente VPN no notebook.

### ADR-008 — Arquivos fora do banco
**Status:** Proposta
**Decisão:** fotos, anexos e documentos no diretório de dados, com nome por hash; metadados no banco. Limites de bytes e pixels antes de decodificar; **compressão e redimensionamento no aparelho** antes do envio (poupa disco e CPU do servidor); reencodificação sem metadados (EXIF removido); limites por arquivo e por requisição; entrega com `Content-Type` correto e `nosniff`. Arquivos entram no backup.

### ADR-009 — Worker separado, outbox e jobs
**Status:** Proposta
**Decisão:** serviço `avante-worker` independente, executando **uma tarefa pesada por vez**, com prioridade baixa de CPU e disco e limite de memória; outbox na mesma transação do evento; e-mails, push, relatórios grandes, etiquetas em lote, OCR de DANFE (R2), reconciliação e verificações rodam só no worker, com timeout. Tarefas de manutenção agendadas para fora do horário de uso; trava contra execução duplicada.

### ADR-010 — Contrato de API
**Status:** Proposta
**Decisão:** `/api/v1`; OpenAPI como contrato; cliente TypeScript gerado no CI; envelope de erro com códigos de domínio estáveis (`STOCK_INSUFFICIENT`, `QR_UNKNOWN`, `QR_REVOKED`, `QR_FOREIGN_ORG`, `DEVICE_REVOKED`...); paginação por cursor; datas ISO 8601 com `Z`; respostas compactas (sem campos desnecessários) e compressão no Caddy. Dispositivos usam a mesma API com escopo próprio (ADR-025).

### ADR-011 — Formato do QR Code
**Status:** Proposta
**Decisão:** conteúdo `https://<endereço-da-organização>/q/<CÓDIGO>`, em que `<CÓDIGO>` = letra do tipo (`U` unidade, `L` local, `I` item a granel, `K` lote, `T` kit, `C` conexão) + 16 caracteres Base32 Crockford (80 bits aleatórios) + 1 verificador. O leitor do app ignora o domínio e usa só o código. Nenhum dado de negócio ou pessoal no QR. Correção de erro nível Q. Detalhes no Volume 08.

### ADR-012 — Backup, recuperação e criptografia
**Status:** Proposta (revisada para hardware sem TPM 2.0)
**Decisão:**
- **Backup:** `pg_basebackup` semanal + arquivamento contínuo de WAL; restic envia backups, WAL e arquivos para repositório externo (S3 compatível) e, opcionalmente, para um disco USB; criptografado e com deduplicação; RPO ≤ 15 min; retenção configurável; `restic check` semanal; **teste de restauração automático mensal**. Backup roda com prioridade baixa de I/O (disco rígido).
- **Criptografia de disco — depende do hardware, verificado na R0:**

| Hardware | Opção | Efeito |
|---|---|---|
| Com TPM 2.0 | LUKS2 com desbloqueio automático por TPM2 (Linux) ou BitLocker (Windows) | Volta sozinho após queda de energia; disco ilegível se removido |
| **Sem TPM 2.0 (provável no notebook da Avante)** | **Recomendado:** sem criptografia de disco inteiro + **criptografia dos backups** + segredos com permissão restrita + segurança física (notebook preso/trancado) + registro dessa decisão de risco | Volta sozinho após queda; o risco de furto do notebook fica documentado e aceito pelo responsável |
| Sem TPM 2.0, com alguém disponível após quedas | LUKS2 com senha digitada no boot | Disco protegido, mas o sistema **não volta sozinho** após queda de energia (viola RNF-06) |

- A senha do repositório de backup fica com o responsável (cópia impressa em local seguro); sem ela, o backup não se recupera.
- Restauração cruzada (Linux ↔ Windows, mesma versão do PostgreSQL) testada na R4.

### ADR-013 — Distribuição, atualização e rollback
**Status:** Proposta
**Decisão:** Linux: pacote `.deb` (amd64) com runtime embutido, em repositório apt assinado (R1). Windows: `.msi` assinado com Authenticode (R4). `avante update`: verifica assinatura → backup → para serviços → instala → migra → health check → volta para a versão anterior se falhar. Migrations *expand/contract*. Canais `stable` e `beta`. Atualizações aplicadas fora do horário de uso.

### ADR-014 — Licenciamento do produto
**Status:** Proposta — implementação na R4 (Edição Comercial); a Edição Avante não verifica licença
**Decisão:** licença JSON assinada com Ed25519, verificada offline, com edição (Essencial/Inteligente), limites (usuários, estações) e validade; ao expirar, carência e depois modo somente leitura — nunca bloquear o acesso aos dados do cliente nem apagar nada. Sem telemetria obrigatória.

### ADR-015 — Datas e fuso horário
**Status:** Proposta
**Decisão:** colunas `timestamptz`; sessão do banco fixada em UTC; datetimes sempre com fuso; API emite `Z`; frontend converte para o fuso da organização com função única testada; testes com o PostgreSQL configurado em fuso ≠ UTC.

### ADR-016 — Política de licenças de terceiros (software, modelos e firmware)
**Status:** Proposta
**Decisão:**
- Permitidas: MIT, BSD, Apache-2.0, ISC, PostgreSQL, Zlib, PSF; OFL-1.1 para fontes.
- Com análise registrada: MPL-2.0, LGPL (ligação dinâmica), EPL.
- **Proibidas** em componentes distribuídos sem decisão do responsável: GPL, AGPL, SSPL, licenças "não comerciais".
- **Modelos de visão computacional:** a licença dos **pesos** e a do **código de treino** são verificadas separadamente; só entram pesos publicados com licença que permita uso comercial. A origem dos dados de treino fica registrada na ficha do modelo; quando o pré-treino usou conjuntos com termos restritivos (caso comum em modelos pré-treinados em ImageNet), isso passa por análise registrada e revisão jurídica antes da venda (Volume 05 §4). Conjuntos próprios com licença não comercial não podem ser usados no treino. Modelos com licença AGPL (por exemplo, a família YOLO da Ultralytics) são **proibidos** nos produtos distribuídos.
- **Firmware:** bibliotecas embarcadas seguem a mesma política; cada binário de firmware acompanha seu inventário de licenças.
- Verificação automática no CI; inventário de licenças publicado com cada release.
- Substituição já decidida: PyMuPDF (AGPL) → pypdfium2 + pdfminer.six.

### ADR-017 — Aplicativo instalável (PWA) e conexão à organização
**Status:** Proposta
**Decisão:** PWA servida pelo servidor de cada organização; instalação a partir do endereço da organização ou do QR de conexão; atualização controlada pelo service worker; leitura offline do catálogo, de "meus empréstimos" e das fichas visitadas, **incluindo os modelos de visão já baixados**; ações exigem conexão. Pós-R4: casca para lojas com "Conectar à organização".

### ADR-018 — Interação em tempo real
**Status:** Proposta
**Decisão:** SSE em `/api/v1/events` por sessão autenticada, filtrado por permissão no servidor; reconexão com `Last-Event-ID`; distribuição entre processos por `LISTEN/NOTIFY`; Web Push (VAPID) pelo worker; consulta periódica como reserva. No Perfil Mínimo, o limite de conexões SSE (RNF-05: 60) é configurado e testado; cada conexão ociosa custa poucos KB no processo assíncrono.

### ADR-019 — Branch `definitivo` no repositório do MVP
**Status:** Proposta
**Decisão:** branch órfã `definitivo`; a `main` continua sendo o MVP. Entrada por PR com CI verde; sem force-push; branches `feat/<ID>-<descricao>`; workflows só para `definitivo`; tags `app-vX.Y.Z`. Commits e pushes só com autorização do responsável. **Antes da venda (R4), o repositório se torna privado** (Volume 11).

### ADR-020 — Camada de plataforma
**Status:** Proposta
**Decisão:** código dependente do SO só em `backend/src/avante/platform/` e `packaging/`. A aplicação usa interfaces (caminhos, serviços, permissões, informações de disco, SMART, temperatura, energia e criptografia para o `avante doctor`). `pathlib` sempre; nada de `fork`, sinais POSIX ou permissões Unix fora da camada; testes da camada nos dois sistemas no CI desde a R0.

### ADR-021 — Design system com tokens como fonte da verdade
**Status:** Proposta
**Decisão:** tokens em JSON (primitivos → semânticos → componente) convertidos por Style Dictionary; temas claro/escuro e marca são conjuntos de tokens com contraste verificado; componentes sobre Radix UI no Storybook; no CI, contraste, proibição de valores soltos, axe, testes visuais e Lighthouse (RNF-18). Telas são desenhadas no Claude Design antes de implementar (Volume 07).

### ADR-022 — Política de versões de plataforma
**Status:** Proposta
**Decisão:** cada release fixa versões exatas, testadas juntas; só entram versões com suporte oficial por pelo menos 3 anos (hoje: PostgreSQL 18, Python 3.14, Debian 13, Ubuntu 24.04/26.04, Windows 11 25H2+); PostgreSQL 19 reavaliado na R0; `pg_upgrade` pelo `avante update` com backup e rollback; alerta quando algo sai do suporte.

### ADR-023 — Perfis de hardware e orçamento de recursos
**Status:** Proposta
**Contexto:** o servidor da Avante é um notebook antigo com DDR3 e disco rígido; clientes terão máquinas variadas.
**Decisão:**
- Três perfis oficiais — **Mínimo** (o notebook da Avante: x86-64, 2 núcleos, 4 GB DDR3, HD), **Recomendado** e **Comercial certificado** — com metas de desempenho próprias (Volume 04, RNF-05).
- **Orçamento de memória por serviço**, imposto pelo gerenciador de serviços (RNF-20), e parâmetros do PostgreSQL calibrados para pouca memória e disco rígido.
- Tudo que é pesado sai do servidor: decodificação de QR, visão computacional, compressão de imagens e geração de miniaturas são feitas no aparelho; o servidor guarda e serve.
- O instalador mede o hardware e se recusa a instalar abaixo do Mínimo (RF-COM-01).
- Melhorias baratas de hardware (SSD, mais memória) são **recomendadas, não exigidas**; o ganho esperado é medido na R0 para o responsável decidir.

### ADR-024 — Visão computacional na ponta, nunca no servidor
**Status:** Proposta
**Contexto:** o notebook-servidor não tem capacidade para inferência; celulares atuais e computadores de placa única têm.
**Decisão:**
- Inferência no **navegador do aparelho** (ONNX Runtime Web com WebAssembly, WebGPU quando disponível; OpenCV.js para processamento clássico) e, na Edição Inteligente, **na Estação Avante**.
- O servidor guarda apenas: modelos versionados (arquivos estáticos), **vetores de características** das fotos de referência do catálogo (para reconhecimento) e os resultados confirmados. A busca de similaridade é feita no servidor sobre vetores compactos (`int8`, índice em memória ≤ 30 MB) ou, se o catálogo crescer, no aparelho.
- Modelos pequenos (≤ 15 MB), quantizados, com licença permissiva (ADR-016); cada recurso tem métrica mínima de qualidade (RNF-23) e protocolo de avaliação (Volume 05).
- A visão **sugere**; a pessoa **confirma**. Nenhuma movimentação é registrada só por inferência.
- Imagens não saem do aparelho, salvo quando o usuário anexa uma foto ou contribui com uma imagem de referência/validação (ADR-028).

### ADR-025 — Integração de dispositivos embarcados
**Status:** Proposta
**Decisão:**
- Dispositivos falam com o servidor por **HTTPS (TLS) na rede local**, usando a mesma API com escopo de dispositivo; sem broker MQTT (poupa recursos no Perfil Mínimo e reduz superfície de ataque).
- Cada dispositivo tem identidade e credencial próprias, emitidas no pareamento aprovado por um administrador, revogáveis (RF-EMB-01); o servidor valida que o dispositivo só executa ações do seu escopo (ex.: leitor de cartão só envia "cartão apresentado").
- Comandos do servidor para o dispositivo por SSE ou consulta curta; heartbeat a cada 30 s para a saúde (RF-EMB-04).
- Firmware com watchdog, OTA assinado com reversão automática (RF-EMB-05) e **nenhum registro de movimentação local** sem servidor (RF-EMB-06).
- O leitor de cartão **identifica**, não autentica: UIDs de cartões comuns podem ser copiados, por isso autoatendimento exige PIN e ações sensíveis exigem login (Volume 06).

### ADR-026 — Entrega em releases incrementais e coexistência com o MVP
**Status:** Proposta
**Contexto:** há um único desenvolvedor, e o produto completo é grande.
**Decisão:** entregar em releases utilizáveis (R0–R4, Volume 12), cada uma com gate e critérios de saída. A R1 entra em uso real **em paralelo** ao MVP; a R2 atinge paridade com o MVP, importa seus dados e o **aposenta**; R3 adiciona inteligência e embarcados; R4 prepara a venda. Um requisito *S* pode passar para a release seguinte com registro; um *M* não.

### ADR-027 — Automação de estoque com estatística simples
**Status:** Proposta
**Decisão:** sugestões de reposição e alertas (RF-AUT) usam estatística explicável (médias móveis, tendência, desvio, sazonalidade simples) calculada no worker, fora do horário de uso. Nada de modelos pesados no servidor. Toda sugestão mostra **por que** foi feita (ex.: "consumo médio de 12 un/semana; restam 1,5 semana").

### ADR-028 — Privacidade das imagens
**Status:** Proposta
**Decisão:** fluxos de visão computacional são desenhados para **não capturar pessoas**: enquadramento em bandeja, caixa ou compartimento; aviso na tela; imagens de inferência descartadas após o uso; imagens guardadas só quando o usuário anexa ou contribui como referência/validação, sempre de itens, com origem registrada. Reconhecimento facial é proibido. Câmeras fixas (pós-R4) exigem relatório de impacto à proteção de dados (Volume 06).

---

## 6. Segurança, operação e observabilidade

- Modelo de ameaças, controles, LGPD e segurança de dispositivos: **Volume 06**.
- Instalação, backup, atualização, monitoramento e runbooks: **Volume 10**.
- Perfis de hardware, parâmetros e capacidade: **Volume 04**.
