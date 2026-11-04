# Matriz de Preservação das Funcionalidades do MVP

**Versão:** 1.0 · **Data:** 03/11/2026
**Objetivo:** garantir que **toda** funcionalidade e ideia do MVP (`lab_almoxarifado`) exista no produto definitivo, em versão mais completa. Nenhuma linha desta matriz pode ser removida sem decisão registrada do responsável pelo produto.
**Fontes inventariadas:** código do backend (37 rotas, `tasks.py`, `email_service.py`, `qr_service.py`), componentes do frontend e os documentos de funcionalidades do MVP (`IMPLEMENTACAO_NOVAS_FUNCIONALIDADES.md`, `UPGRADES_VISAO_NOTAS.md`, `REVISAO-UI-UX.md`, `FRONTEND_LOGIN_CADASTRO_NOTAS_FISCAIS.md`, `ATUALIZACAO_PERFIL_SUPORTE.md`).

Legenda: **Mantida+** = mantida e ampliada · **Redesenhada** = a intenção é mantida, mas a forma muda por motivo técnico explicado.

---

## 1. Conta, acesso e perfil

| # | Funcionalidade no MVP | Situação | Como fica no definitivo | Requisitos |
|---|---|---|---|---|
| 1.1 | Login com usuário e senha, sessão em cookie HttpOnly | Mantida+ | Usuário **ou e-mail**; sessão revogável no servidor; MFA para papéis privilegiados; passkeys | RF-IAM-01, 02, 04, 05 |
| 1.2 | Logout | Mantida+ | Encerra de verdade a sessão no servidor; "sair de todos os dispositivos" | RF-IAM-03, 09 |
| 1.3 | Autocadastro na tela de login (nome, setor, usuário, e-mail, senha, confirmação) | Mantida+ | Convite como padrão; autocadastro ativável por política, com domínio de e-mail permitido e aprovação do administrador | RF-IAM-08, RF-POL-01 |
| 1.4 | Política de senha (8+ caracteres, letra e número) | Mantida+ | Argon2id, mínimo de 10 caracteres, checagem contra senhas vazadas e medidor de força | RF-IAM-01 |
| 1.5 | Meu perfil: resumo de identidade, dados pessoais em modo leitura/edição, username só leitura | Mantida+ | Igual, mais preferências de notificação, idioma e lista de dispositivos conectados | RF-IAM-11, 09 |
| 1.6 | Troca de senha com senha atual, confirmação e validação | Mantida+ | Igual, e encerra as outras sessões | RF-IAM-03 |
| 1.7 | Foto de perfil (PNG/JPEG/WebP até 2 MB) com **enquadramento por arrasto e zoom** e prévia circular | Mantida+ | Recorte no aparelho; servidor detecta o tipo real, remove metadados (EXIF/localização) e gera tamanhos otimizados; arquivo fora do banco | RF-IAM-11, ADR-008 |
| 1.8 | Foto do usuário exibida no cabeçalho e nas mensagens de suporte | Mantida+ | Avatar em todo o app (cabeçalho, chamados, empréstimos, auditoria) | RF-IAM-11 |
| 1.9 | Alteração do próprio setor | Mantida+ | Configurável por política (livre ou com aprovação) | RF-IAM-11 |
| 1.10 | Autodesativação de conta com senha, protegendo o último administrador | Mantida+ | Solicitação de encerramento de conta pelo titular (LGPD), com anonimização e a mesma proteção | RF-IAM-13 |
| 1.11 | Proteção contra lockout: admin não desativa/exclui a si mesmo; sempre resta um admin | Mantida+ | Invariante "sempre existe ao menos um Proprietário ativo com MFA", no serviço e em teste | RF-IAM-10 |

## 2. Usuários e permissões (administração)

| # | Funcionalidade no MVP | Situação | Como fica no definitivo | Requisitos |
|---|---|---|---|---|
| 2.1 | Listar usuários com setor e status | Mantida+ | Busca, filtros (papel, setor, status, MFA ativo), paginação, exportação | RF-IAM-10, RF-REL-03 |
| 2.2 | Editar usuário (nome, e-mail, username, setor) | Mantida+ | Com auditoria antes/depois; username mudado não afeta sessões (sessão usa ID interno) | RF-IAM-10, RF-AUD-01 |
| 2.3 | Reset de senha pelo administrador | Redesenhada | O administrador **envia link de redefinição** (não vê nem escolhe a senha); recuperação também pelo próprio usuário | RF-IAM-06 |
| 2.4 | Desativar e reativar usuário, com confirmação | Mantida+ | Desativação encerra as sessões na hora | RF-IAM-03 |
| 2.5 | Excluir usuário preservando o histórico de empréstimos | Redesenhada | Nunca apaga quem tem histórico: anonimiza; bloqueia se houver empréstimo em aberto (corrige INT-07) | RF-IAM-12 |
| 2.6 | Cadastrar administrador (só por outro admin) | Mantida+ | Papéis granulares (Proprietário, Administrador, Gestor, Operador, Atendente, Auditor, Solicitante) com escopo por almoxarifado; MFA obrigatório | RF-IAM-10, RF-IAM-04 |
| 2.7 | Setores fixos semeados por migration | Redesenhada | Setores configuráveis por cliente (cada organização tem os seus) | RF-ORG-02 |

## 3. Catálogo, estoque e itens

| # | Funcionalidade no MVP | Situação | Como fica no definitivo | Requisitos |
|---|---|---|---|---|
| 3.1 | Cadastro de item: nome, patrimônio, código QR, área, setor, quantidade | Mantida+ | Separado em **item de catálogo** (tipo) + **unidades físicas** (patrimônio, série) ou **saldo** (consumível/lote); fotos, datasheet, fabricante, modelo, unidade de medida | RF-CAT-01..05, RF-INV-01 |
| 3.2 | Editar item com valores atuais, limpar campos opcionais | Mantida+ | Edição de cadastro com controle de concorrência (dois admins editando ao mesmo tempo) | RF-CAT-01, ADR-006 |
| 3.3 | Quantidade total não pode ficar abaixo do emprestado | Redesenhada | Quantidade não é editada: muda por **ajuste com motivo** (movimentação), com aprovação acima de limite | RF-MOV-02, 05, 07 |
| 3.4 | Desativar/reativar item; remover só sem histórico | Mantida+ | Estados explícitos (DISPONIVEL, EM_MANUTENCAO, BAIXADO, PERDIDO...); baixa com motivo; nada com histórico é apagado | RF-INV-02, RF-MOV-02 |
| 3.5 | Catálogo do membro mostra só itens ativos com disponibilidade | Mantida+ | Catálogo com busca, filtros, fotos, disponibilidade por almoxarifado e "previsão de devolução" | RF-CAT-06 |
| 3.6 | Painel de estoque: contadores, abas inventário/cadastro, busca sem acento (nome, patrimônio, QR, área, setor, ID), filtros por status/setor, ordenação, paginação, disponibilidade visual, edição em modal, confirmações | Mantida+ | Tudo mantido, com busca no servidor (escala), filtros salvos, visualização em tabela (notebook) e cartões (celular) | RF-CAT-06, RNF-02 |
| 3.7 | "Área" (texto livre) e "setor atual" do item | Redesenhada | **Localizações hierárquicas** com etiqueta QR própria (prédio › sala › armário › prateleira › gaveta) | RF-ORG-04 |
| 3.8 | Visão geral do admin: saúde do estoque, itens inativos, setores com itens, disponibilidade geral | Mantida+ | Painel com indicadores reconciliados, estoque mínimo, curva de uso e tendências | RF-REL-01 |

## 4. Empréstimos

| # | Funcionalidade no MVP | Situação | Como fica no definitivo | Requisitos |
|---|---|---|---|---|
| 4.1 | Solicitar empréstimo escolhendo item, quantidade e dias (1–30) | Mantida+ | Carrinho com vários itens; unidades específicas ou quantidade; prazo por política; reservas futuras | RF-EMP-01, 02, 08 |
| 4.2 | Empréstimo vinculado sempre ao usuário autenticado | Mantida+ | Igual; o operador pode registrar retirada em nome de alguém **com registro de quem operou** | RF-EMP-03, RF-MOV-04 |
| 4.3 | Proteção contra estoque negativo sob concorrência | Mantida+ | Constraints no banco + idempotência + testes concorrentes no CI | RF-INV-04, RF-MOV-06 |
| 4.4 | Prazo com 1 dia de tolerância; status ATRASADO calculado dinamicamente | Mantida+ | Tolerância configurável; prazos em UTC com fuso da organização (corrige AUD-002); pendências também atrasam (corrige INT-06) | RF-EMP-07, RF-POL-04 |
| 4.5 | Devolução em duas etapas: membro solicita, admin confirma no recebimento | Mantida+ | Vira política configurável (ligada por padrão), com devolução parcial, ocorrências (dano/falta/perda) e fotos | RF-EMP-04, 05, RF-POL-03 |
| 4.6 | Admin força devolução de qualquer empréstimo | Mantida+ | Operador/Gestor registra o recebimento, com auditoria | RF-EMP-04 |
| 4.7 | Meus empréstimos (só do próprio usuário), com estados vazios e erro recuperável | Mantida+ | Linha do tempo de cada empréstimo, renovação, comentários com o almoxarifado | RF-EMP-06, RF-COL-01 |
| 4.8 | Lista de empréstimos do admin, paginada, com quem pegou, setor, retirada e prazo | Mantida+ | Filtros (status, atraso, pessoa, item, período), exportação, ações em lote | RF-REL-02, 03 |
| 4.9 | Banner de empréstimos atrasados ao abrir o painel | Mantida+ | Indicador em tempo real + central de notificações + relatório de atrasos | RF-NOT-01, RF-REL-01 |

## 5. QR Code e visão computacional

| # | Funcionalidade no MVP | Situação | Como fica no definitivo | Requisitos |
|---|---|---|---|---|
| 5.1 | Leitor por câmera no navegador com **seleção de câmera** (integrada, USB, traseira) e preferência pela traseira | Mantida+ | Igual, mais lanterna, zoom quando suportado, troca rápida de câmera e leitor USB/Bluetooth | RF-QR-02, 03 |
| 5.2 | Moldura de leitura (ROI) e dica "mantenha o QR no retângulo" | Mantida+ | Guia visual adaptado ao tamanho da tela; leitura de vários formatos | RF-QR-02 |
| 5.3 | Detecção local com `BarcodeDetector` para não enviar o mesmo QR repetidamente | Mantida+ | Toda decodificação no aparelho (BarcodeDetector + zxing-wasm); **idempotência também no servidor** | RF-QR-02, 06 |
| 5.4 | Leitura robusta de QR pequeno, inclinado e com pouca luz (variações de escala, rotação, contraste) | Mantida+ | Mesmo objetivo no aparelho; métricas de taxa de sucesso; regras de tamanho mínimo e correção de erro na etiqueta | RF-QR-07, `ESTRATEGIA_QR_CODE.md` |
| 5.5 | Fallback OCR do texto impresso no cartão (`AVT-...`) | Redesenhada | Etiqueta com **código curto legível** para digitação manual e busca; OCR deixa de ser necessário para identificar | RF-QR-03 |
| 5.6 | Painel de leitura: estado da câmera, processamento, confirmação visual, aviso flutuante | Mantida+ | Feedback visual, sonoro e por vibração; ficha do objeto com ações contextuais | RF-QR-04 |
| 5.7 | Histórico dos últimos 12 eventos de leitura | Mantida+ | "Sessão de leitura" listando tudo o que foi escaneado, com desfazer antes de confirmar; métricas persistidas sem imagem | RF-QR-10 |
| 5.8 | Amostra da imagem capturada como evidência visual | Redesenhada | Evidência é a **movimentação auditada** (quem, quando, dispositivo); foto só quando o usuário anexa (ex.: ocorrência de dano) — evita guardar imagens à toa (LGPD) | RF-AUD-01, RF-EMP-05 |
| 5.9 | Entrada automática: leitura de item existente soma +1 ao estoque | Redesenhada | **Leitura identifica, não conta.** Entradas são ações confirmadas; em lote, o modo "recebimento" conta unidades com confirmação (corrige INT-01) | RF-QR-04, 10 |
| 5.10 | QR com JSON (nome, patrimônio, setor) cria item novo automaticamente | Redesenhada | QR desconhecido abre **cadastro assistido**; nenhum dado de negócio dentro do QR | RF-QR-05, ADR-011 |
| 5.11 | Notificação por e-mail quando item é cadastrado por QR | Mantida+ | Ver 7.4 | RF-NOT-06 |
| 5.12 | Geração de QR por item com pré-visualização, download PNG e impressão | Mantida+ | Etiquetas em lote (folhas A4 padrão Pimaco, impressoras térmicas), etiquetas pré-impressas para vincular depois, reimpressão e revogação | RF-QR-07, 08, 11 |

## 6. Notas fiscais e documentos

| # | Funcionalidade no MVP | Situação | Como fica no definitivo | Requisitos |
|---|---|---|---|---|
| 6.1 | Importação de produtos do XML oficial da NF-e | Mantida+ | Processada no **servidor** com parser seguro; chave de acesso, emitente, itens, unidades e valores | RF-DOC-01 |
| 6.2 | Extração de produtos de PDF/DANFE com texto e OCR para digitalizados | Mantida+ | No worker, em segundo plano, com timeout; sempre "não verificado"; biblioteca de PDF com licença compatível com venda (ADR-016) | RF-DOC-06 |
| 6.3 | Visualização de PDF e imagem da nota | Mantida+ | Documento anexado à entrada, visualizável a qualquer momento | RF-DOC-07 |
| 6.4 | Tabela de revisão antes de importar; escolha de setor e área de destino | Mantida+ | **Rascunho editável**: mapear cada linha a um item de catálogo, corrigir quantidade/unidade/fator de conversão, escolher local; memória de mapeamento por fornecedor | RF-DOC-03, 05 |
| 6.5 | Relatório de sucesso/falha por produto | Mantida+ | Confirmação atômica (tudo ou nada) com validação prévia de cada linha | RF-DOC-04 |
| 6.6 | Histórico persistente de notas (arquivo, tipo, responsável, produtos, total cadastrado) | Mantida+ | Vinculado às movimentações geradas; deduplicação por chave de acesso; filtros e exportação | RF-DOC-02, 04 |
| 6.7 | Avisos explícitos: extração é aproximada, não é validação SEFAZ | Mantida+ | Mantidos na interface e no manual | RF-DOC-08 |

## 7. Comunicação, suporte e notificações

| # | Funcionalidade no MVP | Situação | Como fica no definitivo | Requisitos |
|---|---|---|---|---|
| 7.1 | Central de suporte: usuário abre chamado (assunto, descrição) | Mantida+ | Categorias, prioridade, vínculo a item/empréstimo; **mensagens em tempo real** entre usuário e equipe de suporte | RF-SUP-01..03 |
| 7.2 | Até 4 imagens anexadas (1 MB cada), com miniaturas | Mantida+ | Imagens e PDFs, limites por arquivo e por chamado, compressão no aparelho, arquivos fora do banco | RF-SUP-04, ADR-008 |
| 7.3 | Histórico da conversa com foto e nome de quem escreveu | Mantida+ | Conversa em tempo real, indicador de lida, notas internas visíveis só para a equipe | RF-SUP-03, 05 |
| 7.4 | Usuário conclui, reabre ou informa "ainda não resolvido" | Mantida+ | Ciclo completo: Aberto → Em atendimento → Aguardando usuário → Resolvido → Fechado (com reabertura); avaliação do atendimento | RF-SUP-06, 09 |
| 7.5 | Painel do admin separa chamados ativos e concluídos; foto do membro | Mantida+ | Fila com filtros, atribuição a atendente, prazos de resposta (SLA), respostas prontas | RF-SUP-07, 08 |
| 7.6 | E-mail lembrete 1 dia antes do prazo (uma vez) | Mantida+ | Lembretes configuráveis (ex.: 3 dias e 1 dia), por e-mail, push e no app | RF-NOT-02, 03, 04 |
| 7.7 | E-mail de atraso no máximo 1 vez por dia, reenviando após falha temporária | Mantida+ | Mesmo controle, via outbox com deduplicação e retry; escalonamento ao gestor após N dias | RF-NOT-04, 05 |
| 7.8 | E-mail para todos quando um item novo é cadastrado | Redesenhada | "Novidades do catálogo" como **resumo opcional** (diário/semanal) por preferência do usuário — evita uma enxurrada de e-mails (corrige PERF-02) | RF-NOT-06 |
| 7.9 | SMTP configurável (Gmail com senha de app) | Mantida+ | Configuração pelo painel com teste de envio; credencial protegida | RF-ADM-02 |

## 8. Experiência, interface e operação

| # | Funcionalidade no MVP | Situação | Como fica no definitivo | Requisitos |
|---|---|---|---|---|
| 8.1 | Navegação lateral por áreas (Visão geral, Estoque, Leitor QR, Notas, Empréstimos, Usuários, Suporte) com **busca na navegação** | Mantida+ | Navegação por papel; paleta de comandos (Ctrl+K) no notebook; barra inferior no celular | RF-APP-06 |
| 8.2 | Atalhos de tarefas frequentes ("Acesso rápido") | Mantida+ | Botão de ação principal "Escanear" sempre à mão no celular; atalhos configuráveis | RF-APP-06 |
| 8.3 | Indicador de conexão/sincronização e atualização manual | Mantida+ | Atualização em tempo real; indicador online/offline; catálogo em modo leitura offline | RF-APP-04, 05 |
| 8.4 | Estados de carregamento, vazio, erro com "tentar novamente" | Mantida+ | Obrigatórios em todas as telas (Guia §7.3) | RNF-03 |
| 8.5 | Responsividade: tabela vira cartões no celular; redução de movimento; foco visível; ARIA em abas e diálogos; Escape fecha modal | Mantida+ | WCAG 2.2 AA verificado por teste automático e manual | RNF-02, 03 |
| 8.6 | Rótulos de status legíveis e formatação de datas centralizada | Mantida+ | i18n completo e função única de datas com testes | RNF-14, 15 |
| 8.7 | Visual de login/cadastro moderno (azul/índigo) e identidade "AVANTE" | Mantida+ | Design system próprio com tema claro/escuro e **marca do cliente** (logotipo) | RF-ORG-01, RF-APP-07 |
| 8.8 | Envelope de erro padronizado com `request_id` | Mantida+ | Códigos de erro de domínio estáveis e mensagens acionáveis | ADR-010 |
| 8.9 | Avisos operacionais nos documentos ("faça backup", "não use `down -v`") | Redesenhada | Backup automático, atualização com backup prévio e rollback; comandos destrutivos protegidos | RF-ADM-03, 05, ADR-013 |

---

**Verificação desta matriz:** cada linha aponta para um requisito existente no `PLANO_MESTRE_DESENVOLVIMENTO.md` v2.3. A Fase 12 inclui um checklist de aceite que percorre esta matriz linha a linha no ambiente de homologação.
