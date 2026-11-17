# Anexo A2 — Análise de Rota

**Produto:** Avante Almoxarifado · **Versão:** 3.0.0 · **Data:** 17/11/2026 (1.0 de 03/11/2026) · **Status:** Proposto — aguarda aprovação
**Pergunta:** qual é o melhor caminho para entregar um aplicativo de excelência para notebooks, celulares e tablets, com servidor num **notebook antigo** (DDR3, HD), acesso local e remoto, interação entre usuários, visão computacional e dispositivos embarcados, desenvolvido por **uma pessoa** e preparado para venda?
**Base:** diagnóstico do MVP, decisões do responsável de 03/11 e 17/11/2026 (Volume 00) e Volumes 01–12.

---

## 1. Requisitos que guiam a rota

1. Produto da **Avante Tech Jr**, instalado **localmente** em um computador (um por instalação), usado internamente e **preparado para venda** como gestão de estoque inteligente com visão computacional.
2. Servidor adaptável a **Linux e Windows**; na Avante, um notebook antigo (DDR3, HD) que não roda Windows 11.
3. Cerca de **30 pessoas com acesso**, não simultâneas; **um único desenvolvedor**, com o Claude Code como executor.
4. Usado como **aplicativo**: o usuário baixa/instala e interage com outros usuários (ex.: chamado de suporte que a equipe vê e responde).
5. Notebooks, celulares e tablets, **dentro e fora** da rede do cliente; servidor com internet.
6. Todas as funções do MVP preservadas e melhoradas (Anexo A1).
7. Segurança, robustez e qualidade comprováveis.
8. MVP continua operando; código novo em **outra branch do mesmo repositório**.

## 2. Decisões de rota

Cada decisão compara as alternativas reais; a escolhida está em **negrito**.

### D-01 — Base de código
| Alternativa | Avaliação |
|---|---|
| Evoluir o MVP no lugar | O modelo de dados (item = catálogo + unidade) e os defeitos estruturais exigiriam reescrever quase tudo, carregando dívidas (migrations quebradas, testes desatualizados) |
| **Código novo, sem nenhum trecho do MVP; só o conhecimento das funções e dos defeitos é aproveitado** | Domínio correto desde o início; nenhum defeito herdado; MVP intocado; exige importador de dados |

### D-02 — Forma do aplicativo
| Alternativa | Celular/tablet | Notebook | Custo e risco |
|---|---|---|---|
| **PWA (aplicativo web instalável)** | Instala pela tela inicial (Android; iPhone/iPad pelo Safari) | Instala pelo Chrome/Edge no Windows, Linux e macOS | Um código só; atualização instantânea; sem taxa de loja |
| Casca Capacitor (PWA empacotada para lojas) | Play Store e App Store | — | +1 build por loja; revisão da Apple; contas de desenvolvedor pagas |
| Apps nativos (Kotlin/Swift) ou Flutter | Ótimo acesso ao hardware | Exige outra solução | 2–3 bases de código; não se justifica para este domínio |
| Electron | — | App de desktop | Grande, mais uma superfície de ataque; o navegador já basta |

**Decisão:** **PWA desde a R1** em todas as plataformas. Isso atende "baixar e usar": o usuário instala o app a partir do endereço da organização (ou escaneando o QR de conexão) e ele abre como aplicativo, com ícone, tela cheia e notificações. **Depois da 1.0**, uma casca Capacitor publicada como "Avante Almoxarifado" na Play Store e na App Store, com tela "Conectar à organização" (escaneando o QR de conexão), se o mercado pedir presença em loja.

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
| **Instalação nativa por sistema, com camada de plataforma comum; Linux primeiro (R0–R3), Windows na R4** | Mesmo código; diferenças isoladas em `platform/` e `packaging/`; testes da camada de plataforma em Windows desde a R0 evitam surpresas; a Avante recebe valor sem esperar o Windows |
| Linux e Windows completos desde a R1 | Dobra empacotamento, testes de instalação e documentação antes de qualquer uso real, com um único desenvolvedor; o notebook da Avante nem roda Windows 11. Descartado |
| Docker Desktop no Windows / VM Linux no Windows | Pesados para hardware modesto e frágeis em notebook. Descartados |

Matriz de suporte e diferenças por sistema: ADR-002 e ADR-022 (Volume 03). Windows 10 não é suportado (fim do suporte em 14/10/2025).

### D-07 — Acesso de dentro e de fora da rede
Mantida a ADR-007: certificado válido emitido por DNS-01 (sem porta aberta), rede local direta, acesso externo por **VPN WireGuard (padrão)** ou **túnel (alternativa)**, decidido na validação de rede da R0 (tarefa R0-07). Funciona igual em Windows e Linux.

### D-08 — Backup
Troca em relação à ADR-012 v1.0: o pgBackRest não roda no Windows. **Decisão:** `pg_basebackup` + arquivamento contínuo de WAL + **restic** (criptografado, com deduplicação, multiplataforma) enviando a um repositório S3 compatível. Mesmo procedimento e mesmas metas (RPO ≤ 15 min, RTO ≤ 4 h) nos dois sistemas.

### D-09 — Licenças de terceiros (produto que poderá ser vendido)
O MVP usa **PyMuPDF**, licenciado como **AGPL-3.0** (ou licença comercial paga). Distribuí-lo em produto fechado obrigaria a abrir o código ou comprar a licença. **Decisão:** usar `pypdfium2` (Apache-2.0/BSD) para renderizar PDF e `pdfminer.six` (MIT) para texto; manter Tesseract (Apache-2.0) para OCR. Toda dependência, modelo de visão e componente de firmware passa por verificação de licença (ADR-016); modelos AGPL (ex.: Ultralytics YOLO) também ficam de fora.

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
- Tags com prefixo próprio (`app-v0.1.0`, …) para não colidir com o MVP.
- No futuro, quando o MVP for aposentado, `definitivo` pode virar a branch padrão (decisão do responsável).

### D-11 — Forma de entrega: releases incrementais
Fatias verticais (banco → API → tela → testes → instalado) organizadas em releases que entregam valor real (ADR-026; Volume 12):

| Release | Conteúdo | Uso |
|---|---|---|
| R0 — Fundação | Hardware e rede validados, design aprovado no Claude Design, base técnica, instalador mínimo | Homologação |
| R1 — Núcleo | Estoque com ledger, empréstimos, QR, segurança, suporte, notificações | Uso real em paralelo ao MVP |
| R2 — Completo | Paridade total com o MVP e além; importação do MVP | MVP aposentado |
| R3 — Inteligente | Visão computacional, leitor de cartão no balcão, automação | Balcão automatizado |
| R4 — Comercial | Windows, licença, importação de planilhas, exportação, Estação Avante, conformidade | Venda |

Prazo: estimado só depois da calibração de capacidade da R0 (Volume 12 §2).

### D-12 — Hardware modesto como requisito, não como problema
| Alternativa | Avaliação |
|---|---|
| **Orçamento de recursos explícito (≤ 1,5 GB normal), PostgreSQL ajustado para HD, trabalho pesado fora do horário e no aparelho do usuário** | Cabe com folga em 4 GB; comprovado por teste de carga no próprio notebook antes de qualquer funcionalidade (R0-05) |
| Exigir hardware novo | Contraria a realidade da Avante e encarece a venda. Mantido só como melhoria recomendada (SSD, 8 GB) |

### D-13 — Onde roda a visão computacional
| Alternativa | Avaliação |
|---|---|
| **No aparelho (navegador com ONNX Runtime Web/OpenCV.js) e na Estação Avante** | Servidor continua leve; funciona sem internet; imagem não precisa trafegar; escala com o número de aparelhos |
| No servidor | Um notebook com 4 GB e 2 núcleos não aguenta inferência concorrente sem prejudicar o restante. Descartado |
| Na nuvem | Custo recorrente, dependência externa e dados fora do cliente. Descartado |

### D-14 — Integração dos dispositivos embarcados
| Alternativa | Avaliação |
|---|---|
| **HTTPS com credencial por dispositivo, direto na API** | Um protocolo só, mesma autenticação, auditoria e TLS; nada a mais rodando no servidor |
| Broker MQTT | Mais um serviço consumindo memória e exigindo segurança própria, sem ganho para o volume de eventos de um balcão. Descartado |

### D-15 — Desenvolvimento por uma pessoa com o Claude Code
**Decisão:** o responsável planeja, aprova designs e aceita entregas; o Claude Code implementa seguindo `CLAUDE.md` e o Volume 13 (limites, autorrevisão, revisor independente, relatórios com evidência real). Travas de permissão em `.claude/settings.json` impedem push e ações destrutivas. WIP = 1.

## 3. Riscos principais e mitigação

Lista viva no Volume 12 §4. Os decisivos para a rota:

| # | Risco | Mitigação na rota |
|---|---|---|
| R1 | Notebook não aguentar | Teste de carga no próprio notebook na R0, antes de qualquer funcionalidade |
| R2 | HD falhar | SMART, backup externo com RPO de 15 min, restauração testada (Volume 10) |
| R3 | HTTPS na rede local falhar (câmera não abre) | Validação na R0 com VPN e DNS local como alternativas |
| R4 | Escopo grande para uma pessoa | Releases úteis, WIP = 1, Claude Code como executor, calibração de capacidade |
| R5 | Visão computacional abaixo da meta | Visão clássica primeiro; recurso desativado se não atingir; o produto vale sem ele |
| R6 | Exigências legais para vender (forma jurídica, LGPD, Anatel) | Volume 11 §7 resolvido antes da R4 |

## 4. Responsabilidades fora do código

| Item | Quando |
|---|---|
| Acesso físico ao notebook e configuração da BIOS | R0 |
| Domínio do produto e conta no provedor de DNS | R0 |
| Celulares (Android e iPhone) e um tablet para homologação | R0 |
| Conta de armazenamento S3 compatível para backup externo e guarda da chave | R0 |
| Participantes das entrevistas e testes de usabilidade (membros da Avante) | R0 em diante |
| Aprovar designs no Claude Design e aceitar cada entrega | Contínuo |
| Administrador substituto treinado | R1 |
| Leitor de cartão (ESP32 com módulo homologado + leitor 13,56 MHz) | R3 |
| Máquina Windows 11 para testes; certificados de assinatura de código | R4 |
| Forma jurídica da venda, propriedade intelectual, revisão jurídica, análise Anatel, preço | Antes da R4 |
| Autorizar commits e push na branch `definitivo` | Contínuo |

## 5. Rota recomendada (resumo)

1. Aprovar os Volumes 00–13 e os anexos (v3.0.0).
2. R0: provar o notebook (hardware, carga, energia), a rede e a câmera; desenhar e testar o protótipo no Claude Design; construir a fundação técnica com o Claude Code.
3. R1: colocar o núcleo em uso real em paralelo ao MVP o quanto antes.
4. R2: completar a paridade, importar os dados e aposentar o MVP.
5. R3: diferenciar com visão computacional, leitor de cartão e automação.
6. R4: só quando a venda for decidida — Windows, licença, implantação em cliente, Estação Avante e conformidade.
