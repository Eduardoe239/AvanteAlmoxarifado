# Volume 02 — Requisitos

**Produto:** Avante Almoxarifado · **Versão:** 3.1.0 · **Data:** 24/11/2026 · **Status:** Aprovado em 24/11/2026
**Responsável:** Luís Eduardo de Sousa Barbosa

---

## 1. Convenções

- **ID:** `RF-<GRUPO>-<nº>` (funcional) e `RNF-<nº>` (não funcional). IDs nunca são reaproveitados; requisito removido vira "Retirado" com motivo.
- **Prioridade (dentro da release):** **M** obrigatório para a release sair · **S** desejável; pode passar para a próxima release com decisão registrada · **C** futuro.
- **Release:** em qual entrega o requisito é implementado (R1–R4; "Pós-R4" = depois da versão comercial). Releases e critérios de saída no Volume 12.
- **Rastreabilidade:** todo requisito M ou S tem pelo menos um teste automatizado ou roteiro de homologação que o cita pelo ID (Volume 09).
- **Funções do MVP:** cada função do MVP aponta para requisitos deste volume (Anexo A1).

## 2. Requisitos funcionais

Convenções na §1.

### 2.1 Identidade, acesso e sessão (IAM)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-IAM-01 | Login com usuário ou e-mail e senha; Argon2id; senha mínima de 10 caracteres, medidor de força, checagem contra senhas vazadas (lista local) | M | R1 |
| RF-IAM-02 | Sessões no servidor (token opaco, revogável, vinculado ao ID interno), expiração por inatividade e absoluta configuráveis | M | R1 |
| RF-IAM-03 | Troca de senha, desativação, mudança de papel e "sair de todos os dispositivos" encerram as sessões afetadas na hora | M | R1 |
| RF-IAM-04 | MFA TOTP com códigos de recuperação; **obrigatório** para Proprietário, Administrador, Gestor e Atendente | M | R1 |
| RF-IAM-05 | Passkeys (WebAuthn) como fator ou login sem senha | S | R2 |
| RF-IAM-06 | Recuperação de senha por e-mail com token de uso único e curta duração; administrador pode **enviar** link de redefinição, nunca definir a senha | M | R1 |
| RF-IAM-07 | Bloqueio progressivo e rate limiting por conta e por IP | M | R1 |
| RF-IAM-08 | Cadastro por convite (padrão); autocadastro opcional por política, com domínio de e-mail permitido e aprovação | M | R1 |
| RF-IAM-09 | Lista de dispositivos/sessões ativos do usuário, com encerramento remoto | M | R1 |
| RF-IAM-10 | RBAC granular com escopo; papéis padrão; invariante "sempre existe um Proprietário ativo com MFA"; papéis personalizados | M / S | R1 |
| RF-IAM-11 | Perfil: nome, e-mail, setor (troca livre ou com aprovação, por política), foto com recorte e zoom no aparelho, preferências de notificação, idioma, tema | M | R1 |
| RF-IAM-12 | Quem tem histórico nunca é apagado: anonimização (LGPD); exclusão bloqueada com empréstimo em aberto | M | R1 |
| RF-IAM-13 | Titular pode solicitar encerramento da própria conta e exportação dos seus dados (LGPD), com a proteção do último Proprietário | M | R1 |

### 2.2 Organização e estrutura (ORG)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-ORG-01 | Dados da organização (nome, CNPJ opcional, logotipo e cores da marca, fuso horário, idioma) | M | R1 |
| RF-ORG-02 | Setores/departamentos configuráveis, desativáveis sem perder histórico | M | R1 |
| RF-ORG-03 | Múltiplos almoxarifados por instalação | M | R1 |
| RF-ORG-04 | Localizações hierárquicas (prédio › sala › armário › prateleira › gaveta) com etiqueta QR própria | M | R1 |
| RF-ORG-05 | Assistente de configuração inicial no primeiro acesso | M | R1 |

### 2.3 Catálogo (CAT)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-CAT-01 | Item: nome, descrição, categoria, fabricante, modelo, part number, unidade de medida, fotos, anexos (datasheet), campos técnicos, códigos de barras do fabricante (EAN/GTIN) | M | R1 |
| RF-CAT-02 | Modo de controle: **UNITARIO**, **QUANTITATIVO** e **LOTE** (com validade) | M | R1 |
| RF-CAT-03 | Estoque mínimo e ponto de reposição por item e almoxarifado | M | R1 |
| RF-CAT-04 | Categorias hierárquicas e fabricantes | M | R1 |
| RF-CAT-05 | Unidades de medida com casas decimais; quantidades fracionárias exatas, sem arredondamento | M | R1 |
| RF-CAT-06 | Busca no servidor, insensível a acentos, por nome, código, patrimônio, part number, QR e código de barras; filtros por categoria, local, estado, setor e disponibilidade; ordenação; paginação; filtros salvos | M | R1 |
| RF-CAT-07 | Itens "emprestáveis" × "somente consumo" | M | R1 |
| RF-CAT-08 | Campos personalizados por categoria | S | R2 |

### 2.4 Unidades físicas e saldos (INV)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-INV-01 | Unidade física com identificador imutável, nº de patrimônio, nº de série, local, estado e responsável atual | M | R1 |
| RF-INV-02 | Estados com transições validadas: DISPONIVEL, RESERVADO, EMPRESTADO, EM_MANUTENCAO, EM_CONFERENCIA, PERDIDO, BAIXADO | M | R1 |
| RF-INV-03 | Saldo por item × almoxarifado × local (× lote), sempre derivado das movimentações | M | R1 |
| RF-INV-04 | Saldo nunca negativo, garantido no banco e no serviço | M | R1 |
| RF-INV-05 | Histórico completo por item, unidade, local, usuário e período | M | R1 |
| RF-INV-06 | Kits: conjunto de unidades emprestado como um todo, com checklist de componentes | S | R2 |

### 2.5 Movimentações (MOV)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-MOV-01 | Entrada: compra (NF-e), doação, devolução de terceiros, ajuste positivo, cadastro inicial | M | R1 |
| RF-MOV-02 | Saída: consumo, baixa (motivo obrigatório), perda, ajuste negativo, envio para manutenção | M | R1 |
| RF-MOV-03 | Transferência entre locais e entre almoxarifados (com confirmação de recebimento opcional) | M | R1 |
| RF-MOV-04 | Toda movimentação registra operador, data/hora UTC, origem, destino, quantidade, motivo, referência e dispositivo | M | R1 |
| RF-MOV-05 | Movimentações imutáveis; correção por estorno | M | R1 |
| RF-MOV-06 | Operações atômicas e idempotentes (`Idempotency-Key`); concorrência sem saldo negativo nem duplicidade | M | R1 |
| RF-MOV-07 | Ajustes acima de limite configurável exigem aprovação de gestor | S | R2 |

### 2.6 Empréstimos e reservas (EMP)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-EMP-01 | Solicitação com carrinho de várias unidades/quantidades e prazo | M | R1 |
| RF-EMP-02 | Política: aprovação obrigatória/automática por categoria, prazo máximo, tolerância, limite por usuário | M | R1 |
| RF-EMP-03 | Retirada registrada pelo operador (escaneando) ou autoatendimento se a política permitir; operador pode registrar em nome de alguém, ficando registrado quem operou | M | R1 |
| RF-EMP-04 | Devolução total ou parcial; conferência pelo operador configurável (o fluxo em duas etapas do MVP é o padrão) | M | R1 |
| RF-EMP-05 | Devolução com ocorrência (dano, falta, perda), com fotos e encaminhamento | M | R1 |
| RF-EMP-06 | Renovação com regras (máximo de renovações; bloqueio se houver reserva) | M | R1 |
| RF-EMP-07 | Atraso calculado em UTC com fuso da organização; pendências de conferência também contam prazo; escalonamento ao gestor após N dias | M | R1 |
| RF-EMP-08 | Reservas com data futura e detecção de conflito; fila de espera para unidade emprestada | S | R2 |
| RF-EMP-09 | Termo de responsabilidade aceito digitalmente na retirada | S | R2 |
| RF-EMP-10 | Empréstimo a pessoa externa (sem conta) com dados mínimos | C | Pós-R4 |

### 2.7 QR Code, etiquetas e leitura (QR) — detalhado no Volume 08
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-QR-01 | Etiquetas de unidade, localização, item a granel, lote, kit e conexão; conteúdo = URL com código opaco de 80 bits + verificador; sem dados pessoais ou de negócio | M (kit: S) | R1 |
| RF-QR-02 | Decodificação no aparelho (BarcodeDetector + zxing-wasm); servidor recebe só o código | M | R1 |
| RF-QR-03 | Digitação do código curto com verificador; leitores USB/Bluetooth em modo teclado em qualquer tela | M | R1 |
| RF-QR-04 | Leitura abre a ficha do objeto com ações contextuais por tipo, estado e papel; **nada muda sem confirmação** | M | R1 |
| RF-QR-05 | Código desconhecido → cadastro assistido (vincular ou criar); nunca criação silenciosa | M | R1 |
| RF-QR-06 | Idempotência no servidor; repetição na mesma sessão sinalizada, não somada | M | R1 |
| RF-QR-07 | Impressão em lote: A4 (modelos padrão Pimaco) e térmica, com teste automático de legibilidade do PDF gerado | M | R1 |
| RF-QR-08 | Revogar/substituir etiqueta mantendo histórico; aviso ao escanear etiqueta revogada | M | R1 |
| RF-QR-09 | Etiquetas do MVP reconhecidas via tabela de mapeamento, com relatório de reetiquetagem | M | R2 |
| RF-QR-10 | Modos em sequência: carrinho de retirada, devolução em lote, recebimento, guardar/transferir, inventário, vincular etiquetas; lista com desfazer antes de confirmar | M | R1 |
| RF-QR-11 | Etiquetas pré-impressas ("virgens") vinculáveis depois | M | R1 |
| RF-QR-12 | Leitura de códigos de barras do fabricante (EAN/GTIN, Code 128) para localizar/sugerir item | S | R2 |
| RF-QR-13 | Modo balcão (tablet/notebook fixo): tela permanente de leitura, bloqueio por inatividade | S | R2 |
| RF-QR-14 | QR de conexão para cartaz/convite, que leva à instalação do app | M | R1 |

### 2.8 Documentos fiscais e compras (DOC)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-DOC-01 | NF-e XML processada no servidor com parser seguro (sem entidades externas): chave, emitente, itens, quantidades, unidades, valores | M | R2 |
| RF-DOC-02 | Deduplicação pela chave de acesso | M | R2 |
| RF-DOC-03 | Rascunho de entrada editável: mapear cada linha a um item de catálogo (existente ou novo), corrigir quantidade, unidade e fator de conversão, escolher local | M | R2 |
| RF-DOC-04 | Confirmação atômica (tudo ou nada) gera as movimentações e vincula a nota a elas | M | R2 |
| RF-DOC-05 | Memória de mapeamento fornecedor + código → item | S | R2 |
| RF-DOC-06 | PDF/DANFE: leitura da chave e extração assistida no worker, com OCR, sempre "não verificada" | S | R2 |
| RF-DOC-07 | Fornecedores; anexos de documentos visualizáveis (PDF, imagem) | M | R2 |
| RF-DOC-08 | Aviso explícito: o sistema não valida autenticidade fiscal na SEFAZ | M | R2 |

### 2.9 Inventário físico (CNT)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-CNT-01 | Abrir inventário por almoxarifado/local, congelando o saldo de referência | M | R2 |
| RF-CNT-02 | Contagem por QR ou digitação, em vários aparelhos ao mesmo tempo | M | R2 |
| RF-CNT-03 | Divergências e ajustes de conciliação com aprovação | M | R2 |
| RF-CNT-04 | Inventário cíclico agendado | C | Pós-R4 |

### 2.10 Políticas configuráveis (POL)
| ID | Requisito | Padrão seguro | Prior. | Release |
|---|---|---|---|---|
| RF-POL-01 | Autocadastro | Desligado (só convite) | M | R1 |
| RF-POL-02 | Aprovação de empréstimos | Obrigatória para UNITARIO | M | R1 |
| RF-POL-03 | Conferência de devolução pelo operador | Ligada | M | R1 |
| RF-POL-04 | Prazo máximo e tolerância | 30 dias / 1 dia | M | R1 |
| RF-POL-05 | Sessão (inatividade/absoluta) | 30 min / 12 h | M | R1 |
| RF-POL-06 | MFA por papel | Obrigatório para privilegiados (não desligável) | M | R1 |
| RF-POL-07 | Troca do próprio setor | Livre | M | R1 |

### 2.11 Experiência de aplicativo e tempo real (APP)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-APP-01 | Instalável como PWA em Android, iPhone/iPad, Windows, Linux e macOS, com ícone, tela cheia e página "Instalar" com instruções por plataforma | M | R1 |
| RF-APP-02 | Atualização do app sem cache obsoleto: aviso de nova versão e recarga sem perder dados em edição | M | R1 |
| RF-APP-03 | Eventos em tempo real (SSE): novas mensagens, aprovações, devoluções, alertas e mudanças de saldo aparecem sem atualizar a tela | M | R1 |
| RF-APP-04 | Leitura offline: catálogo, meus empréstimos e fichas visitadas ficam disponíveis sem conexão, com indicação clara; ações exigem conexão | M | R1 |
| RF-APP-05 | Indicador de conexão (online/offline/reconectando) | M | R1 |
| RF-APP-06 | Navegação por papel: barra inferior + botão "Escanear" no celular; menu lateral com busca e paleta de comandos (Ctrl+K) no notebook; atalhos de tarefas frequentes | M | R1 |
| RF-APP-07 | Tema claro/escuro e marca do cliente (logotipo/cores) | M | R1 |
| RF-APP-08 | Publicação em lojas (Play Store/App Store) por casca Capacitor com "Conectar à organização" | C | Pós-R4 |
| RF-APP-09 | Marca do produto centralizada: nome ("Avante Almoxarifado"), logotipo, ícones, cores e textos de marca definidos em um único ponto de configuração e nos tokens, para que a troca de marca na venda não exija mudar código | M | R1 |

### 2.12 Notificações (NOT)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-NOT-01 | Central de notificações no app, com lidas/não lidas | M | R1 |
| RF-NOT-02 | E-mail transacional: convite, recuperação de senha, aprovação, lembrete, atraso, estoque mínimo, resposta de chamado | M | R1 |
| RF-NOT-03 | Web Push com o app fechado (Android, desktop; iPhone com app instalado) | M | R2 |
| RF-NOT-04 | Preferências por usuário e canal; lembretes configuráveis (ex.: 3 dias e 1 dia antes); atraso no máximo 1×/dia; nunca duplicadas (outbox + deduplicação) | M | R1 |
| RF-NOT-05 | Envio pelo worker, com retry exponencial e registro de falha sem dados sensíveis | M | R1 |
| RF-NOT-06 | "Novidades do catálogo": resumo opcional diário/semanal de itens novos (substitui o e-mail a todos por item do MVP) | S | R2 |

### 2.13 Suporte (SUP) — interação entre usuários e equipe
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-SUP-01 | Qualquer usuário abre chamado com assunto, descrição, categoria e prioridade sugerida | M | R1 |
| RF-SUP-02 | Vínculo opcional a item, unidade, local ou empréstimo (aberto a partir da ficha ou de uma leitura de QR) | M | R1 |
| RF-SUP-03 | Conversa em tempo real entre solicitante e equipe, com nome, foto, horário e indicador de leitura | M | R1 |
| RF-SUP-04 | Anexos: imagens (comprimidas no aparelho) e PDF, com limites por arquivo e por chamado | M | R1 |
| RF-SUP-05 | Notas internas visíveis só para a equipe de suporte | M | R1 |
| RF-SUP-06 | Ciclo: Aberto → Em atendimento → Aguardando usuário → Resolvido → Fechado, com reabertura; o solicitante confirma a resolução ou informa "ainda não resolvido" (do MVP) | M | R1 |
| RF-SUP-07 | Fila da equipe: filtros, atribuição a atendente, prioridade, separação ativos × concluídos | M | R1 |
| RF-SUP-08 | Prazos de primeira resposta e de resolução (SLA) configuráveis, com alerta; respostas prontas | S | R2 |
| RF-SUP-09 | Avaliação do atendimento ao fechar | S | R2 |
| RF-SUP-10 | Notificação ao solicitante e à equipe em cada mudança (app, push, e-mail conforme preferência) | M | R1 |

### 2.14 Colaboração em processos (COL)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-COL-01 | Comentários em empréstimos, solicitações e reservas entre solicitante e almoxarifado, em tempo real | M | R1 |
| RF-COL-02 | Comentários internos da equipe em itens, unidades e inventários | S | R2 |

### 2.15 Relatórios, painéis e exportação (REL)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-REL-01 | Painel por papel: saldos, abaixo do mínimo, empréstimos ativos/atrasados, chamados abertos, movimentações recentes, saúde do estoque | M | R1 |
| RF-REL-02 | Relatórios: posição de estoque, movimentações, histórico por item/usuário/setor, empréstimos, inventários, perdas e baixas, chamados | M | R2 |
| RF-REL-03 | Exportação CSV e XLSX; PDF para posição e termo | M | R1 |
| RF-REL-04 | Exportações auditadas e restritas por permissão | M | R1 |

### 2.16 Auditoria (AUD)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-AUD-01 | Trilha imutável de ações de negócio e de segurança (quem, o quê, quando, de onde, resultado, antes/depois) | M | R1 |
| RF-AUD-02 | Encadeamento por hash e permissões de banco que impedem UPDATE/DELETE | M | R1 |
| RF-AUD-03 | Consulta com filtros por Auditor e Administrador | M | R1 |

### 2.17 Administração da instalação (ADM)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-ADM-01 | Página de saúde: versão, sistema operacional, banco, uso e **saúde do disco (SMART)**, temperatura, memória, último backup e último teste de restauração, validade do certificado, fila de jobs, dispositivos conectados | M | R1 |
| RF-ADM-02 | SMTP (com envio de teste), domínio e acesso remoto configuráveis pelo app ou pela CLI | M | R1 |
| RF-ADM-03 | Backup sob demanda e status dos automáticos | M | R1 |
| RF-ADM-04 | Licença: ver, instalar, renovar (Edição Comercial; Volume 11) | M | R4 |
| RF-ADM-05 | Atualização: aviso de nova versão e notas; aplicação pela CLI `avante update` (mesmos comandos em todas as plataformas suportadas) | M | R1 |
| RF-ADM-06 | CLI `avante` com os mesmos comandos nos dois sistemas: `status`, `doctor`, `backup`, `restore`, `update`, `rollback`, `support-bundle` (sem dados pessoais) | M | R1 |

### 2.18 Importação do MVP (IMP)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-IMP-01 | Importador a partir de dump do MVP restaurado em banco temporário; nunca conecta ao banco em uso | M | R2 |
| RF-IMP-02 | Preflight com relatório: contagens, inconsistências, fuso das datas (defeito de fuso do MVP) | M | R2 |
| RF-IMP-03 | Classificação assistida UNITARIO/QUANTITATIVO; unidades provisórias marcadas para conferência | M | R2 |
| RF-IMP-04 | Empréstimos abertos, usuários, setores, chamados, notas fiscais e fotos preservados; reconciliação sem descarte silencioso | M | R2 |
| RF-IMP-05 | Mapeamento das etiquetas antigas (RF-QR-09) | M | R2 |

### 2.19 Visão computacional (CV) — detalhado no Volume 05
Toda inferência roda **no aparelho do usuário ou na estação embarcada**, nunca no servidor. A visão **sugere**; uma pessoa **confirma**.
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-CV-01 | **Contagem assistida por foto** de peças pequenas sobre bandeja ou fundo de contraste: o app marca cada peça detectada na imagem, a pessoa corrige com toques (adicionar/remover) e confirma; usada em retirada de consumível, recebimento e inventário | M | R3 |
| RF-CV-02 | **Reconhecimento visual de item** ("o que é isto?"): foto comparada às fotos do catálogo, devolvendo as 5 sugestões mais parecidas com grau de confiança; usado na busca, no cadastro assistido e em etiquetas desconhecidas | M | R3 |
| RF-CV-03 | **Leitura de texto no aparelho (OCR)** de plaquetas de patrimônio, part numbers e números de série, preenchendo campos com confirmação | S | R3 |
| RF-CV-04 | Gestão de modelos: versão, métricas de validação, distribuição aos aparelhos e estações, ativação gradual e reversão para a versão anterior | M | R3 |
| RF-CV-05 | Base de imagens de referência e de validação: fotos de itens (nunca de pessoas), com origem, consentimento quando aplicável e anotação feita no próprio app | M | R3 |
| RF-CV-06 | Qualidade em produção: taxa de correção humana por recurso e por versão de modelo, exibida ao gestor; alerta quando piorar | S | R3 |
| RF-CV-07 | Conferência visual de devolução: comparação da foto da retirada com a da devolução, sinalizando possível dano ou falta ao operador | C | Pós-R4 |
| RF-CV-08 | Monitoramento de compartimentos por câmera fixa: detectar mudança sem movimentação registrada e alertar, sem pessoas na imagem | C | Pós-R4 |

### 2.20 Estações e dispositivos embarcados (EMB) — detalhado no Volume 05
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-EMB-01 | Cadastro, aprovação, identificação e revogação de dispositivos, cada um com credencial própria; nada é aceito de dispositivo não aprovado | M | R3 |
| RF-EMB-02 | **Leitor de cartão de balcão** (ESP32 + leitor 13,56 MHz): identifica a pessoa pelo cartão vinculado (ex.: cartão do RU, crachá) e abre, no app do operador, a sessão de retirada ou devolução daquela pessoa | M | R3 |
| RF-EMB-03 | Vínculo de cartão ao usuário com confirmação; um cartão por pessoa; desvinculação imediata; o cartão **nunca** é o único fator para autoatendimento (exige PIN) nem para ações sensíveis | M | R3 |
| RF-EMB-04 | Saúde dos dispositivos (online, versão, última comunicação, erros) na página de saúde, com alerta de dispositivo fora do ar | M | R3 |
| RF-EMB-05 | Atualização remota de firmware/software assinada, com reversão automática se a nova versão falhar | M | R3 |
| RF-EMB-06 | Comportamento seguro sem servidor: o dispositivo informa claramente que está sem conexão e **não** registra movimentação local | M | R3 |
| RF-EMB-07 | **Estação Avante** (comercial): equipamento com câmera, leitor de cartão e tela para autoatendimento — identifica a pessoa (cartão + PIN), lê etiquetas, conta peças por visão (RF-CV-01), mostra o resumo e registra após confirmação, conforme a política de autoatendimento | M | R4 |
| RF-EMB-08 | Modo quiosque em tablet ou notebook fixo como alternativa sem hardware próprio (usa o modo balcão, RF-QR-13) | S | R2 |

### 2.21 Automação e inteligência de estoque (AUT)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-AUT-01 | Sugestão de reposição: consumo médio e tendência por item e almoxarifado, prazo de reposição informado → ponto de pedido sugerido e lista de compras exportável | S | R3 |
| RF-AUT-02 | Alertas inteligentes: itens parados há muito tempo, unidades que sempre voltam atrasadas, consumo fora do padrão, divergências recorrentes em inventário | S | R3 |
| RF-AUT-03 | Regras automáticas configuráveis (ex.: "ao atingir o mínimo, avisar o gestor"; "ao atrasar 3 dias, escalar") | S | R3 |
| RF-AUT-04 | Previsão de demanda por período (ex.: início de semestre) | C | Pós-R4 |

### 2.22 Dados do cliente: importação e portabilidade (DAT)
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-DAT-01 | **Importação de planilha** (CSV/XLSX) do estoque existente do cliente: modelo para baixar, mapeamento de colunas, validação linha a linha, prévia, simulação sem gravar e confirmação atômica, com relatório de erros | M | R4 |
| RF-DAT-02 | Importação de usuários e locais por planilha, com convites em lote | S | R4 |
| RF-DAT-03 | **Exportação completa** dos dados da organização em formato aberto (CSV/JSON + arquivos) sob demanda, com reautenticação e auditoria, para portabilidade e LGPD | M | R4 |

### 2.23 Produto comercial (COM) — detalhado no Volume 11
| ID | Requisito | Prior. | Release |
|---|---|---|---|
| RF-COM-01 | Verificação de requisitos de hardware e sistema pelo instalador (processador, memória, disco, SO, rede), com relatório e bloqueio abaixo do mínimo | M | R1 (básico) / R4 (completo) |
| RF-COM-02 | Acesso de suporte do fornecedor só com consentimento do Proprietário, por janela de tempo, com papel específico, tudo auditado e revogável a qualquer momento | M | R4 |
| RF-COM-03 | Termos de uso e política de privacidade exibidos e aceitos, com versão registrada | M | R4 |
| RF-COM-04 | Assistente de implantação do cliente: organização, marca, importação de planilha, convites, cartaz com QR de conexão | M | R4 |

## 3. Requisitos não funcionais

"Perfil Mínimo" e "Perfil Recomendado" do servidor estão definidos no Volume 04. Metas marcadas com † são calibradas por medição no notebook real na R0.

| ID | Categoria | Requisito / meta | Release |
|---|---|---|---|
| RNF-01 | Plataformas do aplicativo | Chrome/Edge atuais (Windows, Linux, macOS); Chrome no Android 10+; Safari no iOS/iPadOS 16.4+; Firefox atual (leitores via WebAssembly) | R1 |
| RNF-02 | Plataformas do servidor | **Edição Avante:** Linux — Debian 13 ou Ubuntu Server 24.04/26.04 LTS, **sem interface gráfica**, no Perfil Mínimo. **Edição Comercial:** + Windows 11 Pro em versão com suporte vigente da Microsoft. Windows 10 não suportado. Plataforma fora de suporte gera alerta | R1 (Linux) / R4 (Windows) |
| RNF-03 | Responsividade | Sem rolagem horizontal de 320 a 2560 px; layouts para celular, tablet e notebook; retrato e paisagem | R1 |
| RNF-04 | Acessibilidade | WCAG 2.2 AA nos fluxos principais; zero violações sérias/críticas no axe; teclado completo; alvos ≥ 44×44 px | R1 |
| RNF-05 | Desempenho do servidor † | **No Perfil Mínimo**, com 10 usuários ativos simultâneos (⅓ das ~30 pessoas com acesso), 60 conexões de tempo real abertas e base de 100 mil movimentações e 10 mil unidades: p95 < 500 ms em leituras, < 800 ms em operações de estoque, eventos em tempo real < 3 s. No Perfil Recomendado: < 300 ms, < 500 ms, < 2 s | R1 |
| RNF-06 | Disponibilidade † | Serviço volta sozinho em < 5 min após queda de energia ou reinício, sem intervenção | R1 |
| RNF-07 | Recuperação † | RPO ≤ 15 min; RTO ≤ 4 h em outra máquina seguindo só o manual | R1 |
| RNF-08 | Segurança | Zero vulnerabilidades altas/críticas abertas sem exceção aprovada; OWASP ASVS 4.0 nível 2 como referência; dispositivos embarcados conforme Volume 06 | R1 |
| RNF-09 | Privacidade | LGPD (Volume 06): inventário de dados pessoais, base legal, retenção, exportação e anonimização; **nenhuma imagem de pessoas** em fluxos de visão computacional | R1 |
| RNF-10 | Integridade | Saldo = Σ movimentações, verificado diariamente e por testes de propriedade | R1 |
| RNF-11 | Concorrência | Nenhum saldo negativo, empréstimo duplicado ou movimentação duplicada sob carga concorrente | R1 |
| RNF-12 | Manutenibilidade | Cobertura ≥ 85% de linhas e ≥ 80% de ramos nos módulos de domínio; lint e typecheck estritos sem erro | R1 |
| RNF-13 | Observabilidade | Logs JSON com request_id; métricas; alertas: backup, disco > 80%, **SMART do disco**, temperatura, certificado < 14 dias, reconciliação, dispositivo fora do ar | R1 |
| RNF-14 | Compatibilidade de versões | N-1 → N sem perda; rollback N → N-1 testado em cada plataforma suportada | R1 |
| RNF-15 | Localização | pt-BR; textos externalizados (pronto para en/es) | R1 |
| RNF-16 | Tempo e datas | `timestamptz` em UTC; exibição no fuso da organização | R1 |
| RNF-17 | Licenças | Toda dependência, modelo de IA, firmware e biblioteca embarcada distribuídos com licença compatível com venda de software fechado, verificada no CI | R1 |
| RNF-18 | Desempenho percebido | LCP ≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1 em celular intermediário em 4G; JS inicial ≤ 200 KB comprimido; leitor de QR aberto em ≤ 1 s; Lighthouse celular: Desempenho ≥ 90, Acessibilidade = 100, Boas práticas ≥ 95 | R1 |
| RNF-19 | Usabilidade | SUS ≥ 80; ≥ 90% de sucesso sem ajuda nas tarefas principais; zero erros que causem dado errado no estoque (Volume 07) | R2 |
| RNF-20 | Orçamento de recursos do servidor | No Perfil Mínimo (4 GB de RAM): memória residente somada dos serviços ≤ 1,5 GB em operação normal e ≤ 2,0 GB em pico; todo serviço com limite de memória; tarefas pesadas uma por vez, com prioridade baixa de CPU e disco (Volume 04) | R1 |
| RNF-21 | Armazenamento | Crescimento anual estimado e medido; alerta de disco a 80%; retenção definida para logs, WAL, anexos e backups locais (Volume 04) | R1 |
| RNF-22 | Eficiência em disco rígido | Nenhuma consulta frequente sem índice; varreduras completas e manutenção pesada só fora do horário de uso; escrita em disco com I/O de baixa prioridade para backup e relatórios | R1 |
| RNF-23 | Visão computacional † | Cada modelo ≤ 15 MB; inferência ≤ 1,5 s em celular intermediário; funciona sem internet depois de baixado; **contagem** com erro ≤ 2% nas condições padrão do Volume 05; **reconhecimento** com acerto ≥ 90% entre as 5 sugestões para itens com ≥ 3 fotos de referência; **OCR** com ≥ 95% de campos corretos em plaquetas legíveis | R3 |
| RNF-24 | Dispositivos embarcados | Reconexão automática < 30 s; watchdog; identificação de cartão < 1 s; operação contínua de 12 h/dia; firmware assinado e atualizável; consumo e aquecimento dentro da especificação do hardware | R3 |

## 4. Rastreabilidade com os achados do MVP

Os IDs vêm da auditoria interna do MVP (documento mantido fora do repositório).

| Achado no MVP | Requisito ou decisão que impede a repetição |
|---|---|
| Migrations não instalavam em banco vazio | CI: banco vazio → versão atual e N-1 → N; `alembic check` (Volume 09) |
| Datas dependiam do fuso do banco | RNF-16, ADR-015; testes com servidor em fuso ≠ UTC |
| CI sem bloqueio real | Regra de CI sem etapa mascarada (Volume 13) |
| Testes desatualizados e schema criado sem migrations | Volume 09: schema dos testes sempre via migrations |
| Sessão vinculada ao nome de usuário | RF-IAM-02 |
| Sessões não revogadas em troca de senha e logout | RF-IAM-03 |
| Sem limite de tentativas | RF-IAM-07 |
| Upload de imagem sem limite | RF-QR-02 (decodificação no aparelho); ADR-008 (limites antes de processar) |
| Dependências vulneráveis | RNF-08; varredura bloqueante |
| Cabeçalhos de segurança e CSRF | Volume 06 |
| Anexos sem limite e imagens dentro do banco | ADR-008; RF-SUP-04 |
| HTML sem escape em e-mail | Templates com escape automático (Volume 06) |
| QR Code somava estoque sozinho | RF-QR-04, RF-QR-06 |
| Sem movimentações nem auditoria | RF-MOV, RF-AUD |
| Sem restrições no banco | RF-INV-04 |
| NF arredondava quantidades, sem revisão e não atômica | RF-CAT-05, RF-DOC-02..04 |
| QR podia casar com itens diferentes | ADR-011 |
| Pendência de devolução nunca atrasava | RF-EMP-07 |
| Exclusão de usuário com empréstimo aberto | RF-IAM-12 |
| OCR travava a API inteira | ADR-009; RNF-20 |
| E-mail enviado a todos dentro da requisição | RF-NOT-05, RF-NOT-06 |
| Câmera exige HTTPS | ADR-007; validação na R0 |
| Datas exibidas com desvio | ADR-015 |
| Biblioteca de PDF com licença AGPL | ADR-016, RNF-17 |
