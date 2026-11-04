# Análise de Rota — Avante Almoxarifado (Produto Definitivo)

**Versão:** 1.0 · **Data:** 03/11/2026
**Pergunta:** qual é o melhor caminho para entregar um aplicativo de excelência que funcione em notebooks, celulares e tablets, com servidor Linux **ou** Windows em um notebook do cliente, acesso local e remoto, interação entre usuários e venda comercial?
**Base:** auditoria do MVP, requisitos informados pelo responsável em 03/11/2026, Plano Mestre v2.3 e ADRs v1.3.

---

## 1. Requisitos que guiam a rota

1. Produto da **Avante Tech Jr**, instalado **localmente** em um notebook (um por instalação), usado internamente na 1.0 e **preparado para venda futura**.
2. Servidor em **Linux ou Windows**.
3. Usado como **aplicativo**: o usuário baixa/instala e interage com outros usuários (ex.: chamado de suporte que a equipe vê e responde).
4. Notebooks, celulares e tablets, **dentro e fora** da rede do cliente; servidor com internet.
5. Todas as funções do MVP preservadas e melhoradas (`MATRIZ_FUNCIONALIDADES_MVP.md`).
6. Segurança, robustez e qualidade comprováveis.
7. MVP continua operando; código novo em **outra branch do mesmo repositório**.

## 2. Decisões de rota

Cada decisão compara as alternativas reais; a escolhida está em **negrito**.

### D-01 — Base de código
| Alternativa | Avaliação |
|---|---|
| Evoluir o MVP no lugar | O modelo de dados (item = catálogo + unidade) e os defeitos estruturais exigiriam reescrever quase tudo, carregando dívidas (migrations quebradas, testes desatualizados) |
| **Código novo, reaproveitando conhecimento e trechos validados do MVP** | Domínio correto desde o início; MVP intocado; exige importador de dados |

### D-02 — Forma do aplicativo
| Alternativa | Celular/tablet | Notebook | Custo e risco |
|---|---|---|---|
| **PWA (aplicativo web instalável)** | Instala pela tela inicial (Android; iPhone/iPad pelo Safari) | Instala pelo Chrome/Edge no Windows, Linux e macOS | Um código só; atualização instantânea; sem taxa de loja |
| Casca Capacitor (PWA empacotada para lojas) | Play Store e App Store | — | +1 build por loja; revisão da Apple; contas de desenvolvedor pagas |
| Apps nativos (Kotlin/Swift) ou Flutter | Ótimo acesso ao hardware | Exige outra solução | 2–3 bases de código; não se justifica para este domínio |
| Electron | — | App de desktop | Grande, mais uma superfície de ataque; o navegador já basta |

**Decisão:** **PWA na 1.0** em todas as plataformas. Isso atende "baixar e usar": o usuário instala o app a partir do endereço da organização (ou escaneando o QR de conexão) e ele abre como aplicativo, com ícone, tela cheia e notificações. **Depois da 1.0**, uma casca Capacitor publicada como "Avante Almoxarifado" na Play Store e na App Store, com tela "Conectar à organização" (escaneando o QR de conexão), se o mercado pedir presença em loja.

Limitações honestas da PWA, todas com contorno: no iPhone, notificações push exigem o app instalado na tela inicial (iOS 16.4+); o Firefox não tem leitor de QR nativo (contorno: zxing-wasm); escrita offline fica fora da 1.0 (leitura offline incluída).

### D-03 — Interação entre usuários em tempo real
| Alternativa | Avaliação |
|---|---|
| Atualizar a tela manualmente (MVP) | Não é experiência de aplicativo |
| Consultar o servidor a cada X segundos | Simples, mas atrasado e com custo constante |
| **Server-Sent Events (SSE) + Web Push** | SSE leva eventos ao app aberto (nova mensagem, aprovação, devolução); Web Push avisa com o app fechado. SSE atravessa proxy/VPN sem configuração especial |
| WebSocket | Bidirecional; desnecessário aqui (as ações já vão por HTTP) e mais complexo |

**Decisão:** SSE com distribuição de eventos via `LISTEN/NOTIFY` do PostgreSQL, Web Push (VAPID) enviado pelo worker, e consulta periódica só como reserva. Interações cobertas: chamados de suporte (conversa em tempo real), comentários em empréstimos e solicitações, aprovações, notificações. Chat livre entre usuários **não** entra (custo de moderação e privacidade sem ganho para o almoxarifado).

### D-04 — Backend
| Alternativa | Avaliação |
|---|---|
| **Python 3.14 + FastAPI + SQLAlchemy** | Continuidade do conhecimento do MVP; bibliotecas maduras para XML, PDF, imagens, OCR |
| Go (binário único) | Empacotamento mais simples em Windows/Linux; porém reescrita total e ecossistema mais fraco para PDF/OCR |
| Node/NestJS | Sem ganho que justifique trocar |

**Decisão:** Python, com **runtime Python embutido no instalador** (python-build-standalone), o que elimina a dependência do Python do sistema e torna Windows e Linux iguais.

### D-05 — Banco de dados
| Alternativa | Avaliação |
|---|---|
| **PostgreSQL 18** | Concorrência, constraints, `SKIP LOCKED`, `LISTEN/NOTIFY`, `timestamptz`; disponível nativamente em Windows e Linux |
| SQLite | Instalação trivial, mas fraco para muitos usuários simultâneos e para a fila de jobs |

### D-06 — Servidor em Linux **e** Windows
| Alternativa | Avaliação |
|---|---|
| **Instalação nativa por sistema, com uma camada comum** | Mesmo código de aplicação; diferenças isoladas em instalador, serviços e caminhos; CLI `avante` com os mesmos comandos nos dois sistemas |
| Docker Desktop no Windows | Depende de WSL2/virtualização, é frágil em notebook, e o Docker Desktop exige licença paga em empresas grandes. Descartado |
| Máquina virtual Linux dentro do Windows | Dobra a manutenção e o consumo; descartado |

**Matriz de suporte do servidor:**
| Sistema | Situação | Motivo |
|---|---|---|
| Ubuntu 26.04 LTS | **Suportado (referência)** | Suporte padrão até 2031 |
| Ubuntu 24.04 LTS | Suportado | Suporte padrão até 2029 |
| Debian 13 | Suportado | Mesmo empacotamento `.deb`; suporte até 2030 (com LTS) |
| Windows 11 Pro em versão suportada (hoje 25H2 ou mais nova) | **Suportado** | BitLocker disponível; cada versão do Windows 11 Home/Pro tem 24 meses de suporte |
| Windows 11 Home | Suportado com aviso | Criptografia de disco depende do hardware ("Criptografia do dispositivo") |
| Windows 10 | **Não suportado** | Fim do suporte da Microsoft em 14/10/2025 |

O que muda entre os sistemas (todo o resto é igual):
| Aspecto | Linux | Windows |
|---|---|---|
| Serviços | systemd com sandbox | Serviços do Windows (WinSW) com conta de serviço dedicada |
| PostgreSQL | Pacote oficial PGDG | Binários oficiais embutidos no instalador e registrados como serviço |
| HTTPS | Caddy | Caddy (mesmo binário, versão Windows) |
| Backup | `pg_basebackup` + arquivamento de WAL + restic | Idem (todas as ferramentas existem nos dois) |
| Criptografia de disco | LUKS2 + TPM2 | BitLocker + TPM |
| Firewall | ufw/nftables | Windows Defender Firewall (perfil privado) |
| Energia/tampa | logind e `sleep.target` | `powercfg` |
| Instalador | `.deb` assinado em repositório apt | `.msi` assinado (Authenticode) |
| Atualização do SO | unattended-upgrades | Windows Update com janela de reinício fora do expediente |

Custo honesto: suportar os dois sistemas **dobra** o esforço de empacotamento, testes de instalação, documentação de operação e suporte. O código da aplicação é compartilhado. Por isso o CI testa nos dois sistemas desde a Fase 1, e nenhum gate de plataforma aprova um sistema sem o outro.

### D-07 — Acesso de dentro e de fora da rede
Mantida a ADR-007: certificado válido emitido por DNS-01 (sem porta aberta), rede local direta, acesso externo por **VPN WireGuard (padrão)** ou **túnel (alternativa)**, decidido no spike do Gate 0. Funciona igual em Windows e Linux.

### D-08 — Backup
Troca em relação à ADR-012 v1.0: o pgBackRest não roda no Windows. **Decisão:** `pg_basebackup` + arquivamento contínuo de WAL + **restic** (criptografado, com deduplicação, multiplataforma) enviando a um repositório S3 compatível. Mesmo procedimento e mesmas metas (RPO ≤ 15 min, RTO ≤ 4 h) nos dois sistemas.

### D-09 — Licenças de terceiros (produto que poderá ser vendido)
O MVP usa **PyMuPDF**, licenciado como **AGPL-3.0** (ou licença comercial paga). Distribuí-lo em produto fechado obrigaria a abrir o código ou comprar a licença. **Decisão:** usar `pypdfium2` (Apache-2.0/BSD) para renderizar PDF e `pdfminer.six` (MIT) para texto; manter Tesseract (Apache-2.0) para OCR. Toda dependência passa por verificação automática de licença no CI (ADR-016).

### D-10 — Estratégia de branch no mesmo repositório
| Alternativa | Avaliação |
|---|---|
| Branch criada a partir da `main` | Carrega todo o código e histórico do MVP, mistura estruturas e confunde CI e revisões |
| **Branch órfã `definitivo`** (`git switch --orphan definitivo`) | Histórico limpo, estrutura nova, sem arquivos do MVP; o MVP continua na `main` intocado |
| Repositório novo | Mais limpo ainda, mas o responsável pediu o mesmo repositório |

**Regras para a branch `definitivo`:**
- Proteção de branch: só entra por pull request com CI verde e revisão.
- Trabalho em branches curtas `feat/<ID>-<descricao>` saindo de `definitivo` e voltando para ela.
- Workflows de CI disparam só para `definitivo` e suas PRs; os da `main` não são afetados.
- Dependabot configurado com `target-branch: definitivo`.
- Tags com prefixo próprio (`app-v0.1.0`, …, `app-v1.0.0`) para não colidir com o MVP.
- No futuro, quando o MVP for aposentado, `definitivo` pode virar a branch padrão (decisão do responsável).

### D-11 — Forma de entrega: fatias verticais com marcos
Em vez de construir camada por camada, cada fase entrega **fluxos completos** (banco → API → tela responsiva → testes → instalado no notebook de homologação). Marcos:

| Marco | Conteúdo | Fases | Uso |
|---|---|---|---|
| **M0 — Fundação** | Decisões, protótipo, CI nos dois sistemas, instalador mínimo | 0–1 | Interno |
| **M1 — Alfa interno** | Login seguro, catálogo, estoque, empréstimos, QR básico | 2–6 | O laboratório testa em homologação, em paralelo ao MVP |
| **M2 — Beta** | Todas as funções obrigatórias, suporte em tempo real, relatórios, PWA completa | 7–8 | Piloto controlado no laboratório |
| **M3 — Candidato a release** | Plataforma do servidor, importação do MVP, qualidade e segurança finais | 9–11 | Ensaios de instalação, restauração e pentest |
| **M4 — 1.0 interna** | Piloto, documentação, suporte interno, aceite | 12 | Uso diário na Avante Tech Jr |
| **M5 — Pacote comercial** | Licenciamento, marca comercial, documentos jurídicos, onboarding de clientes | 13 | Venda (quando decidida) |

Tamanho relativo das fases (P/M/G/GG), sem datas: estimativas de calendário só depois da Fase 0, medindo o ritmo real.

| Fase | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tamanho | M | G | G | GG | G | G | G | G | G | GG | M | G | M | M |

## 3. Riscos principais e mitigação

| # | Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|---|
| R1 | Notebook-servidor desligado, suspenso, roubado ou com disco danificado | Média | Alto | Energia/tampa configuradas; disco criptografado; backup externo; restauração ensaiada; alerta de servidor fora do ar |
| R2 | HTTPS válido na rede local falhar (roteador bloqueia DNS para IP local) | Média | Alto (câmera não abre) | Spike no Gate 0; alternativas: VPN também na rede local, DNS local do roteador |
| R3 | Diferenças entre Windows e Linux gerarem defeitos só em um deles | Alta | Médio | CI nos dois; testes de instalação em VMs limpas dos dois a cada release |
| R4 | Escopo grande demais para o ritmo de desenvolvimento | Alta | Alto | Prioridades M/S/C; marcos com uso real; Should e Could podem ir para 1.x |
| R5 | Vulnerabilidade com servidor acessível de fora | Média | Alto | Sem porta aberta; MFA; ASVS L2; scans bloqueantes; pentest antes da 1.0 |
| R6 | Licença de dependência incompatível com venda | Média | Alto | Verificação de licenças no CI (ADR-016); PyMuPDF já substituído |
| R7 | Exigências legais (LGPD, contratos) | Média | Médio | Política de privacidade interna na Fase 12; documentos jurídicos de venda na Fase 13, **revisados por advogado** |
| R8 | Dependência de terceiros (DNS, VPN, S3) | Baixa | Médio | Provedores substituíveis; sem dado de negócio fora do cliente, exceto backup criptografado |
| R9 | Usuários não instalarem o app | Média | Médio | QR de conexão, instruções por plataforma na própria página, o app também funciona no navegador sem instalar |

## 4. Responsabilidades fora do código

Coisas que dependem de você (ou da empresa) e não podem ser feitas por mim:

| Item | Quando |
|---|---|
| Notebook de homologação com Linux **e** acesso a uma máquina Windows 11 para testes | Fase 0 |
| Registro do domínio do produto e conta no provedor de DNS | Fase 0 |
| Celulares (Android e iPhone) e um tablet para homologação | Fase 0 |
| Conta de armazenamento S3 compatível para backup externo | Fase 9 |
| Certificado de assinatura de código para Windows (Authenticode) e chave de assinatura dos pacotes `.deb` | Fase 9 |
| Política de privacidade interna da Avante | Fase 12 |
| Revisão jurídica para venda (termos de uso, contrato e DPA) | Fase 13 |
| Modelo comercial e preço | Fase 13 |
| Contas de desenvolvedor Google Play e Apple (só se a casca de loja for aprovada) | Pós-1.0 |
| Aprovar cada gate e dar autorização para commits/push na branch `definitivo` | Contínuo |

## 5. Rota recomendada (resumo)

1. Aprovar Plano v2.3, ADRs v1.3, Guia v2.3, a especificação de UI/UX, a estratégia de QR e esta análise.
2. Criar a branch órfã `definitivo` com a estrutura do monorepo e o CI em Linux e Windows (com sua autorização para o push).
3. Fase 0: spikes de rede/HTTPS/câmera e de hardware nos dois sistemas, protótipo navegável das telas-chave, modelo de ameaças.
4. Seguir os marcos M1 → M4, com a Avante usando o Alfa em paralelo ao MVP o quanto antes; o M5 (pacote comercial) só quando a venda for decidida.
5. Importar os dados do MVP só depois que o produto estiver estável (Fase 10), e aposentar o MVP quando você decidir.
