# Especificação de UI, UX e Design System — Avante Almoxarifado

**Versão:** 1.1 · **Data:** 03/11/2026 — 1.1: marca Avante Tech Jr aplicada (§6.4), participantes dos testes definidos (§17), UX-DA-01 e UX-DA-05 resolvidas
**Relação:** parte do conjunto de governança do produto definitivo. Detalha RF-APP, RNF-03, RNF-04, RNF-18 e RNF-19 do `PLANO_MESTRE_DESENVOLVIMENTO.md` v2.3, a ADR-021 e o RF-APP-09.
**Vale para:** todas as telas, em celular, tablet e notebook, nos temas claro e escuro.
**Regra de ouro:** nenhuma tela entra em produção sem cumprir a Definição de Pronto de UI (§18).

---

## 1. Objetivo

O almoxarifado é usado **em pé, no balcão, com um item na mão**, e também **sentado, no notebook, conferindo uma nota fiscal de 40 linhas**. A experiência precisa ser excelente nos dois extremos. Esta especificação define:
- como o aplicativo **se comporta** (princípios, padrões de interação e fluxos);
- como ele **se parece** (design system: tokens, componentes, tipografia, cores, movimento);
- como a qualidade é **medida** (métricas, testes e checklists).

## 2. Princípios de experiência

Cada princípio vem com regras verificáveis.

| # | Princípio | Regras |
|---|---|---|
| P1 | **Tarefa primeiro** | A ação mais frequente de cada papel fica a no máximo 1 toque da tela inicial. No celular, "Escanear" está sempre visível. Telas de tarefa não têm decoração que concorra com a ação. |
| P2 | **Confiança acima de rapidez** | Operações de estoque mostram um resumo antes de confirmar e o resultado real do servidor depois. **Nunca** há UI otimista para estoque, empréstimo ou documento: o "pronto" só aparece quando o servidor confirmou. |
| P3 | **Sempre se sabe o que está acontecendo** | Toda ação dá retorno em até 100 ms (visual, sonoro ou vibração). Operações acima de 1 s mostram progresso; acima de 10 s viram tarefa em segundo plano, com notificação ao terminar. |
| P4 | **Errar é seguro** | O que pode ser desfeito tem "Desfazer". O que não pode ter confirmação explícita. Formulários nunca perdem dados por erro, queda de conexão ou navegação acidental. |
| P5 | **O mesmo app em qualquer tela** | Mesmos nomes, ícones, cores e fluxos no celular, tablet e notebook; o layout se adapta, o modelo mental não muda. |
| P6 | **Acessível por padrão** | WCAG 2.2 AA é requisito de entrada, não melhoria posterior. Teclado, leitor de tela, zoom de 200% e alto contraste funcionam em todos os fluxos. |
| P7 | **Linguagem do almoxarifado** | Termos do glossário (§12.2), nunca jargão técnico ("erro 422", "payload", "token"). |
| P8 | **Calmo e profissional** | Interface limpa, densidade adequada ao aparelho, cor usada para significado, não para enfeite. Sem emojis como ícones, sem animações gratuitas. |
| P9 | **Rápido de verdade** | Desempenho é parte do design: orçamentos do §15 são critério de aceite. |

## 3. Usuários e contextos de uso

### 3.1 Contextos
| Contexto | Aparelho | Condições | Implicações de design |
|---|---|---|---|
| Balcão do almoxarifado | Celular do operador, tablet fixo ou notebook com leitor USB | Em pé, uma mão ocupada, fila, iluminação variável | Alvos grandes, ações principais no alcance do polegar (metade inferior da tela), leitura contínua, retorno sonoro e vibração |
| Bancada do laboratório | Celular do solicitante | Mãos sujas ou com luvas, atenção dividida | Poucos campos, botões grandes, voz do sistema curta |
| Mesa do gestor | Notebook, tela de 13–15" ou monitor externo | Tarefas longas: NF-e, relatórios, usuários | Densidade alta, tabelas, atalhos de teclado, painéis lado a lado |
| Fora do laboratório | Celular via VPN/túnel | Rede lenta ou instável | Leitura offline, carregamento leve, estados de conexão claros |
| Inventário | Vários celulares/tablets ao mesmo tempo | Repetitivo, longo, em corredores | Modo de leitura em sequência, progresso visível, retomada após interrupção |

### 3.2 Tarefas principais por papel e metas
| Papel | Tarefa | Meta (usuário treinado) |
|---|---|---|
| Solicitante | Solicitar empréstimo de 1 item pelo celular | ≤ 4 toques após encontrar o item; ≤ 30 s |
| Solicitante | Ver o que está comigo e quando devolvo | 1 toque a partir da tela inicial |
| Solicitante | Abrir chamado de suporte com foto | ≤ 60 s |
| Operador | Registrar retirada de 1 item escaneando | ≤ 10 s do escaneamento à confirmação |
| Operador | Receber devolução de 3 itens | ≤ 30 s |
| Gestor | Dar entrada em NF-e de 20 itens já mapeados | ≤ 3 min |
| Gestor | Aprovar uma solicitação | ≤ 2 toques a partir da notificação |
| Atendente | Responder um chamado | ≤ 2 toques a partir da notificação |
| Administrador | Convidar um usuário com papel | ≤ 60 s |

As metas são validadas nos testes de usabilidade (§17) e revisadas após o piloto.

## 4. Arquitetura de informação

### 4.1 Mapa de navegação (o conteúdo depende das permissões)
```
Início (painel do papel)
├── Escanear  ← ação global
├── Catálogo ─── Item ─── Unidade
├── Empréstimos ─── Meus | Solicitações (aprovar) | Ativos | Atrasados | Reservas
├── Estoque ─── Saldos | Movimentações | Entradas (NF-e) | Transferências | Inventários | Locais
├── Suporte ─── Meus chamados | Fila da equipe
├── Relatórios
├── Notificações
├── Perfil ─── Dados | Segurança (senha, MFA, dispositivos) | Preferências
└── Administração ─── Usuários e papéis | Organização (setores, almoxarifados, políticas) | Etiquetas | Integrações (e-mail) | Sistema (saúde, backup, licença, atualizações) | Auditoria
```

### 4.2 URLs
- Toda tela tem URL própria, legível e compartilhável: `/catalogo/itens/:id`, `/emprestimos?status=atrasado`.
- Filtros, ordenação e aba ativa ficam na URL. Copiar o link reproduz a mesma visão para quem tem permissão.
- `/q/:codigo` resolve etiquetas QR (`ESTRATEGIA_QR_CODE.md`).
- Voltar do navegador sempre funciona como o usuário espera; modais com estado relevante (ex.: ficha aberta pelo QR) têm URL.

### 4.3 Busca global
- Um campo resolve item, unidade (patrimônio/série), local, pessoa, empréstimo e chamado, com resultados agrupados por tipo.
- Notebook: `Ctrl+K` / `Cmd+K` abre a **paleta de comandos** (busca + ações: "Nova entrada", "Convidar usuário").
- Celular: ícone de busca no topo; o código digitado de uma etiqueta é reconhecido e abre a ficha direto.

## 5. Layout responsivo

### 5.1 Pontos de quebra (tokens únicos; substituem os 9 pontos diferentes do MVP)
| Token | Largura | Aparelhos típicos | Navegação |
|---|---|---|---|
| `xs` | 0–479 px | Celulares | Barra inferior com 4 destinos + botão central "Escanear" |
| `sm` | 480–767 px | Celulares grandes, paisagem | Barra inferior |
| `md` | 768–1023 px | Tablets em retrato | **Trilho de navegação** lateral (ícones + rótulos curtos) |
| `lg` | 1024–1439 px | Tablets em paisagem, notebooks | Barra lateral recolhível + barra superior |
| `xl` | ≥ 1440 px | Notebooks grandes, monitores | Barra lateral fixa; painéis lado a lado (lista + detalhe) |

Componentes internos usam **container queries** (se adaptam ao espaço disponível, não à tela inteira), para que o mesmo cartão funcione em uma coluna estreita do notebook e na tela cheia do celular.

### 5.2 Padrões por classe de aparelho
| Elemento | Celular | Tablet | Notebook |
|---|---|---|---|
| Navegação principal | Barra inferior: Início, Catálogo, **Escanear** (central, destacado), Empréstimos, Menu | Trilho lateral | Barra lateral com grupos, busca e atalhos |
| Listas de dados | Cartões com as 3–4 informações essenciais e ação principal | Cartões em 2 colunas ou tabela compacta | Tabela com colunas configuráveis, ordenação, seleção múltipla |
| Detalhe | Tela própria | Painel lateral | Painel lateral ou lado a lado com a lista |
| Formulários | Uma coluna, botões fixos no rodapé | Uma ou duas colunas | Duas colunas quando houver relação entre campos |
| Filtros | Folha inferior (bottom sheet) + chips de filtros ativos | Painel lateral | Barra de filtros acima da tabela |
| Diálogos | Folha inferior em tela cheia ou parcial | Diálogo central | Diálogo central |
| Ações secundárias | Menu "⋯" | Menu "⋯" | Botões visíveis + menu |

### 5.3 Regras gerais de layout
- Largura de leitura máxima de 72 caracteres para textos corridos.
- Respeitar as **áreas seguras** (`env(safe-area-inset-*)`): entalhe, cantos arredondados e barra de gestos do celular.
- Retrato e paisagem funcionam em todos os aparelhos; em paisagem no celular, o leitor de QR usa a tela inteira.
- Nada depende de *hover*: toda informação revelada por hover também está acessível por toque e teclado.
- Sem rolagem horizontal da página de 320 px a 2560 px (RNF-03). Tabelas largas rolam dentro do próprio contêiner, com a primeira coluna fixa.

## 6. Design system

### 6.1 Arquitetura de tokens
Três camadas, com uma única fonte da verdade em JSON no repositório (`frontend/design-tokens/`), convertida para variáveis CSS e para a configuração do Tailwind pelo **Style Dictionary** (Apache-2.0):
1. **Primitivos:** escala de cores, tamanhos e tempos (`blue-700`, `space-4`, `duration-200`).
2. **Semânticos:** significado (`color-action-primary`, `color-text-secondary`, `color-status-loaned-bg`).
3. **De componente:** uso específico (`button-primary-bg`, `input-border-focus`).

Componentes **só** usam tokens semânticos ou de componente. Um lint (Stylelint + regra de ESLint para classes) bloqueia cores e tamanhos soltos no código.

### 6.2 Cores — tema claro
Herdam a identidade do MVP (azul-marinho, azul de ação e índigo). Todas as combinações abaixo foram **calculadas** contra WCAG 2.2 (texto ≥ 4,5:1, componentes de interface ≥ 3:1), e o cálculo roda no CI a cada mudança de token.

| Token semântico | Valor | Uso | Contraste verificado |
|---|---|---|---|
| `bg-canvas` | `#F5F7FA` | Fundo da aplicação | — |
| `bg-surface` | `#FFFFFF` | Cartões, painéis, diálogos | — |
| `text-primary` | `#0F172A` | Texto principal | 17,85:1 em `#FFFFFF`; 16,63:1 em `#F5F7FA` |
| `text-secondary` | `#475569` | Texto de apoio | 7,58:1 / 7,06:1 |
| `text-tertiary` | `#64748B` | Metadados, placeholders de exemplo | 4,76:1 em `#FFFFFF` (não usar sobre `bg-canvas` para texto essencial) |
| `brand-navy` | `#10243E` | Barra lateral, cabeçalho de marca | Branco sobre ela: 15,63:1 |
| `action-primary` | `#1D4ED8` | Botão principal, links, seleção | Branco sobre ela: 6,70:1; como link em branco: 6,70:1 |
| `action-primary-hover` | `#1E40AF` | Hover/pressionado | Branco sobre ela: 8,72:1 |
| `accent` | `#3730D9` | Destaques pontuais (novidades, marca) | 8,12:1 em branco |
| `focus-ring` | `#2563EB` | Anel de foco (2 px + 2 px de afastamento) | 5,17:1 em branco |
| `border-control` | `#64748B` | Borda de campos e controles | 4,76:1 (mínimo 3:1) |
| `border-subtle` | `#E2E8F0` | Divisórias decorativas (nunca a única indicação de um controle) | — |
| `danger` | `#B91C1C` | Botão destrutivo | Branco sobre ela: 6,47:1 |

**Estados de feedback e de objetos do almoxarifado** (chip = fundo claro + texto escuro + ícone; **nunca só cor**):
| Estado | Texto / fundo | Ícone (Lucide) | Contraste |
|---|---|---|---|
| Sucesso · Disponível | `#166534` / `#DCFCE7` | `check-circle-2` | 6,49:1 |
| Emprestado | `#1E40AF` / `#DBEAFE` | `arrow-up-right` | 7,15:1 |
| Reservado | `#5B21B6` / `#EDE9FE` | `calendar-clock` | 7,57:1 |
| Alerta · Em manutenção · Atenção | `#92400E` / `#FEF3C7` | `wrench` / `alert-triangle` | 6,37:1 |
| Em conferência | `#115E59` / `#CCFBF1` | `clipboard-check` | 6,73:1 |
| Erro · Perdido · Atrasado | `#991B1B` / `#FEE2E2` | `alert-octagon` / `clock-alert` | 6,80:1 |
| Informação | `#075985` / `#E0F2FE` | `info` | 6,59:1 |
| Baixado · Inativo | `#334155` / `#E2E8F0` | `archive` | 8,40:1 |

### 6.3 Cores — tema escuro
Não é a inversão do claro: superfícies em camadas de azul-escuro, saturação reduzida e cores de estado clareadas.
| Token | Valor | Contraste verificado |
|---|---|---|
| `bg-canvas` | `#0B1220` | — |
| `bg-surface` | `#111A2B` | — |
| `bg-surface-raised` | `#18233A` | — |
| `text-primary` | `#E6EBF2` | 15,63:1 sobre `#0B1220` |
| `text-secondary` | `#A7B3C4` | 8,20:1 sobre `#111A2B` |
| `action-primary` | `#60A5FA` (texto do botão `#0B1220`) | 7,36:1 |
| `focus-ring` | `#93C5FD` | 10,38:1 |
| `border-control` | `#64748B` | 3,66:1 sobre `#111A2B` |
| Sucesso / Alerta / Erro (texto) | `#4ADE80` / `#FBBF24` / `#F87171` | 9,99 / 10,43 / 6,29:1 sobre `#111A2B` |

Escolha do tema: Sistema (padrão), Claro ou Escuro, salva no perfil. O modo **alto contraste do Windows** (`forced-colors`) é respeitado: bordas e foco continuam visíveis usando cores do sistema.

### 6.4 Marca do produto: Avante Almoxarifado, da Avante Tech Jr
**Nome exibido:** "Avante Almoxarifado" (título das páginas, manifest do app, e-mails, etiquetas). **Logotipo:** logo da **Avante Tech Jr**, sem fundo. Nome, logo, ícones e cores de marca ficam num único ponto de configuração (RF-APP-09): se o produto for vendido com outro nome, a troca não mexe em componentes.

**Arquivos da marca** (pasta `brand/`, gerados a partir da imagem enviada em 03/11/2026):
| Arquivo | Uso |
|---|---|
| `logo-avantetechjr-ciano.svg/.png` | Logo completa sobre fundos escuros: barra lateral azul-marinho, tela de login, tema escuro, splash |
| `logo-avantetechjr-navy.svg/.png` | Logo completa sobre fundos claros (tema claro, e-mails, PDFs, etiquetas) |
| `logo-avantetechjr-branca.svg/.png` | Sobre o azul de ação ou fotos escuras |
| `simbolo-avante-{ciano,navy,branca}.svg/.png` | Só o símbolo "A": cabeçalho compacto no celular, favicon, etiquetas QR pequenas |
| `icone-app-512.png`, `icone-app-192.png`, `icone-app-maskable-512.png`, `favicon-32.png` | Ícone do app instalado (símbolo ciano sobre o degradê da marca) |

**Tokens de marca** (contraste calculado):
| Token | Valor | Uso | Contraste |
|---|---|---|---|
| `brand-cyan` | `#13F1FC` | Logo e símbolo sobre fundos escuros; detalhes decorativos no tema escuro | 11,17:1 sobre `#10243E`; 13,39:1 sobre `#0B1220`; **1,40:1 sobre branco — proibido em fundo claro** |
| `brand-gradient` | `#191256` → `#312EB9` (horizontal) | Fundo do ícone do app, splash e painel visual do login | Ciano sobre ele: 11,90:1 a 6,76:1; branco: 16,64:1 a 9,45:1 |
| `brand-navy` | `#10243E` | Barra lateral, logo no tema claro | (já definido em §6.2) |

**Regras de uso da logo:** usar sempre um dos arquivos acima, nunca recriar ou redesenhar; ciano só sobre fundo escuro; navy sobre fundo claro; área de respiro mínima igual à altura do "T" de "TECH" em volta; tamanho mínimo da logo completa 96 px de largura (abaixo disso, usar só o símbolo); não distorcer, girar, aplicar sombra ou trocar cores; o ciano da marca **não** é cor de interface (botões e links continuam com `action-primary`).

**Limitação conhecida:** a imagem enviada tem 437 px. Nessa resolução, as trilhas de circuito do símbolo têm cerca de 1 px e não podem ser vetorizadas com fidelidade. Por isso os arquivos usam o **símbolo simplificado, sem as trilhas** (o texto foi preservado). Quando o arquivo vetorial original (SVG/AI/PDF) da Avante Tech Jr for obtido, ele substitui esses arquivos sem nenhuma mudança de código.

### 6.4.1 Marca do cliente (white-label, para a venda futura)
- O cliente envia o **logotipo** (SVG ou PNG ≥ 512 px), que aparece no cabeçalho, no login, nos e-mails, nas etiquetas e no ícone do app instalado.
- O cliente pode escolher uma **cor de destaque**. O sistema gera as variações e **valida o contraste automaticamente**; se a cor não atingir 4,5:1 com texto branco, ela é escurecida até atingir, com prévia. A marca do cliente nunca quebra a acessibilidade.
- Cores de estado (sucesso, erro etc.) não são personalizáveis, para manter o significado.

### 6.5 Tipografia
| Item | Definição |
|---|---|
| Família | **Inter** (variável, licença OFL-1.1, servida pelo próprio servidor — sem chamadas a serviços externos), com pilha de sistema como reserva |
| Códigos e números de patrimônio | **JetBrains Mono** (OFL-1.1) |
| Números em tabelas e quantidades | Algarismos tabulares (`font-variant-numeric: tabular-nums`) para alinhar colunas |
| Tamanho mínimo de corpo | **16 px** no celular (também evita o zoom automático do iPhone ao focar campos); 14 px permitido em tabelas densas no notebook |
| Escala | 12 · 14 · 16 · 18 · 20 · 24 · 30 · 36 px (`text-xs` … `text-4xl`) |
| Altura de linha | 1,5 para corpo; 1,25 para títulos |
| Pesos | 400 (corpo), 500 (rótulos), 600 (títulos e botões), 700 (números de destaque) |
| Unidades | `rem`, para respeitar o tamanho de fonte escolhido pelo usuário; layout testado com fonte do sistema a 200% |

### 6.6 Espaçamento, forma e profundidade
| Token | Valores |
|---|---|
| Espaçamento (grade de 4 px) | 0 · 4 · 8 · 12 · 16 · 20 · 24 · 32 · 40 · 48 · 64 |
| Raios (substituem os 8/9/10/12/16 px misturados do MVP) | `sm` 6 px (chips, campos) · `md` 10 px (botões, cartões) · `lg` 16 px (diálogos, folhas) · `full` (avatares, pílulas) |
| Elevação | `0` plano · `1` cartões (sombra sutil) · `2` menus e popovers · `3` diálogos e folhas; no tema escuro a elevação usa superfícies mais claras, não sombras |
| Camadas (z-index) | base 0 · cabeçalho fixo 10 · barra inferior 20 · menus 30 · folhas/diálogos 40 · avisos (toasts) 50 |
| Alvos de toque | Mínimo **44 × 44 px** (acima dos 24 px exigidos pelo WCAG 2.5.8); 8 px entre alvos adjacentes |

### 6.7 Iconografia e ilustração
- Biblioteca única: **Lucide** (ISC), traço 1,75, tamanhos 16/20/24 px.
- Ícones de navegação sempre acompanhados de rótulo; ícones sozinhos só para ações universais (fechar, buscar, mais opções), sempre com `aria-label` e dica.
- **Sem emojis como ícones** (o MVP usava ⚠️, ▦, ✓).
- Ilustrações só em estados vazios e no onboarding: estilo de linha, duas cores da paleta, sem pessoas realistas, adaptadas ao tema escuro.

### 6.8 Movimento
| Token | Duração | Uso |
|---|---|---|
| `instant` | 100 ms | Pressionar botão, alternar estado |
| `fast` | 150 ms | Hover, aparecer dicas |
| `base` | 200 ms | Abrir menus, trocar abas |
| `slow` | 300 ms | Folhas inferiores, diálogos, painéis laterais |

- Curvas: `ease-out` para entrar, `ease-in` para sair, `ease-in-out` para mudança de posição.
- Movimento serve para **mostrar de onde as coisas vêm e para onde vão** (folha sobe do rodapé, painel desliza da lateral), nunca para enfeite.
- `prefers-reduced-motion`: substitui deslocamentos por troca de opacidade e desliga o brilho animado dos esqueletos.
- Nenhuma animação bloqueia a interação; nada pisca mais de 3 vezes por segundo.

### 6.9 Som e vibração (leitura de QR e confirmações)
| Evento | Vibração (Android) | Som (opcional, desligado por padrão no celular, ligado no modo balcão) | Visual |
|---|---|---|---|
| Leitura reconhecida | 1 pulso curto (40 ms) | Bipe curto agudo | Moldura verde + ficha |
| Leitura repetida | 2 pulsos curtos | Bipe duplo | Aviso "já lido" |
| Erro / desconhecido | 1 pulso longo (200 ms) | Tom grave | Moldura vermelha + mensagem |
| Operação confirmada | 1 pulso médio | Som de confirmação | Tela de sucesso |

O iPhone não oferece a API de vibração para web: nele o retorno é visual e sonoro. O retorno nunca depende de um único sentido.

## 7. Componentes

Todos os componentes são construídos sobre primitivas acessíveis (Radix UI) e documentados no **Storybook** (MIT) com todos os estados, temas e tamanhos. Cada um tem teste de acessibilidade automatizado e teste visual de regressão (capturas do Playwright comparadas no CI).

**Estados obrigatórios** em todo componente interativo: padrão · hover · foco (visível por teclado) · pressionado · desabilitado (com motivo explicado quando possível) · carregando · erro · somente leitura.

| Componente | Especificação essencial |
|---|---|
| **Botão** | Variantes: primário (1 por área), secundário, terciário (texto), destrutivo. Tamanhos: 36 px (notebook denso), 44 px (padrão), 52 px (balcão). Estado "carregando" mantém a largura, mostra indicador e bloqueia novo clique. Rótulo com verbo ("Confirmar retirada", não "OK"). |
| **Campo de texto** | Rótulo sempre visível acima (nunca só placeholder); texto de ajuda; erro abaixo com ícone, ligado por `aria-describedby`; `autocomplete` e `inputmode` corretos (e-mail, número, código); colar sempre permitido. |
| **Quantidade** | Botões − / + de 44 px com campo editável; respeita casas decimais da unidade de medida (ex.: 2,5 m); mostra a unidade ao lado; mostra o disponível e impede ultrapassar. |
| **Seleção com busca (combobox)** | Para listas com mais de 7 opções; busca sem acento; teclado completo; "criar novo" quando a permissão existir. |
| **Data e prazo** | Seletor nativo no celular; calendário acessível no notebook; atalhos ("7 dias", "até sexta"); mostra o fuso da organização quando ele for diferente do aparelho. |
| **Tabela de dados** | Cabeçalho fixo; ordenação; colunas configuráveis e salvas por usuário; seleção múltipla com barra de ações em lote; primeira coluna fixa; virtualização acima de 200 linhas (TanStack Virtual); vira lista de cartões em `xs`/`sm`. |
| **Cartão de objeto** | Foto ou ícone do tipo, nome, código, chip de estado, local, ação principal. Mesmo cartão para item, unidade e local. |
| **Chip de estado** | Ícone + texto + cor (§6.2). |
| **Filtros** | Chips dos filtros ativos com "x" para remover e "Limpar tudo"; filtros salvos; contagem de resultados. |
| **Paginação** | Cursor; "carregar mais" no celular; paginação numerada com tamanho de página no notebook. |
| **Aviso (toast)** | Canto inferior (celular: acima da barra de navegação); some em 5 s, exceto erros; pausa ao passar o mouse ou focar; ação "Desfazer" quando couber; anunciado por região `aria-live`. |
| **Faixa (banner)** | Para estados globais: offline, nova versão, servidor em manutenção, licença expirando. Não cobre conteúdo. |
| **Diálogo** | Foco preso dentro, Escape fecha (exceto quando houver dados não salvos — pergunta antes), foco volta ao elemento de origem. Destrutivo irreversível: nome do objeto em destaque e botão destrutivo **não** é o padrão do Enter. |
| **Folha inferior** | Equivalente do diálogo no celular; arrastar para fechar **com** botão "Fechar" visível (WCAG 2.5.7: alternativa ao arraste). |
| **Abas** | Até 5; abas com contagem ("Atrasados 3"); estado na URL. |
| **Estado vazio** | Ilustração simples, frase do que é a área, próxima ação ("Cadastrar primeiro item"); diferente para "sem resultados nos filtros" (oferece limpar filtros). |
| **Esqueleto** | Para carregamentos acima de 300 ms; mesma forma do conteúdo final (evita salto de layout). |
| **Avatar** | Foto ou iniciais com cor derivada do nome (contraste garantido); tamanhos 24/32/40/64/96. |
| **Envio de arquivo** | Arrastar e soltar no notebook, câmera e galeria no celular; prévia; progresso; compressão de imagem no aparelho; limites mostrados antes do envio; remover antes de enviar. |
| **Recorte de imagem** (do MVP) | Arrastar e zoom **e** botões de mover/zoom para quem não arrasta; prévia circular. |
| **Visor do leitor** | §8.5. |
| **Linha do tempo** | Histórico de item, unidade, empréstimo e chamado: ícone do evento, quem, quando (relativo + data completa na dica), detalhes expansíveis. |
| **Conversa** | Suporte e comentários: bolhas com avatar e horário, separadores de data, anexos com miniatura, indicador "enviando / enviado / lido", rascunho preservado, `Enter` envia e `Shift+Enter` quebra linha no notebook. |
| **Central de notificações** | Agrupada por dia, lidas/não lidas, ação direta (ex.: "Aprovar"), marcar tudo como lido; contador no ícone e no ícone do app instalado (Badging API). |
| **Paleta de comandos** | `Ctrl+K`; busca + ações; recentes; navegação só por teclado. |
| **Assistente (passos)** | Configuração inicial, entrada por NF-e, inventário: passos numerados, progresso, voltar sem perder dados, rascunho salvo automaticamente. |
| **Indicador numérico (KPI)** | Número, rótulo, variação no período, link para a lista filtrada correspondente. |
| **Gráfico** | §11. |

## 8. Padrões de interação

### 8.1 Retorno e tempos de resposta
| Tempo da operação | Padrão |
|---|---|
| < 100 ms | Resposta direta, sem indicador |
| 100 ms – 1 s | Botão em "carregando" |
| 1 – 10 s | Indicador com texto do que está acontecendo ("Gerando etiquetas…") |
| > 10 s | Tarefa em segundo plano: o usuário pode sair da tela; notificação quando termina (OCR de DANFE, exportações, etiquetas em lote) |

### 8.2 Confirmar × desfazer
| Tipo de ação | Padrão | Exemplos |
|---|---|---|
| Reversível e de baixo impacto | Executa e oferece **Desfazer** por 5 s | Marcar notificação como lida, arquivar filtro, remover item do carrinho de leitura |
| Movimenta estoque ou responsabilidade | **Tela de revisão** com o resumo (quem, o quê, quantidade, de onde para onde) + botão com verbo específico; depois, **tela de resultado** com o comprovante | Retirada, devolução, entrada, transferência, ajuste |
| Irreversível ou destrutiva | Diálogo destrutivo com o nome do objeto; para as mais graves, digitar o nome para confirmar | Baixar patrimônio, revogar etiqueta, anonimizar usuário, restaurar backup |
| Sensível de segurança | Reautenticação (senha/MFA/passkey) | Mudar papéis, exportar dados pessoais, desativar MFA |

### 8.3 Formulários
- Validação ao sair do campo e no envio, nunca a cada tecla (exceto força de senha). Mensagens dizem **como corrigir**.
- Erros do servidor aparecem no campo correspondente; erros gerais, no topo, com foco movido para eles.
- Nunca perder dados: rascunho local automático em formulários longos; aviso ao sair com alterações não salvas; reenvio seguro após queda (chave de idempotência).
- Botão de envio fica habilitado; ao enviar com erro, o foco vai para o primeiro campo inválido (botão desabilitado sem explicação confunde).
- Proteção contra duplo envio em toda ação que muda dados.
- Campos obrigatórios marcados com "(obrigatório)" no rótulo, não só com `*`.
- Gerenciadores de senha e colagem sempre funcionam; códigos MFA aceitam colagem e preenchimento automático (`autocomplete="one-time-code"`).

### 8.4 Listas, busca e filtros
- Busca com espera de 250 ms após a digitação; resultados destacam o termo; busca sem acento e por códigos.
- Filtros e ordenação persistem na URL e voltam ao retornar à lista.
- Ações em lote com seleção múltipla no notebook; no celular, toque longo inicia a seleção (com alternativa no menu "⋯").
- Gestos de deslizar em cartões são **só atalhos**: a mesma ação existe em botão visível.

### 8.5 Leitura de QR (experiência completa)
1. **Abrir em até 1 s:** o botão "Escanear" abre o visor direto. A biblioteca de leitura é carregada antecipadamente.
2. **Permissão de câmera:** no primeiro uso, uma tela explica por que a câmera é necessária **antes** do pedido do navegador. Se a permissão for negada, mostrar instruções específicas do navegador/sistema para liberar e oferecer digitação do código.
3. **Visor:** moldura central com cantos destacados; escurecimento ao redor; texto de orientação; botões de lanterna, troca de câmera e "Digitar código" sempre visíveis no rodapé (alcance do polegar).
4. **Leitura:** retorno em até 100 ms (§6.9); a ficha sobe em folha inferior sem fechar o visor, para continuar escaneando.
5. **Ficha:** objeto, estado, local, responsável e as ações contextuais (`ESTRATEGIA_QR_CODE.md` §5.2), com a principal em destaque.
6. **Modos em sequência:** barra fixa "Carrinho · 3 itens — Revisar" acima dos controles; lista com remover/desfazer; repetição sinalizada, não somada.
7. **Leitor USB/Bluetooth:** reconhecido em qualquer tela; aviso discreto "Leitor conectado" no primeiro uso.
8. **Modo balcão:** tela cheia, leitura permanente, sessão do operador com bloqueio por inatividade, fonte maior e sons ligados.

### 8.6 Tempo real
- Mensagens novas, aprovações e mudanças aparecem sem recarregar.
- **Listas não saltam embaixo do dedo:** quando chegam itens novos, aparece "3 atualizações — mostrar" no topo; a lista só muda com o toque.
- Um registro aberto que foi alterado por outra pessoa mostra o aviso "Atualizado por Ana há instantes — recarregar"; edição simultânea é bloqueada com mensagem clara (controle de concorrência da ADR-006).
- O estado da conexão aparece de forma discreta: nada quando conectado; faixa "Sem conexão — exibindo dados salvos de 14:32" quando offline; "Reconectando…" na transição.

### 8.7 Erros e situações excepcionais
| Situação | Comportamento |
|---|---|
| Erro de validação | No campo, com instrução |
| Regra de negócio (ex.: saldo insuficiente) | Mensagem com o motivo e o caminho ("Disponível: 2. Reduza a quantidade ou entre na fila de reserva") |
| Sem permissão (403) | Página explicando o que falta e quem pode conceder; nunca uma tela em branco |
| Não encontrado (404) | Página com busca e atalho para o início |
| Erro do servidor (500) | "Algo deu errado do nosso lado", **código do erro** (request_id) copiável para o suporte, botão "Tentar de novo" e "Abrir chamado" já preenchido com o código |
| Sessão expirada | Diálogo de login por cima da tela, **preservando** o que estava em edição; após entrar, a ação continua |
| Offline | Leitura dos dados salvos; ações desabilitadas com o motivo; nada se perde |
| Servidor em atualização | Faixa "Atualização em andamento, volta em instantes" e reconexão automática |

### 8.8 Atalhos de teclado (notebook)
`Ctrl/Cmd+K` paleta · `/` busca · `N` novo (na lista atual) · `G` seguido de `I`/`E`/`S` ir para Início/Empréstimos/Suporte · `?` lista de atalhos · `Esc` fecha. Atalhos de uma tecla podem ser desligados e nunca disparam dentro de campos (WCAG 2.1.4).

## 9. Jornadas principais

Cada jornada vira um protótipo na Fase 0, um teste E2E e um roteiro de teste de usabilidade.

### J1 — Primeiro acesso e instalação do app
Convite por e-mail **ou** QR de conexão → página da organização (logotipo, nome) → criar senha (com medidor de força) → MFA, se o papel exigir (QR do autenticador + digitação, códigos de recuperação para baixar/imprimir) → **tela "Instale o app"** com instruções da plataforma detectada (Android/desktop: botão de instalação; iPhone: passo a passo ilustrado com o botão Compartilhar) → **tour de 3 telas**, que pode ser pulado, mostrando as tarefas do papel → início.
**Meta:** concluir em ≤ 3 min sem ajuda.

### J2 — Solicitar empréstimo (solicitante, celular)
Catálogo ou leitura do QR → ficha do item (fotos, disponível agora, previsão de devolução) → "Solicitar" → quantidade/unidade e prazo (atalhos de dias; limite da política mostrado) → revisão → enviado → acompanhamento em "Meus empréstimos", com linha do tempo e notificação na aprovação.
**Variação:** carrinho com vários itens.

### J3 — Retirada no balcão (operador)
Escanear (ou leitor USB) → ficha da unidade → "Registrar retirada" → escolher pessoa (busca, recentes, ou a solicitação aprovada já vinculada aparece primeiro) → prazo preenchido pela política → revisão → confirmado (som + vibração + tela de comprovante) → visor pronto para o próximo.
**Meta:** ≤ 10 s por item.

### J4 — Devolução com ocorrência
Escanear a unidade → "Receber devolução" (operador) ou "Devolver" (solicitante, se a política permitir) → checklist de estado: "Em ordem" (padrão, 1 toque) ou "Com problema" (dano/falta, fotos, descrição, destino: manutenção ou baixa) → revisão → confirmado. Em lote: escanear todos e confirmar uma vez.

### J5 — Entrada por NF-e (gestor, notebook)
Arrastar o XML → validação imediata (duplicada? de outro destinatário?) → **tela em dois painéis**: à esquerda as linhas da nota; à direita o mapeamento de cada uma (item existente sugerido pela memória de mapeamento / criar item novo / ignorar), quantidade com fator de conversão, local de destino → linhas com problema destacadas, com contador "3 pendências" → rascunho salvo automaticamente → revisão com totais → confirmar (tudo ou nada) → comprovante e opção "Gerar etiquetas das novas unidades".
**Celular:** possível, um produto por tela.

### J6 — Inventário com vários aparelhos
Gestor abre o inventário (escopo e responsáveis) → cada participante recebe a notificação e entra → escaneia o local → escaneia os itens / digita a contagem de granel → progresso por local visível para todos em tempo real → gestor vê as divergências consolidadas → aprova os ajustes.
**Interrupção:** sair e voltar retoma do ponto exato.

### J7 — Suporte (dois lados)
**Solicitante:** "Abrir chamado" (de qualquer lugar ou da ficha de um item/empréstimo, já vinculado) → categoria, assunto, descrição, fotos → enviado → conversa em tempo real, notificações, "Resolvido / Ainda não resolvido" → avaliação.
**Atendente:** notificação → fila com filtros e prazos → abrir → histórico + contexto vinculado (item, empréstimo) ao lado → responder (respostas prontas) ou nota interna → mudar estado/atribuir.

### J8 — Cadastrar item e etiquetar
"Novo item" → tipo de controle explicado com exemplos (unidade patrimonial / consumível / lote) → dados essenciais primeiro, detalhes opcionais recolhidos → fotos pela câmera → para unitários, "Adicionar unidades": escanear etiquetas virgens ou gerar novas → imprimir.

### J9 — Administrar usuários e papéis
Lista com filtros → "Convidar" → e-mail(s), papel(éis) e escopo (almoxarifados) com descrição do que cada papel pode fazer → enviar. Edição de papel mostra o impacto ("passará a poder aprovar empréstimos em Almoxarifado Central") e pede reautenticação.

### J10 — Configuração inicial da organização (Proprietário)
Assistente: organização e marca → fuso e idioma → almoxarifados e locais (com modelo de exemplo) → setores → políticas (padrões seguros, explicados) → e-mail (com envio de teste) → convidar a equipe → gerar cartaz com o QR de conexão. Pode parar e continuar depois.

## 10. Inventário de telas

| Área | Telas | Ênfase de aparelho |
|---|---|---|
| Acesso | Login · Primeiro acesso (convite) · Recuperar senha · MFA (configurar, verificar, recuperação) · Instalar app · Sessão expirada (diálogo) | Todos |
| Início | Painel por papel (Solicitante, Operador, Gestor, Atendente, Administrador, Auditor) | Todos |
| Leitor | Visor · Ficha por leitura · Carrinho/sequência · Modo balcão · Permissão de câmera · Digitar código | Celular, tablet |
| Catálogo | Lista/busca · Ficha do item · Ficha da unidade · Novo/editar item · Unidades e etiquetas do item | Todos (edição: notebook/tablet) |
| Empréstimos | Meus empréstimos · Detalhe com linha do tempo e comentários · Nova solicitação/carrinho · Aprovações · Ativos/atrasados · Reservas · Retirada · Devolução/ocorrência | Todos |
| Estoque | Saldos · Movimentações · Detalhe de movimentação/estorno · Nova entrada manual · Entrada por NF-e (upload, mapeamento, revisão) · Transferência · Ajuste · Locais (árvore + conteúdo) · Inventários (lista, execução, divergências) | Notebook (execução de inventário: celular) |
| Documentos | Notas fiscais (lista, detalhe com movimentações) · Fornecedores | Notebook |
| Etiquetas | Gerar em lote · Modelos de impressão · Etiquetas virgens · Revogadas | Notebook |
| Suporte | Meus chamados · Novo chamado · Conversa · Fila da equipe · Respostas prontas | Todos |
| Notificações | Central · Preferências | Todos |
| Relatórios | Catálogo de relatórios · Visualização com filtros · Exportar | Notebook |
| Perfil | Dados e foto · Segurança (senha, MFA, passkeys, dispositivos) · Preferências (tema, idioma, notificações) · Meus dados (LGPD) | Todos |
| Administração | Usuários e papéis · Convites · Organização e marca · Almoxarifados · Setores · Políticas · E-mail · Saúde do sistema · Backups · Licença · Atualizações · Auditoria | Notebook |
| Sistema | 403 · 404 · 500 · Offline · Manutenção | Todos |

## 11. Painéis e visualização de dados

- **Painel por papel**, nunca um painel único genérico. Exemplos: Operador → "retiradas de hoje, devoluções esperadas, aprovadas aguardando retirada"; Gestor → "abaixo do mínimo, atrasos, divergências, entradas da semana"; Atendente → "chamados por prazo".
- Todo número do painel é clicável e leva à lista filtrada correspondente.
- Gráficos: biblioteca única (Recharts, MIT); barras e linhas como padrão; pizza só com até 4 categorias; sem 3D; paleta categórica segura para daltonismo, com rótulos diretos em vez de só legenda; **toda visualização tem tabela equivalente** acessível; números com formatação pt-BR e algarismos tabulares.
- Períodos com atalhos (hoje, 7 dias, 30 dias, mês atual) e fuso da organização.

## 12. Conteúdo e linguagem

### 12.1 Voz e tom
Claro, direto, respeitoso e calmo. Tratamento por "você". Frases curtas, voz ativa. Sem culpar o usuário ("Não encontramos esse código" em vez de "Você digitou um código inválido"). Sem exclamações em mensagens de erro. Sucesso discreto ("Retirada registrada").

### 12.2 Glossário (termos usados sempre da mesma forma)
| Termo | Significado | Não usar |
|---|---|---|
| Item | Tipo de material no catálogo ("Multímetro Minipa ET-1002") | Produto, patrimônio |
| Unidade | Um exemplar físico identificado de um item | Item, peça |
| Local | Lugar físico na hierarquia | Área, setor |
| Setor | Departamento da organização | Local |
| Almoxarifado | Unidade de estoque com seus locais | Depósito |
| Retirada | Saída de material para empréstimo | Saque |
| Devolução | Retorno de material emprestado | Entrega |
| Consumo | Saída definitiva de material de uso | Baixa |
| Baixa | Retirada definitiva do patrimônio por dano, perda ou descarte | Exclusão |
| Movimentação | Registro de qualquer entrada, saída ou transferência | Transação |
| Etiqueta | Adesivo com QR Code | Tag, código |
| Chamado | Pedido de suporte | Ticket |

### 12.3 Formatos (pt-BR)
Datas `03/11/2026`; horas `14:32`; tempos relativos até 7 dias ("há 5 min", "ontem às 14:32") com data completa na dica; números `1.234,5`; moeda `R$ 1.234,50`; quantidades sempre com unidade (`2,5 m`, `12 un`). Plurais por mensagens ICU (FormatJS), nunca "item(s)". Todos os textos ficam em arquivos de tradução (RNF-15).

### 12.4 Padrão de mensagens
- **Erro:** o que aconteceu + por quê (se útil) + o que fazer. Ex.: "Não foi possível confirmar a retirada. A unidade foi emprestada para outra pessoa há instantes. Escolha outra unidade."
- **Vazio:** o que é esta área + primeira ação.
- **Confirmação destrutiva:** consequência concreta. Ex.: "Baixar a unidade U-7K3M? Ela deixará de aparecer no estoque. O histórico é mantido."

## 13. Acessibilidade (WCAG 2.2 AA)

Requisitos além do básico, com atenção aos critérios novos da 2.2:
| Critério | Como o produto atende |
|---|---|
| 1.4.3 / 1.4.11 Contraste | Tokens verificados no CI (§6.2–6.3) |
| 1.4.10 Reflow | Funciona a 320 px de largura e com zoom de 400% sem rolagem horizontal da página |
| 1.4.12 Espaçamento de texto | Layouts não quebram com espaçamento aumentado |
| 2.1.1 Teclado | Todos os fluxos, incluindo leitor (digitação do código), recorte de imagem e tabelas |
| 2.1.4 Atalhos de uma tecla | Desligáveis e inativos dentro de campos |
| 2.4.3 / 2.4.7 Ordem e foco visível | Anel de foco de 2 px com afastamento; ordem lógica |
| **2.4.11 Foco não encoberto** | Cabeçalho fixo e barra inferior nunca cobrem o elemento focado (`scroll-padding`) |
| **2.5.7 Movimentos de arrastar** | Toda ação por arraste (folha inferior, recorte, reordenar) tem alternativa por botão |
| **2.5.8 Tamanho do alvo** | 44 × 44 px (acima do mínimo de 24 px) |
| 3.3.1 / 3.3.3 Erros | Identificados no campo com sugestão de correção |
| **3.2.6 Ajuda consistente** | Acesso ao suporte sempre no mesmo lugar do menu |
| **3.3.7 Entrada redundante** | Dados já informados no fluxo são reaproveitados (ex.: chamado pré-preenchido com o contexto) |
| **3.3.8 Autenticação acessível** | Colar senha, gerenciadores de senha, colar código MFA, passkeys; sem testes cognitivos |
| 4.1.2 / 4.1.3 Nome, papel e mensagens de status | Primitivas Radix; resultados de leitura, avisos e "salvo" anunciados por regiões `aria-live` |

Mais: marcos de página (`header`, `nav`, `main`), títulos hierárquicos, título da página atualizado em cada rota, link "pular para o conteúdo", respeito a `prefers-reduced-motion`, `prefers-color-scheme` e `forced-colors`.

**Testes:** axe-core em todo E2E (zero violações sérias ou críticas); revisão manual a cada fase com NVDA + Chrome no Windows, Orca no Linux, VoiceOver no iPhone e TalkBack no Android; rodada só com teclado; verificação de zoom de 200% e 400%.

## 14. Aplicativo instalável (PWA)

| Item | Especificação |
|---|---|
| Manifest | Gerado **por organização**: nome ("Avante Almoxarifado"; em clientes futuros, o nome configurado pela marca), nome curto, ícones 192/512 px nas versões normal e *maskable* (na Avante: símbolo ciano sobre `brand-gradient`, arquivos de `brand/`; em clientes futuros: logo do cliente), `theme_color` e `background_color` do tema, `display: standalone`, orientação livre |
| Atalhos do ícone | "Escanear", "Meus empréstimos", "Novo chamado" (pressionar e segurar o ícone) |
| Capturas no manifest | Telas de celular e notebook, para a janela de instalação mais completa no Android e no desktop |
| Convite à instalação | Faixa discreta depois do 2º uso (nunca no primeiro acesso), dispensável, com botão nativo onde existir (Chromium) e passo a passo no iPhone; reaparece só depois de 30 dias |
| Tela de abertura | Fundo da marca e logo; nada de carregamento falso |
| Atualização | Nova versão baixada em segundo plano → faixa "Nova versão disponível — atualizar" → recarrega preservando rascunhos; atualização obrigatória quando a API exigir (com aviso) |
| Offline | Catálogo, meus empréstimos e fichas visitadas em cache, com a hora da última sincronização; página offline própria para o resto |
| Contador no ícone | Notificações não lidas (Badging API, onde suportada) |
| Notificações push | Pedido de permissão só depois de o usuário ativar notificações nas preferências ou em um momento com contexto ("Avisar quando for aprovado?") — nunca na abertura |

## 15. Desempenho como parte da experiência (orçamentos)

| Métrica | Meta (celular intermediário em 4G) | Verificação |
|---|---|---|
| LCP (maior conteúdo visível) | ≤ 2,5 s | Lighthouse CI |
| INP (resposta à interação) | ≤ 200 ms | Lighthouse CI + medição em aparelho real |
| CLS (salto de layout) | ≤ 0,1 | Lighthouse CI |
| JavaScript inicial | ≤ 200 KB comprimido; cada rota carregada sob demanda | Verificação de tamanho no CI |
| Abertura do leitor de QR | ≤ 1 s após o toque | E2E com tempo medido |
| Lighthouse (celular) | Desempenho ≥ 90, Acessibilidade = 100, Boas práticas ≥ 95 | CI, bloqueante |

Técnicas obrigatórias: divisão de código por rota; leitor (wasm) carregado antecipadamente após a primeira tela; imagens em WebP/AVIF com tamanhos responsivos e carregamento tardio; listas longas virtualizadas; fontes servidas localmente com `font-display: swap` e subconjunto latino; cache inteligente (TanStack Query) com atualização em segundo plano.

## 16. Ferramentas e implementação

| Necessidade | Escolha | Licença |
|---|---|---|
| Primitivas acessíveis | Radix UI | MIT |
| Estilos | Tailwind CSS sobre os tokens | MIT |
| Tokens | Style Dictionary | Apache-2.0 |
| Ícones | Lucide | ISC |
| Fontes | Inter, JetBrains Mono | OFL-1.1 |
| Documentação viva de componentes | Storybook | MIT |
| Formulários | React Hook Form + Zod | MIT |
| Dados e cache | TanStack Query, TanStack Virtual | MIT |
| Gráficos | Recharts | MIT |
| Internacionalização | FormatJS (ICU) | BSD-3 |
| Leitura de códigos | BarcodeDetector + zxing-wasm | Apache-2.0 |
| Recorte de imagem | react-easy-crop (ou equivalente com alternativa por botões) | MIT |
| Testes visuais | Capturas do Playwright comparadas no CI | Apache-2.0 |
| Acessibilidade | axe-core | MPL-2.0 (ferramenta de teste, não distribuída) |
| Desempenho | Lighthouse CI | Apache-2.0 |

Toda tela é composta de componentes do design system; componente novo entra primeiro no Storybook, com estados, temas e teste de acessibilidade.

## 17. Processo de design e validação com usuários

| Fase | Atividade | Saída |
|---|---|---|
| 0 | Entrevistas com 6–8 **membros da Avante Tech Jr** de pelo menos 3 papéis; observação do balcão e de um inventário real; levantamento das dores do MVP com quem usa | Personas, jornadas atuais, lista de dores priorizada |
| 0 | Organização da navegação validada com usuários (classificação de cartões) | Mapa de navegação aprovado (§4.1) |
| 0 | Wireframes → **protótipo navegável** de J1–J7 em celular e notebook | Protótipo testado com 5 usuários; ajustes |
| 1 | Tokens, tema claro/escuro, componentes base no Storybook | Design system v0.1 |
| 2–7 | Cada funcionalidade: revisão de design antes de codificar; revisão de qualidade visual antes do merge (§18) | Telas aprovadas |
| Marco M1 (Alfa) | 1ª rodada de teste de usabilidade com tarefas reais | Relatório com problemas por gravidade |
| Fase 8 | Revisão heurística completa (Nielsen) + auditoria de acessibilidade + 2ª rodada de usabilidade | Correções; métricas do §19 |
| Piloto | Observação em uso real + questionário SUS | Métricas finais e backlog de melhorias |

**Participantes:** membros da Avante Tech Jr. Para os resultados não serem enviesados:
- priorizar quem **não** participa do desenvolvimento do sistema e quem usa o almoxarifado no dia a dia (balcão, retirada, gestão);
- cobrir pelo menos 3 papéis (Solicitante, Operador, Gestor/Administrador) e incluir membros recém-chegados, que ainda não conhecem o MVP;
- não repetir as mesmas pessoas nas duas rodadas, quando possível, para medir quem vê o app pela primeira vez;
- o facilitador não ajuda durante as tarefas; dúvidas são anotadas como problema de usabilidade.

Testes de usabilidade sem gravação de rosto: registro de tela e anotações, com consentimento.

## 18. Definição de Pronto de UI (checklist por tela/funcionalidade)

- [ ] Usa só componentes e tokens do design system; nenhuma cor ou tamanho solto.
- [ ] Funciona e foi verificada em `xs`, `md` e `lg`, em retrato e paisagem, nos temas claro e escuro.
- [ ] Estados: carregando, vazio, sem resultados, erro, sem permissão, offline e sucesso implementados.
- [ ] Navegável só por teclado, com foco visível e não encoberto; ordem de foco lógica.
- [ ] Leitor de tela anuncia título, campos, erros e resultados (verificado em pelo menos um leitor).
- [ ] axe sem violações sérias ou críticas; contraste dentro dos tokens.
- [ ] Alvos de toque ≥ 44 px; nenhuma ação depende só de hover ou de arraste.
- [ ] Textos seguem o glossário e o padrão de mensagens; nenhum texto fixo no código (tudo em i18n).
- [ ] Datas, números e quantidades pela formatação central.
- [ ] Proteção contra duplo envio; dados preservados em erro e em queda de conexão.
- [ ] Orçamentos de desempenho da rota respeitados.
- [ ] Captura visual de regressão atualizada e aprovada.
- [ ] Teste E2E do fluxo principal da tela.

## 19. Métricas de experiência

| Métrica | Meta para a 1.0 | Como medir |
|---|---|---|
| SUS (System Usability Scale) | ≥ 80 (faixa "excelente") | Questionário após o teste de usabilidade e após o piloto |
| Sucesso nas tarefas principais (§3.2) sem ajuda | ≥ 90% | Teste de usabilidade |
| Tempo nas tarefas principais | Dentro das metas do §3.2 | Teste de usabilidade e medição no piloto |
| Erros graves por tarefa | 0 (erro que causa dado errado no estoque) | Teste de usabilidade |
| Instalação do app sem ajuda | ≥ 80% dos participantes | Teste de usabilidade (J1) |
| Lighthouse e Core Web Vitals | §15 | CI e aparelho real |
| Acessibilidade | §13, zero violações sérias/críticas | CI e revisão manual |

Métricas de uso no produto (ex.: tempo médio de retirada) são calculadas **no servidor do cliente**, a partir das próprias movimentações, sem rastreamento de terceiros e sem enviar dados para fora.

## 20. Decisões em aberto de UX

| ID | Decisão | Quando |
|---|---|---|
| UX-DA-01 | **Resolvida em 03/11/2026:** "Avante Almoxarifado" com a logo da Avante Tech Jr sem fundo (§6.4). Pendente apenas obter o arquivo vetorial original da logo | Fase 0 |
| UX-DA-02 | Ferramenta do protótipo navegável | Fase 0 |
| UX-DA-03 | Estilo de ilustração dos estados vazios | Fase 1 |
| UX-DA-04 | Sons padrão (ligado/desligado) por modo | Fase 6, após teste no balcão |
| UX-DA-05 | **Resolvida em 03/11/2026:** membros da Avante Tech Jr, com os critérios do §17 | — |
