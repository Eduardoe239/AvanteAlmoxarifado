# Volume 01 — Visão do Produto e Escopo

**Produto:** Avante Almoxarifado · **Organização:** Avante Tech Jr — setor de Sistemas Embarcados
**Responsável:** Luís Eduardo de Sousa Barbosa (Coordenador de Sistemas Embarcados)
**Versão:** 3.0.0 · **Data:** 17/11/2026 · **Status:** Proposto — aguarda aprovação

---

## 1. Problema

Almoxarifados de laboratórios e equipes técnicas sofrem com os mesmos problemas:
- não se sabe ao certo **o que existe, onde está e com quem está**;
- empréstimos são anotados à mão ou em planilha, sem prazo e sem cobrança;
- consumíveis (resistores, parafusos, cabos) somem sem registro;
- inventários levam dias e nunca batem;
- a nota fiscal chega, mas o material não entra no controle;
- quem procura um item não sabe se ele está disponível.

O MVP (`lab_almoxarifado`, branch `main`) provou que a Avante precisa de um sistema e que as pessoas o usam. Também mostrou os limites de uma primeira versão: estoque sem histórico confiável, QR Code que somava estoque sozinho, falhas de segurança e instalação frágil.

## 2. Visão

> **Cada material com identidade, lugar, saldo, responsável e histórico confiáveis — registrados em segundos pelo celular, conferidos automaticamente por visão computacional e controlados de qualquer lugar.**

O Avante Almoxarifado é um sistema de gestão de almoxarifado, patrimônio e empréstimos que combina:
1. **Aplicativo instalável** para notebook, celular e tablet, com interação em tempo real entre usuários e equipe;
2. **Servidor local leve**, que roda em um notebook antigo, com dados sob controle de quem usa;
3. **Visão computacional na ponta** (no celular e em estações embarcadas), que identifica, conta e confere materiais com confirmação humana;
4. **Estações embarcadas** (setor de Sistemas Embarcados) que automatizam o balcão do almoxarifado.

## 3. Edições do produto

O mesmo código atende duas situações. As diferenças são de configuração, empacotamento e hardware, nunca de código separado.

| Edição | Para quem | O que inclui | Quando |
|---|---|---|---|
| **Edição Avante (interna)** | Avante Tech Jr | Sistema completo no notebook do laboratório; QR Code; visão computacional no celular; estação de balcão com leitor de cartão (reaproveitando o conhecimento do Avante Ponto e do Avante Porta) | Releases R1–R3 |
| **Edição Comercial — Essencial** | Laboratórios, empresas juniores, escolas técnicas, oficinas | Software instalado no computador do cliente (Linux ou Windows), aplicativo, QR Code, visão no celular | Release R4 |
| **Edição Comercial — Inteligente** | Clientes que querem automação do balcão | Essencial + **Estação Avante** (equipamento embarcado com câmera, leitor de cartão e tela) para retirada e devolução automatizadas e contagem por visão | Release R4 |

**Nome e marca:** "Avante Almoxarifado" com a logo da Avante Tech Jr. Se o produto for vendido com outro nome, a troca é feita no ponto único de marca (RF-APP-09), sem mudar código.

## 4. Proposta de valor

| Para… | Valor | Como é medido |
|---|---|---|
| Quem pega material | Encontrar, pedir e devolver sem burocracia, pelo celular | Tempo para solicitar ≤ 30 s; tarefa concluída sem ajuda |
| Quem cuida do balcão | Retirada e devolução em segundos, sem digitação | Retirada ≤ 10 s por item com QR; ≤ 5 s na estação |
| Quem gerencia | Saber o que existe, o que falta e quem deve | Divergência de inventário em queda; atrasos visíveis no mesmo dia |
| A organização | Dados próprios, histórico auditável, custo baixo de hardware | Roda em notebook antigo; backup recuperável comprovado |
| Clientes (venda) | Controle de estoque **automatizado** com visão computacional e hardware próprio | Contagem por imagem com erro ≤ 2%; implantação a partir da planilha que o cliente já tem |

## 5. Usuários e papéis

| Papel | Quem é | Principais tarefas |
|---|---|---|
| Proprietário da instalação | Responsável técnico (na Avante: coordenação de Embarcados) | Configurar servidor, backup, papéis administrativos |
| Administrador | Diretoria/gestão | Usuários, papéis, políticas, relatórios |
| Gestor de almoxarifado | Responsável pelo almoxarifado | Aprovar empréstimos, ajustes, inventário, baixas |
| Operador | Membro de plantão no balcão | Retiradas, devoluções, entradas, transferências |
| Atendente de suporte | Quem responde chamados | Fila de chamados, respostas |
| Solicitante | Membro em geral | Catálogo, empréstimos, reservas, chamados |
| Auditor | Leitura (ex.: conselho, fiscal) | Relatórios e histórico |

**Escala de referência da Edição Avante:** cerca de **30 pessoas com acesso**, com uso simultâneo baixo (estimativa de pico: até 10 pessoas ativas ao mesmo tempo, a confirmar na R0).

## 6. Restrições que moldam o projeto

| # | Restrição | Consequência no projeto |
|---|---|---|
| R-01 | Servidor da Avante é um **notebook antigo, memória DDR3, disco rígido (HD)** | Orçamento de recursos rígido (Volume 04); nada pesado roda no servidor; visão computacional roda nos aparelhos e nas estações |
| R-02 | **Um único desenvolvedor** | Entregas em releases pequenas e utilizáveis (Volume 12); automação de testes e de qualidade em vez de revisão manual extensa; escopo priorizado |
| R-03 | Esse notebook **não roda Windows 11** oficialmente (processador anterior à 8ª geração Intel, sem TPM 2.0 provável) | Servidor da Avante em Linux; suporte a Windows entregue para clientes com hardware compatível (R4), com a arquitetura preparada desde o início |
| R-04 | O MVP continua em uso até a substituição | Coexistência; importação dos dados do MVP antes de aposentá-lo |
| R-05 | Repositório público | Nenhum segredo, dado real ou falha não corrigida publicados; repositório privado antes da venda |
| R-06 | Produto vendável no futuro | Licenças de terceiros compatíveis com software fechado desde já; marca centralizada; requisitos legais e regulatórios (LGPD, Anatel para hardware) no Volume 11 |

## 7. Escopo por release (resumo)

Detalhamento, critérios de saída e backlog no Volume 12.

| Release | Objetivo | Resultado para a Avante |
|---|---|---|
| **R0 — Fundação** | Decisões validadas, protótipo testado, base técnica e instalação no notebook | Servidor instalado e acessível; ambiente de homologação |
| **R1 — Núcleo** | Estoque com histórico, empréstimos, QR Code, segurança, suporte e notificações | Uso real em paralelo ao MVP |
| **R2 — Completo** | Paridade total com o MVP e além: NF-e, inventário, reservas, relatórios, tempo real completo; importação do MVP | **MVP aposentado** |
| **R3 — Inteligente** | Visão computacional no celular (contagem, reconhecimento), reposição sugerida, estação de balcão com leitor de cartão | Balcão automatizado na Avante |
| **R4 — Comercial** | Windows, instalador para clientes, licença, importação de planilhas, exportação completa, Estação Avante comercial, conformidade legal e regulatória | Produto pronto para venda |

## 8. Fora do escopo (até decisão registrada)

- Aplicativos nativos e Electron (a PWA é o aplicativo; publicação em lojas é opção pós-R4).
- Escrita offline com sincronização (há leitura offline).
- SaaS multi-cliente hospedado pela Avante.
- Reconhecimento facial e qualquer captura deliberada de rostos.
- Integração com SEFAZ ou ERP.
- Estoque automático sem confirmação humana (a visão sugere; uma pessoa confirma).
- Correções no MVP, salvo decisão própria do responsável.

## 9. Indicadores de sucesso

| Indicador | Meta na Avante (após R2) | Meta comercial (após R4) |
|---|---|---|
| Itens com etiqueta e local definidos | ≥ 95% do acervo patrimonial | Medido por cliente |
| Divergência no inventário físico | Medida no 1º inventário e reduzida a cada ciclo | Idem |
| Empréstimos atrasados sem aviso | 0 | 0 |
| SUS (usabilidade) | ≥ 80 | ≥ 80 |
| Disponibilidade percebida | Sem paradas não planejadas > 30 min/mês | Idem |
| Restauração de backup testada | Mensal, automática | Mensal, automática |

## 10. Princípios de produto

1. **Dados acima de velocidade** — nada destrutivo sem backup restaurável.
2. **Saldo é consequência de movimentações** — nunca editado à mão.
3. **A máquina sugere, a pessoa confirma** — visão computacional e automação propõem; o registro é confirmado por alguém identificado.
4. **Leve por projeto** — funciona bem num notebook antigo; o peso fica nos aparelhos e nas estações.
5. **Segurança e privacidade por padrão** — mínimo de dados pessoais, nenhuma imagem de pessoas.
6. **Uma base, várias edições** — Avante e clientes usam o mesmo código.
7. **Nada do MVP se perde** — toda função do MVP existe, melhorada (Anexo A1).
8. **Pronto é comprovado** — cada requisito tem teste e evidência.
