# Plano Mestre de Desenvolvimento — Avante Almoxarifado (Produto Definitivo)

**Versão:** 2.3 — substitui as versões 2.2, 2.1, 2.0 e 1.0 (03/11/2026)
**Data:** 03/11/2026
**Escopo:** aplicativo completo, **Avante Almoxarifado**, da **Avante Tech Jr**, para uso interno na 1.0 e preparado para venda futura. Servidor instalado em um notebook por cliente, com **Linux ou Windows**. Usado como aplicativo em notebooks, celulares e tablets, dentro e fora da rede local, com interação entre usuários.
**Branch:** `definitivo` (órfã) do mesmo repositório do MVP; a `main` permanece com o MVP.
**Documentos do conjunto (obrigatórios):**
| Documento | Papel |
|---|---|
| `PLANO_MESTRE_DESENVOLVIMENTO.md` (este) | O quê: requisitos, metas, fases e gates |
| `ARQUITETURA_E_DECISOES.md` v1.3 | Como: arquitetura e ADRs |
| `ESPECIFICACAO_UI_UX.md` | Experiência, interface, interação e design system |
| `GUIA_EXECUCAO_CLAUDE.md` v2.3 | Regras de execução |
| `ESTRATEGIA_QR_CODE.md` | Propósito e uso do QR |
| `MATRIZ_FUNCIONALIDADES_MVP.md` | Preservação de cada função do MVP |
| `ANALISE_DE_ROTA.md` | Alternativas avaliadas e rota escolhida |
| `RELATORIO_AUDITORIA_BASELINE_2026-11-03.md` | Diagnóstico do MVP — **documento interno, mantido fora do repositório** (os IDs citados no §9 vêm dele) |

**Histórico de versões:**
- 2.0 — produto definitivo: repositório novo, servidor Linux, acesso remoto, requisitos comerciais e metas mensuráveis.
- 2.1 — servidor Linux **e** Windows; branch `definitivo`; experiência de aplicativo instalável; interação em tempo real; suporte completo; matriz de preservação do MVP; nova estratégia de QR; licenças de terceiros.
- 2.2 — especificação completa de UI/UX e design system; metas de desempenho percebido (RNF-18) e de usabilidade (RNF-19); pesquisa com usuários e protótipo testado na Fase 0; design system na Fase 1; Definição de Pronto de UI.
- 2.3 — produto da Avante Tech Jr com 1.0 interna e pacote comercial em fase própria (Fase 13); logo da Avante Tech Jr; membros da Avante nos testes de usuário; versões de plataforma atualizadas (Ubuntu 26.04/24.04, Debian 13, Windows 11 25H2+, PostgreSQL 18, Python 3.14); marca centralizada (RF-APP-09).

---

## 0. Avaliação dos documentos originais (v1.0)

A v1.0 foi escrita para **evoluir o MVP no lugar**. O objetivo definido pelo responsável do produto em 03/11/2026 é outro:
- o **MVP continua operando** no computador do responsável, intocado;
- o **produto definitivo** é um aplicativo novo e completo, o **Avante Almoxarifado**, usado primeiro pela **Avante Tech Jr** e preparado para ser **vendido no futuro** (com outro nome, se for o caso);
- servidor em **notebook com Linux ou Windows**, um por instalação (instalação local), **com internet**;
- acesso **pela rede local e pela internet**;
- usuários **instalam o app** e interagem entre si (ex.: suporte);
- **todas as funções do MVP** preservadas e melhoradas.

### 0.1 Preservado da v1.0
Princípios (dados acima de velocidade, fonte de verdade, sem conclusão por declaração, segurança por padrão, operação simples, multiplataforma real, centralização, rastreabilidade); separação catálogo/unidade/movimentação; modos UNITARIO/QUANTITATIVO; estados explícitos; QR opaco e versionado que nunca cria patrimônio silenciosamente; NF-e XML como fonte prioritária e PDF/OCR nunca como validação fiscal; worker separado com outbox; PWA sem Electron; fases com gates PASS/HOLD/FAIL; plano mínimo de testes.

### 0.2 Adaptado
| Lacuna/conflito da v1.0 | Adaptação |
|---|---|
| Evoluir e migrar o banco em uso | Código novo na branch `definitivo`; MVP intocado; dados entram por importador a partir de dump (Fase 10) |
| Fase 0 dedicada a consertar o MVP | Correções do MVP saem do caminho crítico (§11) |
| Hospedagem "a decidir" | Linux e Windows, instalação local, acesso local e remoto (ADR-002, ADR-007) |
| Sem dimensão de produto | Onboarding, atualização assinada, suporte, LGPD e documentação na 1.0 interna (Fase 12); licenciamento, marca comercial e documentos jurídicos de venda no pacote comercial (Fase 13) |
| MFA opcional | Obrigatório para papéis privilegiados |
| Sem metas mensuráveis | Requisitos não funcionais com metas (§5) e definição de pronto (§10) |
| Sem plano de desastre | Criptografia de disco, backup externo, RPO/RTO, restauração ensaiada |
| Setores e regras fixos no código | Organização, setores, locais e **políticas configuráveis** |
| QR como contador de estoque | QR como **identidade física** com ações contextuais (`ESTRATEGIA_QR_CODE.md`) |
| Sem interação em tempo real | Eventos em tempo real e push (RF-APP, RF-SUP, RF-COL) |
| Sem análise de licenças | PyMuPDF (AGPL) substituído; verificação de licenças no CI (ADR-016) |

### 0.3 Conclusão
A v1.0 acerta no domínio e na governança, mas **não propunha o almoxarifado definitivo**. Esta versão mantém o que estava correto e acrescenta o que falta.

### 0.4 Sobre "impecável"
Nenhum software é perfeito. Aqui, "impecável" é verificável: **todo requisito tem critério de aceite testável, todo gate exige evidência executada, e nenhuma falha alta ou crítica conhecida é aceita sem exceção formal aprovada**.

---

## 1. Visão do produto

O Avante Almoxarifado é um aplicativo de gestão de almoxarifado, patrimônio e empréstimos para laboratórios e organizações técnicas. Ele garante que **cada material tenha identidade, localização, saldo, responsável e histórico confiáveis**, com operação em segundos pelo celular (QR Code) e controle completo pelo notebook.

**Primeiro usuário:** a própria **Avante Tech Jr**, que usará a 1.0 no seu laboratório (servidor em um notebook da Avante). **Mercado futuro**, quando a venda for decidida: laboratórios de pesquisa e ensino, empresas de engenharia e tecnologia, oficinas e makerspaces, com 1 a 3 almoxarifados e até algumas centenas de usuários por instalação.

**Proposta de valor:**
1. Inventário confiável: saldo derivado de movimentações imutáveis e auditáveis.
2. Operação em segundos: escanear, confirmar, pronto — no celular, no tablet ou no notebook.
3. Aplicativo de verdade: instala no aparelho, avisa em tempo real, conversa com a equipe.
4. Dados sob controle do cliente: servidor no cliente, Linux ou Windows, backup criptografado que só ele lê.
5. Segurança profissional mesmo com acesso pela internet.

### 1.1 Experiência de aplicativo
- O usuário recebe um convite (e-mail) ou escaneia o **QR de conexão** no cartaz do laboratório → abre a página da organização → entra → toca em "Instalar aplicativo". O app aparece na tela inicial (celular/tablet) ou no menu de aplicativos (notebook), abre em tela cheia e recebe notificações.
- Sem instalar, tudo funciona igual no navegador.
- Atualizações chegam sozinhas: ao publicar uma versão no servidor, o app avisa "nova versão disponível" e recarrega sem perder o que o usuário estava fazendo.

## 2. Princípios não negociáveis

1. **Dados acima de velocidade.** Nenhuma operação destrutiva sem backup restaurável, ensaio e rollback.
2. **Fonte de verdade.** Código, migrations, testes e execução prevalecem sobre documentação.
3. **Sem conclusão por declaração.** Pronto só com evidência reproduzível.
4. **Saldo nunca é editado; é consequência de movimentações.**
5. **Segurança por padrão e por projeto.** Mínimo privilégio, MFA para privilégios, segredos fora do Git, validação no servidor, auditoria imutável, nenhuma porta exposta sem necessidade.
6. **Privacidade (LGPD).** Mínimo de dados pessoais, finalidade declarada, retenção definida, direitos do titular atendíveis.
7. **Operação simples.** Instalar, atualizar, fazer backup e restaurar com comandos iguais em Linux e Windows, executáveis por um técnico sem o desenvolvedor.
8. **Multiplataforma real.** Servidor homologado em Linux e Windows; app homologado em notebook, Android, iPhone e tablet reais.
9. **Centralização.** Um servidor e um banco por cliente; todos os aparelhos veem os mesmos dados.
10. **Compatibilidade.** Mudanças de API, schema e etiquetas têm plano de transição.
11. **MVP intocado.** Nada no MVP é alterado; dados só por cópia (dump).
12. **Nada do MVP se perde.** Toda função listada em `MATRIZ_FUNCIONALIDADES_MVP.md` existe no produto, melhorada.
13. **Rastreabilidade.** Requisito → teste → evidência.

## 3. Atores e papéis

| Papel | Descrição | Exemplos de permissão |
|---|---|---|
| **Proprietário da instalação** | Responsável técnico do cliente | Configuração do servidor, backup, licença, papéis administrativos |
| **Administrador** | Gestão completa da organização | Usuários, papéis, políticas, todos os almoxarifados |
| **Gestor de almoxarifado** | Responsável por um ou mais almoxarifados | Aprovar empréstimos, ajustes, inventário e baixas no escopo |
| **Operador** | Equipe do balcão | Entradas, saídas, retiradas e devoluções no escopo |
| **Atendente de suporte** | Equipe que atende chamados | Fila de chamados, respostas, notas internas, atribuição |
| **Solicitante** | Membro comum | Catálogo, empréstimos, reservas, chamados próprios |
| **Auditor** | Somente leitura | Relatórios, histórico e trilha de auditoria |

Permissões granulares (ex.: `estoque.ajustar`, `emprestimo.aprovar`, `suporte.atender`); papéis são conjuntos de permissões com **escopo por almoxarifado**; uma pessoa pode ter vários papéis; papéis personalizados são Should.

## 4. Requisitos funcionais

Prioridade: **M** = obrigatório na 1.0 · **S** = desejável na 1.0 · **C** = pós-1.0.

### 4.1 Identidade, acesso e sessão (IAM)
| ID | Requisito | Prior. |
|---|---|---|
| RF-IAM-01 | Login com usuário ou e-mail e senha; Argon2id; senha mínima de 10 caracteres, medidor de força, checagem contra senhas vazadas (lista local) | M |
| RF-IAM-02 | Sessões no servidor (token opaco, revogável, vinculado ao ID interno), expiração por inatividade e absoluta configuráveis | M |
| RF-IAM-03 | Troca de senha, desativação, mudança de papel e "sair de todos os dispositivos" encerram as sessões afetadas na hora | M |
| RF-IAM-04 | MFA TOTP com códigos de recuperação; **obrigatório** para Proprietário, Administrador, Gestor e Atendente | M |
| RF-IAM-05 | Passkeys (WebAuthn) como fator ou login sem senha | S |
| RF-IAM-06 | Recuperação de senha por e-mail com token de uso único e curta duração; administrador pode **enviar** link de redefinição, nunca definir a senha | M |
| RF-IAM-07 | Bloqueio progressivo e rate limiting por conta e por IP | M |
| RF-IAM-08 | Cadastro por convite (padrão); autocadastro opcional por política, com domínio de e-mail permitido e aprovação | M |
| RF-IAM-09 | Lista de dispositivos/sessões ativos do usuário, com encerramento remoto | M |
| RF-IAM-10 | RBAC granular com escopo; papéis padrão; invariante "sempre existe um Proprietário ativo com MFA"; papéis personalizados | M / S |
| RF-IAM-11 | Perfil: nome, e-mail, setor (troca livre ou com aprovação, por política), foto com recorte e zoom no aparelho, preferências de notificação, idioma, tema | M |
| RF-IAM-12 | Quem tem histórico nunca é apagado: anonimização (LGPD); exclusão bloqueada com empréstimo em aberto | M |
| RF-IAM-13 | Titular pode solicitar encerramento da própria conta e exportação dos seus dados (LGPD), com a proteção do último Proprietário | M |

### 4.2 Organização e estrutura (ORG)
| ID | Requisito | Prior. |
|---|---|---|
| RF-ORG-01 | Dados da organização (nome, CNPJ opcional, logotipo e cores da marca, fuso horário, idioma) | M |
| RF-ORG-02 | Setores/departamentos configuráveis, desativáveis sem perder histórico | M |
| RF-ORG-03 | Múltiplos almoxarifados por instalação | M |
| RF-ORG-04 | Localizações hierárquicas (prédio › sala › armário › prateleira › gaveta) com etiqueta QR própria | M |
| RF-ORG-05 | Assistente de configuração inicial no primeiro acesso | M |

### 4.3 Catálogo (CAT)
| ID | Requisito | Prior. |
|---|---|---|
| RF-CAT-01 | Item: nome, descrição, categoria, fabricante, modelo, part number, unidade de medida, fotos, anexos (datasheet), campos técnicos, códigos de barras do fabricante (EAN/GTIN) | M |
| RF-CAT-02 | Modo de controle: **UNITARIO**, **QUANTITATIVO** e **LOTE** (com validade) | M |
| RF-CAT-03 | Estoque mínimo e ponto de reposição por item e almoxarifado | M |
| RF-CAT-04 | Categorias hierárquicas e fabricantes | M |
| RF-CAT-05 | Unidades de medida com casas decimais; quantidades fracionárias exatas, sem arredondamento | M |
| RF-CAT-06 | Busca no servidor, insensível a acentos, por nome, código, patrimônio, part number, QR e código de barras; filtros por categoria, local, estado, setor e disponibilidade; ordenação; paginação; filtros salvos | M |
| RF-CAT-07 | Itens "emprestáveis" × "somente consumo" | M |
| RF-CAT-08 | Campos personalizados por categoria | S |

### 4.4 Unidades físicas e saldos (INV)
| ID | Requisito | Prior. |
|---|---|---|
| RF-INV-01 | Unidade física com identificador imutável, nº de patrimônio, nº de série, local, estado e responsável atual | M |
| RF-INV-02 | Estados com transições validadas: DISPONIVEL, RESERVADO, EMPRESTADO, EM_MANUTENCAO, EM_CONFERENCIA, PERDIDO, BAIXADO | M |
| RF-INV-03 | Saldo por item × almoxarifado × local (× lote), sempre derivado das movimentações | M |
| RF-INV-04 | Saldo nunca negativo, garantido no banco e no serviço | M |
| RF-INV-05 | Histórico completo por item, unidade, local, usuário e período | M |
| RF-INV-06 | Kits: conjunto de unidades emprestado como um todo, com checklist de componentes | S |

### 4.5 Movimentações (MOV)
| ID | Requisito | Prior. |
|---|---|---|
| RF-MOV-01 | Entrada: compra (NF-e), doação, devolução de terceiros, ajuste positivo, cadastro inicial | M |
| RF-MOV-02 | Saída: consumo, baixa (motivo obrigatório), perda, ajuste negativo, envio para manutenção | M |
| RF-MOV-03 | Transferência entre locais e entre almoxarifados (com confirmação de recebimento opcional) | M |
| RF-MOV-04 | Toda movimentação registra operador, data/hora UTC, origem, destino, quantidade, motivo, referência e dispositivo | M |
| RF-MOV-05 | Movimentações imutáveis; correção por estorno | M |
| RF-MOV-06 | Operações atômicas e idempotentes (`Idempotency-Key`); concorrência sem saldo negativo nem duplicidade | M |
| RF-MOV-07 | Ajustes acima de limite configurável exigem aprovação de gestor | S |

### 4.6 Empréstimos e reservas (EMP)
| ID | Requisito | Prior. |
|---|---|---|
| RF-EMP-01 | Solicitação com carrinho de várias unidades/quantidades e prazo | M |
| RF-EMP-02 | Política: aprovação obrigatória/automática por categoria, prazo máximo, tolerância, limite por usuário | M |
| RF-EMP-03 | Retirada registrada pelo operador (escaneando) ou autoatendimento se a política permitir; operador pode registrar em nome de alguém, ficando registrado quem operou | M |
| RF-EMP-04 | Devolução total ou parcial; conferência pelo operador configurável (o fluxo em duas etapas do MVP é o padrão) | M |
| RF-EMP-05 | Devolução com ocorrência (dano, falta, perda), com fotos e encaminhamento | M |
| RF-EMP-06 | Renovação com regras (máximo de renovações; bloqueio se houver reserva) | M |
| RF-EMP-07 | Atraso calculado em UTC com fuso da organização; pendências de conferência também contam prazo; escalonamento ao gestor após N dias | M |
| RF-EMP-08 | Reservas com data futura e detecção de conflito; fila de espera para unidade emprestada | S |
| RF-EMP-09 | Termo de responsabilidade aceito digitalmente na retirada | S |
| RF-EMP-10 | Empréstimo a pessoa externa (sem conta) com dados mínimos | C |

### 4.7 QR Code, etiquetas e leitura (QR) — detalhado em `ESTRATEGIA_QR_CODE.md`
| ID | Requisito | Prior. |
|---|---|---|
| RF-QR-01 | Etiquetas de unidade, localização, item a granel, lote, kit e conexão; conteúdo = URL com código opaco de 80 bits + verificador; sem dados pessoais ou de negócio | M (kit: S) |
| RF-QR-02 | Decodificação no aparelho (BarcodeDetector + zxing-wasm); servidor recebe só o código | M |
| RF-QR-03 | Digitação do código curto com verificador; leitores USB/Bluetooth em modo teclado em qualquer tela | M |
| RF-QR-04 | Leitura abre a ficha do objeto com ações contextuais por tipo, estado e papel; **nada muda sem confirmação** | M |
| RF-QR-05 | Código desconhecido → cadastro assistido (vincular ou criar); nunca criação silenciosa | M |
| RF-QR-06 | Idempotência no servidor; repetição na mesma sessão sinalizada, não somada | M |
| RF-QR-07 | Impressão em lote: A4 (modelos padrão Pimaco) e térmica, com teste automático de legibilidade do PDF gerado | M |
| RF-QR-08 | Revogar/substituir etiqueta mantendo histórico; aviso ao escanear etiqueta revogada | M |
| RF-QR-09 | Etiquetas do MVP reconhecidas via tabela de mapeamento, com relatório de reetiquetagem | M |
| RF-QR-10 | Modos em sequência: carrinho de retirada, devolução em lote, recebimento, guardar/transferir, inventário, vincular etiquetas; lista com desfazer antes de confirmar | M |
| RF-QR-11 | Etiquetas pré-impressas ("virgens") vinculáveis depois | M |
| RF-QR-12 | Leitura de códigos de barras do fabricante (EAN/GTIN, Code 128) para localizar/sugerir item | S |
| RF-QR-13 | Modo balcão (tablet/notebook fixo): tela permanente de leitura, bloqueio por inatividade | S |
| RF-QR-14 | QR de conexão para cartaz/convite, que leva à instalação do app | M |

### 4.8 Documentos fiscais e compras (DOC)
| ID | Requisito | Prior. |
|---|---|---|
| RF-DOC-01 | NF-e XML processada no servidor com parser seguro (sem entidades externas): chave, emitente, itens, quantidades, unidades, valores | M |
| RF-DOC-02 | Deduplicação pela chave de acesso | M |
| RF-DOC-03 | Rascunho de entrada editável: mapear cada linha a um item de catálogo (existente ou novo), corrigir quantidade, unidade e fator de conversão, escolher local | M |
| RF-DOC-04 | Confirmação atômica (tudo ou nada) gera as movimentações e vincula a nota a elas | M |
| RF-DOC-05 | Memória de mapeamento fornecedor + código → item | S |
| RF-DOC-06 | PDF/DANFE: leitura da chave e extração assistida no worker, com OCR, sempre "não verificada" | S |
| RF-DOC-07 | Fornecedores; anexos de documentos visualizáveis (PDF, imagem) | M |
| RF-DOC-08 | Aviso explícito: o sistema não valida autenticidade fiscal na SEFAZ | M |

### 4.9 Inventário físico (CNT)
| ID | Requisito | Prior. |
|---|---|---|
| RF-CNT-01 | Abrir inventário por almoxarifado/local, congelando o saldo de referência | M |
| RF-CNT-02 | Contagem por QR ou digitação, em vários aparelhos ao mesmo tempo | M |
| RF-CNT-03 | Divergências e ajustes de conciliação com aprovação | M |
| RF-CNT-04 | Inventário cíclico agendado | C |

### 4.10 Políticas configuráveis (POL)
| ID | Requisito | Padrão seguro | Prior. |
|---|---|---|---|
| RF-POL-01 | Autocadastro | Desligado (só convite) | M |
| RF-POL-02 | Aprovação de empréstimos | Obrigatória para UNITARIO | M |
| RF-POL-03 | Conferência de devolução pelo operador | Ligada | M |
| RF-POL-04 | Prazo máximo e tolerância | 30 dias / 1 dia | M |
| RF-POL-05 | Sessão (inatividade/absoluta) | 30 min / 12 h | M |
| RF-POL-06 | MFA por papel | Obrigatório para privilegiados (não desligável) | M |
| RF-POL-07 | Troca do próprio setor | Livre | M |

### 4.11 Experiência de aplicativo e tempo real (APP)
| ID | Requisito | Prior. |
|---|---|---|
| RF-APP-01 | Instalável como PWA em Android, iPhone/iPad, Windows, Linux e macOS, com ícone, tela cheia e página "Instalar" com instruções por plataforma | M |
| RF-APP-02 | Atualização do app sem cache obsoleto: aviso de nova versão e recarga sem perder dados em edição | M |
| RF-APP-03 | Eventos em tempo real (SSE): novas mensagens, aprovações, devoluções, alertas e mudanças de saldo aparecem sem atualizar a tela | M |
| RF-APP-04 | Leitura offline: catálogo, meus empréstimos e fichas visitadas ficam disponíveis sem conexão, com indicação clara; ações exigem conexão | M |
| RF-APP-05 | Indicador de conexão (online/offline/reconectando) | M |
| RF-APP-06 | Navegação por papel: barra inferior + botão "Escanear" no celular; menu lateral com busca e paleta de comandos (Ctrl+K) no notebook; atalhos de tarefas frequentes | M |
| RF-APP-07 | Tema claro/escuro e marca do cliente (logotipo/cores) | M |
| RF-APP-08 | Publicação em lojas (Play Store/App Store) por casca Capacitor com "Conectar à organização" | C |
| RF-APP-09 | Marca do produto centralizada: nome ("Avante Almoxarifado"), logotipo, ícones, cores e textos de marca definidos em um único ponto de configuração e nos tokens, para que a troca de marca na venda não exija mudar código | M |

### 4.12 Notificações (NOT)
| ID | Requisito | Prior. |
|---|---|---|
| RF-NOT-01 | Central de notificações no app, com lidas/não lidas | M |
| RF-NOT-02 | E-mail transacional: convite, recuperação de senha, aprovação, lembrete, atraso, estoque mínimo, resposta de chamado | M |
| RF-NOT-03 | Web Push com o app fechado (Android, desktop; iPhone com app instalado) | M |
| RF-NOT-04 | Preferências por usuário e canal; lembretes configuráveis (ex.: 3 dias e 1 dia antes); atraso no máximo 1×/dia; nunca duplicadas (outbox + deduplicação) | M |
| RF-NOT-05 | Envio pelo worker, com retry exponencial e registro de falha sem dados sensíveis | M |
| RF-NOT-06 | "Novidades do catálogo": resumo opcional diário/semanal de itens novos (substitui o e-mail a todos por item do MVP) | S |

### 4.13 Suporte (SUP) — interação entre usuários e equipe
| ID | Requisito | Prior. |
|---|---|---|
| RF-SUP-01 | Qualquer usuário abre chamado com assunto, descrição, categoria e prioridade sugerida | M |
| RF-SUP-02 | Vínculo opcional a item, unidade, local ou empréstimo (aberto a partir da ficha ou de uma leitura de QR) | M |
| RF-SUP-03 | Conversa em tempo real entre solicitante e equipe, com nome, foto, horário e indicador de leitura | M |
| RF-SUP-04 | Anexos: imagens (comprimidas no aparelho) e PDF, com limites por arquivo e por chamado | M |
| RF-SUP-05 | Notas internas visíveis só para a equipe de suporte | M |
| RF-SUP-06 | Ciclo: Aberto → Em atendimento → Aguardando usuário → Resolvido → Fechado, com reabertura; o solicitante confirma a resolução ou informa "ainda não resolvido" (do MVP) | M |
| RF-SUP-07 | Fila da equipe: filtros, atribuição a atendente, prioridade, separação ativos × concluídos | M |
| RF-SUP-08 | Prazos de primeira resposta e de resolução (SLA) configuráveis, com alerta; respostas prontas | S |
| RF-SUP-09 | Avaliação do atendimento ao fechar | S |
| RF-SUP-10 | Notificação ao solicitante e à equipe em cada mudança (app, push, e-mail conforme preferência) | M |

### 4.14 Colaboração em processos (COL)
| ID | Requisito | Prior. |
|---|---|---|
| RF-COL-01 | Comentários em empréstimos, solicitações e reservas entre solicitante e almoxarifado, em tempo real | M |
| RF-COL-02 | Comentários internos da equipe em itens, unidades e inventários | S |

### 4.15 Relatórios, painéis e exportação (REL)
| ID | Requisito | Prior. |
|---|---|---|
| RF-REL-01 | Painel por papel: saldos, abaixo do mínimo, empréstimos ativos/atrasados, chamados abertos, movimentações recentes, saúde do estoque | M |
| RF-REL-02 | Relatórios: posição de estoque, movimentações, histórico por item/usuário/setor, empréstimos, inventários, perdas e baixas, chamados | M |
| RF-REL-03 | Exportação CSV e XLSX; PDF para posição e termo | M |
| RF-REL-04 | Exportações auditadas e restritas por permissão | M |

### 4.16 Auditoria (AUD)
| ID | Requisito | Prior. |
|---|---|---|
| RF-AUD-01 | Trilha imutável de ações de negócio e de segurança (quem, o quê, quando, de onde, resultado, antes/depois) | M |
| RF-AUD-02 | Encadeamento por hash e permissões de banco que impedem UPDATE/DELETE | M |
| RF-AUD-03 | Consulta com filtros por Auditor e Administrador | M |

### 4.17 Administração da instalação (ADM)
| ID | Requisito | Prior. |
|---|---|---|
| RF-ADM-01 | Página de saúde: versão, sistema operacional, banco, disco, último backup e último teste de restauração, validade do certificado, fila de jobs | M |
| RF-ADM-02 | SMTP (com envio de teste), domínio e acesso remoto configuráveis pelo app ou pela CLI | M |
| RF-ADM-03 | Backup sob demanda e status dos automáticos | M |
| RF-ADM-04 | Licença: ver, instalar, renovar (só no pacote comercial, Fase 13) | C |
| RF-ADM-05 | Atualização: aviso de nova versão e notas; aplicação pela CLI `avante update` (igual em Linux e Windows) | M |
| RF-ADM-06 | CLI `avante` com os mesmos comandos nos dois sistemas: `status`, `doctor`, `backup`, `restore`, `update`, `rollback`, `support-bundle` (sem dados pessoais) | M |

### 4.18 Importação do MVP (IMP)
| ID | Requisito | Prior. |
|---|---|---|
| RF-IMP-01 | Importador a partir de dump do MVP restaurado em banco temporário; nunca conecta ao banco em uso | M |
| RF-IMP-02 | Preflight com relatório: contagens, inconsistências, fuso das datas (AUD-002) | M |
| RF-IMP-03 | Classificação assistida UNITARIO/QUANTITATIVO; unidades provisórias marcadas para conferência | M |
| RF-IMP-04 | Empréstimos abertos, usuários, setores, chamados, notas fiscais e fotos preservados; reconciliação sem descarte silencioso | M |
| RF-IMP-05 | Mapeamento das etiquetas antigas (RF-QR-09) | M |

## 5. Requisitos não funcionais (metas mensuráveis)

† = meta inicial, confirmada ou revisada com medição no hardware real na Fase 0.

| ID | Categoria | Requisito / meta |
|---|---|---|
| RNF-01 | Plataformas do app | Chrome/Edge atuais (Windows, Linux, macOS); Chrome no Android 10+; Safari no iOS/iPadOS 16.4+; Firefox atual (leitor via zxing-wasm) |
| RNF-02 | Plataformas do servidor | Ubuntu 26.04 LTS (referência, suporte até 2031) e 24.04 LTS; Debian 13; Windows 11 Pro em versão com suporte vigente da Microsoft (hoje 25H2 ou mais nova; Home com aviso). Windows 10 não suportado. O `avante doctor` alerta quando o sistema sai do suporte |
| RNF-03 | Responsividade | Sem overflow horizontal de 320 a 2560 px; layouts específicos para celular, tablet e notebook; orientação retrato e paisagem |
| RNF-04 | Acessibilidade | WCAG 2.2 AA nos fluxos principais; zero violações "serious/critical" no axe; teclado completo; alvos de toque ≥ 44×44 px |
| RNF-05 | Desempenho † | API p95 < 300 ms em leituras e < 500 ms em operações de estoque, com 20 usuários simultâneos e 50 mil movimentações; primeira carga < 3 s em 4G; app em cache < 1 s; evento em tempo real entregue < 2 s |
| RNF-06 | Disponibilidade † | Serviço volta sozinho após queda de energia/reinício em < 3 min, nos dois sistemas |
| RNF-07 | Recuperação † | RPO ≤ 15 min; RTO ≤ 4 h em notebook novo, inclusive restaurando backup feito em um sistema operacional no outro |
| RNF-08 | Segurança | Zero vulnerabilidades altas/críticas abertas sem exceção aprovada; OWASP ASVS 4.0 nível 2 como referência |
| RNF-09 | Privacidade | LGPD: inventário de dados pessoais, base legal, retenção, exportação e anonimização |
| RNF-10 | Integridade | Saldo = Σ movimentações, verificado diariamente e por testes de propriedade |
| RNF-11 | Concorrência | Nenhum saldo negativo, empréstimo duplicado ou movimentação duplicada sob carga concorrente |
| RNF-12 | Manutenibilidade | Cobertura ≥ 85% de linhas e ≥ 80% de ramos nos módulos de domínio; lint e typecheck estritos sem erro |
| RNF-13 | Observabilidade | Logs JSON com request_id; métricas; alertas (backup, disco > 85%, certificado < 14 dias, reconciliação) |
| RNF-14 | Compatibilidade de versões | N-1 → N sem perda; rollback N → N-1 testado nos dois sistemas |
| RNF-15 | Localização | pt-BR na 1.0; textos externalizados (pronto para en/es) |
| RNF-16 | Tempo e datas | `timestamptz` em UTC; exibição no fuso da organização |
| RNF-17 | Licenças | Toda dependência distribuída com licença compatível com venda de software fechado, verificada no CI |
| RNF-18 | Desempenho percebido | LCP ≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1 em celular intermediário em 4G; JS inicial ≤ 200 KB comprimido; leitor de QR aberto em ≤ 1 s; Lighthouse celular: Desempenho ≥ 90, Acessibilidade = 100, Boas práticas ≥ 95 (`ESPECIFICACAO_UI_UX.md` §15) |
| RNF-19 | Usabilidade | SUS ≥ 80; ≥ 90% de sucesso sem ajuda nas tarefas principais; tempos dentro das metas; zero erros graves que causem dado errado no estoque (`ESPECIFICACAO_UI_UX.md` §3.2 e §19) |

## 6. Arquitetura (resumo — detalhes em `ARQUITETURA_E_DECISOES.md`)

- **Servidor:** notebook com Linux ou Windows; disco criptografado (LUKS/BitLocker com TPM); firewall fechado por padrão; energia e tampa configuradas para não suspender.
- **Serviços nativos** (systemd no Linux, serviços do Windows): Caddy (HTTPS e arquivos estáticos), API FastAPI (Python 3.14 embutido), worker de jobs, PostgreSQL 18, backup (WAL + restic).
- **Aplicativo:** SPA React + TypeScript + Vite, instalável (PWA), no mesmo domínio da API (`/api/v1`); tempo real por SSE; Web Push.
- **Acesso:** domínio por cliente com certificado válido (DNS-01); rede local direta; acesso externo sem portas abertas (VPN WireGuard ou túnel — Gate 0).
- **Distribuição:** `.deb` assinado (repositório apt) e `.msi` assinado (Authenticode); licença assinada verificada offline.
- **Backend:** monólito modular (identidade, organização, catálogo, estoque, empréstimos, documentos, etiquetas, suporte, notificações, relatórios, auditoria, administração) com camada de plataforma isolando diferenças entre sistemas.

## 7. Fases, entregas e gates

Regras gerais:
- Uma fase só começa com o gate anterior em PASS aprovado pelo responsável.
- A partir da Fase 1, existe um **ambiente de homologação** no notebook do laboratório; cada fase de funcionalidade termina com demonstração nele.
- Cada fase de funcionalidade entrega backend, telas que cumprem a Definição de Pronto de UI (`ESPECIFICACAO_UI_UX.md` §18), testes (unitários, integração com PostgreSQL, E2E do fluxo) e documentação **juntos**.
- **Paridade de plataforma:** qualquer gate que envolva o servidor exige evidência em Linux **e** Windows.
- Marcos (ver `ANALISE_DE_ROTA.md`): M0 = Fases 0–1 · M1 Alfa = 2–6 · M2 Beta = 7–8 · M3 RC = 9–11 · M4 1.0 interna = 12 · M5 pacote comercial = 13 (quando a venda for decidida).

### Fase 0 — Descoberta, requisitos e decisões
**Entregas:** validação dos documentos; pesquisa com 6–8 membros da Avante Tech Jr de 3+ papéis e observação do balcão; personas, jornadas e mapa de navegação validados; **protótipo navegável das jornadas J1–J7** (celular e notebook) testado com 5 usuários (`ESPECIFICACAO_UI_UX.md` §17); modelo de ameaças; ADRs aprovadas; **spike de rede** em Linux e Windows (domínio, HTTPS válido na LAN e fora, acesso remoto, câmera no Android e no iPhone, Web Push); **spike de hardware** (desempenho, energia/tampa, TPM, criptografia de disco); obtenção do arquivo vetorial original da logo da Avante Tech Jr.
**Gate 0:** ADRs aceitas; protótipo aprovado após o teste com usuários; câmera lendo QR em celular real via HTTPS válido dentro e fora da rede, com servidor nos dois sistemas; metas † medidas.

### Fase 1 — Fundação de engenharia
**Entregas:** branch órfã `definitivo` com monorepo; backend modular com camada de plataforma; SPA/PWA com **design system v0.1** e ponto único de marca (RF-APP-09) com os arquivos de `brand/` (tokens em JSON, temas claro/escuro, componentes base no Storybook, verificação de contraste, testes visuais e Lighthouse CI); CI bloqueante em **Ubuntu e Windows** (lint, typecheck, testes, migrations vazio e N-1, build, SAST, dependências, segredos, licenças, SBOM); pre-commit; logs estruturados, request_id, health checks; SSE de base; primeiro pacote `.deb` e `.msi` instalando em homologação.
**Gate 1:** CI verde nos dois sistemas sem etapa mascarada; instalação limpa do pacote em Ubuntu 26.04, Ubuntu 24.04, Debian 13 e Windows 11 limpos; app vazio aberto por HTTPS e instalado como PWA em celular e notebook.

### Fase 2 — Identidade, acesso e segurança
**Entregas:** RF-IAM-01..13; RF-AUD-01..03 (base); CSP estrita e headers; CSRF; rate limiting; telas de login, convite, MFA, recuperação, perfil (com foto), dispositivos.
**Gate 2:** testes de autorização horizontal e vertical em todas as rotas; testes de sessão; ZAP baseline sem achados altos.

### Fase 3 — Núcleo de inventário
**Entregas:** RF-ORG-01..05, RF-CAT-01..08, RF-INV-01..05, RF-MOV-04..06; ledger; saldos com constraints; reconciliação diária; telas de catálogo e estoque (incluindo tudo da Matriz §3).
**Gate 3:** testes de propriedade (saldo = Σ movimentações); concorrência com PostgreSQL real; nenhuma rota altera saldo sem movimentação.

### Fase 4 — Operações de estoque e documentos
**Entregas:** RF-MOV-01..03, 07; RF-DOC-01..08; RF-CNT-01..03.
**Gate 4:** NF-e reais e hostis testadas; entrada por NF atômica; inventário com vários aparelhos.

### Fase 5 — Empréstimos e reservas
**Entregas:** RF-EMP-01..09; RF-POL-01..07; RF-COL-01.
**Gate 5:** todas as combinações de política testadas; devolução parcial e ocorrências; prazos corretos com servidor em fuso diferente de UTC.

### Fase 6 — QR, etiquetas e leitura
**Entregas:** RF-QR-01..14 conforme `ESTRATEGIA_QR_CODE.md`; RF-INV-06 (kits).
**Gate 6:** câmera homologada em Android, iPhone, tablet e notebook; leitor USB; casos duplicado, revogado, malformado, desconhecido, de outra organização e repetido com códigos de erro definidos; nenhuma leitura altera estoque sem confirmação; etiquetas impressas validadas.

### Fase 7 — Suporte, notificações, relatórios e administração
**Entregas:** RF-SUP-01..10, RF-NOT-01..06, RF-COL-02, RF-REL-01..04, RF-ADM-01..03, 05, 06.
**Gate 7:** conversa de suporte em tempo real entre dois aparelhos (< 2 s); zero notificações duplicadas em reprocessamento; push funcionando com app fechado; exportações auditadas.

### Fase 8 — Experiência, acessibilidade e PWA (homologação transversal)
**Entregas:** RF-APP-01..07; revisão heurística e auditoria de acessibilidade de todas as telas (`ESPECIFICACAO_UI_UX.md` §13 e §18); instalação PWA nas plataformas; atualização sem cache obsoleto; leitura offline.
**Gate 8:** RNF-03, RNF-04, RNF-18 e RNF-19 comprovados; 2ª rodada de teste de usabilidade (tarefas do §3.2 da especificação, pessoas de 3 papéis); toda tela cumprindo a Definição de Pronto de UI.

### Fase 9 — Plataforma do servidor e operação (Linux e Windows)
**Entregas:** instaladores finais; hardening dos dois sistemas; serviços com sandbox/contas dedicadas; Caddy; acesso remoto escolhido; backup WAL + restic com cópia local e externa criptografada; `avante update` com backup prévio e rollback; monitoramento e alertas; manuais de instalação e operação para cada sistema.
**Gate 9:** nos dois sistemas: instalação em notebook limpo seguindo só o manual; queda de energia simulada; restauração completa em outro notebook dentro do RTO (incluindo backup Linux → restauração Windows e vice-versa); atualização N-1 → N e rollback.

### Fase 10 — Importação de dados do MVP
**Entregas:** RF-IMP-01..05; ensaio com dump real em ambiente isolado; relatório de reconciliação; aprovação do responsável.
**Gate 10:** totais conciliados; empréstimos abertos preservados; inconsistências decididas; MVP operando sem alteração.

### Fase 11 — Qualidade final e segurança
**Entregas:** E2E completo (Playwright: Chromium, WebKit, Firefox, perfis móveis) no CI; rodada em aparelhos reais; carga (RNF-05); caos e recuperação; **pentest** (checklist ASVS L2 interno e, idealmente, externo independente); correções.
**Gate 11:** RNF-05, RNF-08, RNF-10, RNF-11 comprovados; nenhum achado alto/crítico aberto.

### Fase 12 — Piloto e release 1.0 na Avante Tech Jr
**Entregas:** onboarding da Avante Tech Jr (assistente, cartaz com QR de conexão); documentação (manual do usuário, do administrador, de instalação e operação por sistema, política de privacidade interna); processo de suporte interno e de incidentes; **piloto no laboratório da Avante**; checklist de aceite percorrendo a `MATRIZ_FUNCIONALIDADES_MVP.md` linha a linha; release 1.0 assinada (`app-v1.0.0`).
**Gate 12:** Definição global de pronto (§10).

### Fase 13 — Pacote comercial (executada quando a venda for decidida)
**Entregas:** RF-ADM-04 e ADR-014 (licenciamento); nome e identidade comerciais aplicados pelo ponto único de marca (RF-APP-09); termos de uso, contrato e DPA com revisão jurídica; onboarding de clientes externos; canal de suporte do produto e níveis de serviço; material comercial; reavaliação da matriz de plataformas e do pentest externo independente.
**Gate 13:** instalação e operação de um cliente piloto externo com o pacote comercial, sem participação do desenvolvedor, e aceite formal.

## 8. Estratégia de testes

| Camada | Ferramenta | Exigência |
|---|---|---|
| Unitário backend | pytest | Regras de domínio, políticas, validações |
| Propriedade | Hypothesis | Invariantes de saldo e transições de estado |
| Integração | pytest + PostgreSQL real, em Linux e Windows | Toda rota; constraints; transações; schema **sempre pelas migrations** |
| Concorrência | threads/processos contra PostgreSQL real | Última unidade, transferências simultâneas, QR repetido, idempotência |
| Migrations | Alembic | Vazio → head; N-1 com dados → N; `alembic check` sem drift |
| Contrato | OpenAPI + cliente TS gerado | Mudança quebrada falha o CI |
| Tempo real | Testes de integração do SSE e do push | Entrega, reconexão, permissões (ninguém recebe evento que não pode ver) |
| Plataforma | Testes da camada de plataforma nos dois sistemas; instalação em VMs limpas a cada release | Serviços, caminhos, permissões, backup/restore cruzado |
| Frontend | Vitest + Testing Library | Componentes e hooks |
| E2E | Playwright | Fluxos críticos de cada papel, incluindo dois usuários interagindo (suporte, aprovação) |
| Acessibilidade | axe-core + revisão manual com leitor de tela (TalkBack, VoiceOver, NVDA, Orca) | RNF-04 |
| Visual | Capturas do Playwright comparadas no CI, por tema e ponto de quebra; Storybook | Sem regressão visual não aprovada |
| Desempenho percebido | Lighthouse CI e medição em aparelho real | RNF-18 |
| Usabilidade | Testes moderados com tarefas reais e SUS | RNF-19 |
| Segurança | Bandit/Semgrep, pip-audit, OSV-Scanner, gitleaks, ZAP, verificação de licenças | RNF-08, RNF-17 |
| Carga | k6 ou Locust | RNF-05 |
| Recuperação | Roteiros automatizados em homologação | RNF-06, RNF-07, RNF-14 |
| Aparelhos reais | Matriz do Gate 0 | Câmera, instalação PWA, push, layout |

Casos obrigatórios herdados da v1.0: uploads inválidos/gigantes/MIME falso; QR duplicado/desconhecido/malformado/legado/repetido; NF malformada/repetida/divergente; empréstimo, devolução parcial, atraso, baixa, transferência; login, logout, expiração, revogação, força bruta; permissões horizontais e verticais.

## 9. Lições do MVP (rastreabilidade)

| Achado | Requisito/decisão que impede a repetição |
|---|---|
| AUD-001 migrations não instalam do zero | CI: vazio → head e N-1 → N; `alembic check` |
| AUD-002 datas dependem do fuso | RNF-16, ADR-015, testes com servidor em fuso ≠ UTC |
| AUD-003 CI não bloqueia | Gate 1 sem etapa mascarada |
| AUD-004 testes desatualizados / `create_all` | §8; regra de testes junto com o comportamento |
| SEC-01 token por username | RF-IAM-02 |
| SEC-02 sem revogação | RF-IAM-03 |
| SEC-03 sem rate limit | RF-IAM-07 |
| SEC-04 upload de QR sem limite | RF-QR-02; limites antes de decodificar (ADR-008) |
| SEC-05 dependências vulneráveis | RNF-08; scan bloqueante e atualização automatizada |
| SEC-06/07 headers e CSRF | Fase 2 |
| SEC-08 anexos sem limite; base64 no banco | ADR-008; RF-SUP-04 |
| SEC-09 HTML sem escape em e-mail | Templates com escape automático |
| SEC-11 tipo de imagem declarado pelo cliente | ADR-008 |
| INT-01 QR soma estoque sozinho | RF-QR-04, RF-QR-06 |
| INT-02 sem movimentações/auditoria | RF-MOV, RF-AUD |
| INT-03 sem constraints | RF-INV-04 |
| INT-04 NF arredonda, sem revisão, não atômica | RF-CAT-05, RF-DOC-02..04 |
| INT-05 QR casando com itens diferentes | ADR-011 |
| INT-06 pendência de devolução não atrasa | RF-EMP-07 |
| INT-07 exclusão com empréstimo aberto | RF-IAM-12 |
| PERF-01 OCR bloqueia a API | Jobs pesados só no worker (ADR-009) |
| PERF-02 e-mail síncrono para todos | RF-NOT-05, RF-NOT-06 |
| FE-01 câmera exige HTTPS | Gate 0 |
| FE-03 datas exibidas com desvio | Função única de datas (ADR-015) |
| Licença AGPL do PyMuPDF | ADR-016, RNF-17 |

## 10. Definição global de pronto (release 1.0)

O produto só é pronto quando **todos** os itens têm evidência anexada:
1. Todos os requisitos **M** implementados, testados e demonstrados em homologação.
2. Gates 0–11 em PASS.
3. Em Linux **e** Windows: instalação limpa, atualização N-1 → N, rollback e restauração em outro notebook executados por alguém que não é o desenvolvedor, só com o manual.
4. E2E dos fluxos críticos verde no CI; homologação em aparelhos reais registrada; RNF-18 e RNF-19 comprovados.
5. Pentest sem achado alto/crítico aberto.
6. Importação do MVP ensaiada e reconciliada.
7. Checklist da `MATRIZ_FUNCIONALIDADES_MVP.md` 100% aprovado.
8. Piloto concluído com termo de aceite.
9. Documentação técnica e de uso publicada; suporte interno operacional. (Licença e documentação comercial pertencem à Fase 13.)

## 11. Fora de escopo da 1.0 (até decisão explícita)

- Apps nativos e Electron (a casca de loja Capacitor é C, RF-APP-08).
- Escrita offline com sincronização (a 1.0 tem leitura offline; as chaves de idempotência deixam o caminho aberto).
- Chat livre entre usuários (a interação é contextual: suporte, empréstimos, solicitações).
- Integração com SEFAZ ou ERP.
- SaaS multi-cliente (não impedido pela arquitetura, mas não é objetivo).
- Servidor em macOS.
- Biometria e reconhecimento facial.
- IA sem caso de uso, política de dados e métrica de benefício.
- Requisitos de prioridade **C** (RF-EMP-10, RF-CNT-04, RF-APP-08), planejados para versões 1.x; RF-ADM-04 pertence à Fase 13.
- Correções no MVP: se o responsável quiser corrigir defeitos do MVP em uso (ex.: AUD-002), abrir **backlog separado**, com aprovação própria, sem atrasar o produto.

## 12. Governança

- Toda tarefa segue o `GUIA_EXECUCAO_CLAUDE.md` v2.3.
- Decisões arquiteturais viram ADR; mudar ADR aceita exige nova ADR.
- Versionamento: `0.x.y` até a 1.0, SemVer depois; tags `app-vX.Y.Z` só após gate aprovado; nunca sobrescritas.
- Mudanças neste plano exigem nova versão com motivo registrado; o plano nunca é enfraquecido para aprovar entrega.

## 13. Decisões em aberto

| ID | Decisão | Quando |
|---|---|---|
| DA-01 | Acesso remoto: VPN WireGuard (Tailscale/Headscale) × túnel com camada de acesso | Gate 0 (spike) |
| DA-02 | Domínio do produto e padrão de nome por cliente | Gate 0 |
| DA-03 | Modelo de licença (assinatura × perpétua + suporte) e comportamento ao expirar | Fase 13 |
| DA-04 | Destino do backup externo e guarda da chave | Gate 0 |
| DA-05 | Matriz de aparelhos reais e máquinas Windows/Linux de homologação | Gate 0 |
| DA-06 | Metas † do §5 | Gate 0, após medição |
| DA-07 | Duração e critérios do piloto | Fase 11 |
| DA-08 | Publicação em lojas (RF-APP-08) | Após a 1.0 |
| UX-DA-02..04 | Decisões de UX restantes (`ESPECIFICACAO_UI_UX.md` §20); UX-DA-01 e UX-DA-05 resolvidas em 03/11/2026 | Fases 0, 1 e 6 |
