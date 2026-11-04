# Relatório de Prontidão para o Início do Desenvolvimento — Avante Almoxarifado

**Data:** 03/11/2026
**Pergunta:** o planejamento está completo, consistente e validado para iniciar o desenvolvimento do produto definitivo?
**Veredito:** **PRONTO PARA INICIAR A FASE 0**, condicionado à autorização do responsável e ao acesso ao repositório (§4). Nenhuma pendência bloqueia o início; as pendências listadas no §5 precisam ser resolvidas **durante** a Fase 0, e são exatamente o que o Gate 0 verifica.

---

## 1. Conjunto de documentos validado

| Documento | Versão | Conteúdo |
|---|---|---|
| `PLANO_MESTRE_DESENVOLVIMENTO.md` | 2.3 | 127 requisitos funcionais, 19 não funcionais com metas, 14 fases (0–13) com gates |
| `ARQUITETURA_E_DECISOES.md` | 1.3 | Arquitetura, 22 ADRs, modelo de ameaças STRIDE, observabilidade |
| `ESPECIFICACAO_UI_UX.md` | 1.1 | Princípios, navegação por aparelho, design system com contraste verificado, 26 componentes, 10 jornadas, acessibilidade WCAG 2.2, PWA, desempenho, processo de design |
| `GUIA_EXECUCAO_CLAUDE.md` | 2.3 | Regras, aprovações, protocolo por tarefa, autorrevisão, relatório, paridade Linux × Windows |
| `ESTRATEGIA_QR_CODE.md` | 1.0 | Propósito do QR, 6 tipos de etiqueta, ações contextuais, modos de leitura |
| `MATRIZ_FUNCIONALIDADES_MVP.md` | 1.0 | 72 funções e ideias do MVP mapeadas para requisitos do produto |
| `ANALISE_DE_ROTA.md` | 1.0 | 11 decisões de rota com alternativas, riscos, marcos M0–M5, responsabilidades |
| `RELATORIO_AUDITORIA_BASELINE_2026-11-03.md` | — | Diagnóstico executado do MVP — **documento interno, não publicado no repositório** (contém falhas de segurança do MVP em uso) |
| `brand/` | — | 16 arquivos de marca (SVG e PNG), ícones do app e regras de uso |

## 2. Decisões registradas nesta rodada

| Decisão | Onde está |
|---|---|
| Nome: **Avante Almoxarifado**, da Avante Tech Jr; nome comercial só será trocado se houver venda | Plano §1, RF-APP-09, UI/UX §6.4 |
| Logo: **Avante Tech Jr sem fundo** | `brand/`, UI/UX §6.4 |
| Testes de usuário com **membros da Avante Tech Jr**, com critérios contra viés | UI/UX §17 |
| 1.0 para **uso interno**; licenciamento, marca comercial e documentos de venda vão para a **Fase 13**, executada só quando a venda for decidida | Plano §7 (Fases 12 e 13), ADR-014 |

## 3. Validação executada (evidências)

### 3.1 Verificações automáticas (todas aprovadas na última execução)
| # | Verificação | Resultado |
|---|---|---|
| 1 | Todo RF/RNF citado em qualquer documento existe no Plano | 0 faltando |
| 2 | Toda ADR citada existe | 0 faltando |
| 3 | Toda seção interna citada existe | 0 faltando (1 falso positivo: referência cruzada entre documentos) |
| 4 | Todo requisito M/S tem fase responsável | 127 requisitos; só os 3 de prioridade C (pós-1.0) ficam sem fase, como previsto; RF-APP-09 está nas Fases 1 e 13 de propósito |
| 5 | Nenhuma versão de plataforma desatualizada | 0 ocorrências |
| 6 | Referências de versão entre documentos coerentes | Todas apontam para Plano 2.3, ADRs 1.3, Guia 2.3 |
| 7 | Contraste WCAG de todas as combinações de cores do design system | 30/30 aprovadas; tokens da marca também calculados |
| 8 | Arquivos de marca válidos | 16 arquivos; SVGs válidos; prévia conferida visualmente |

### 3.2 Problemas encontrados e corrigidos durante a validação
| # | Problema | Correção |
|---|---|---|
| 1 | Ubuntu 24.04 como referência, mas o 26.04 LTS já existe (suporte até 2031) | Ubuntu 26.04 (referência) e 24.04 |
| 2 | Debian 12 em vez do estável atual | Debian 13 |
| 3 | PostgreSQL 16, com fim de suporte mais próximo | PostgreSQL 18 (suporte até nov/2030); PostgreSQL 19 reavaliado no Gate 0 (ADR-022) |
| 4 | Python 3.12, já só com correções de segurança | Python 3.14 (até out/2030), com 3.13 como alternativa |
| 5 | Windows 11 23H2 como mínimo, mas a 23H2 e a 24H2 Home/Pro já estão fora de suporte | "Versão com suporte vigente" (hoje 25H2+), verificada pelo `avante doctor` |
| 6 | Licenciamento obrigatório na 1.0, embora a venda seja futura | RF-ADM-04 e ADR-014 movidos para a Fase 13 |
| 7 | A Fase 7 ainda entregava o RF-ADM-04 | Removido da Fase 7 |
| 8 | A marca centralizada (RF-APP-09) só aparecia na Fase 13 | Implementada desde a Fase 1 |
| 9 | Fase 0 ainda previa "modelo de licença" | Trocado por "obter o vetorial original da logo" |
| 10 | Textos tratando a venda como imediata (Plano §0, ADRs, Análise, Guia) | Ajustados para "1.0 interna, preparada para venda futura" |
| 11 | Referências de versão desatualizadas entre documentos | Unificadas |
| 12 | Logo: a primeira vetorização saiu invertida, e o símbolo virou um quadrado no 2º teste | Erros corrigidos no script; resultado conferido visualmente |
| 13 | Logo: trilhas de circuito de ~1 px viraram "pontos de sujeira" | Símbolo simplificado sem trilhas; pendência de obter o vetorial original registrada |

### 3.3 Limites da validação (declarados)
- A consistência foi verificada por ferramentas e por releitura das seções críticas; não houve revisão por uma segunda pessoa ou agente independente.
- As metas marcadas com † (desempenho, disponibilidade, recuperação) são propostas e só serão confirmadas medindo no notebook real (Fase 0), por desenho do Plano.
- Versões de plataforma foram conferidas na web em 03/11/2026 e mudam com o tempo; a ADR-022 define como mantê-las atualizadas.

## 4. Condições para iniciar a Fase 0

| # | Condição | Situação |
|---|---|---|
| C1 | Aprovação do conjunto de documentos | Aguardando você |
| C2 | Autorização explícita para iniciar | Aguardando você |
| C3 | Repositório: nome (`dono/repositório`) e acesso de escrita para criar a branch órfã `definitivo` e fazer push dos documentos | Aguardando você (não tenho acesso a nenhum repositório nesta sessão) |

## 5. Pendências a resolver durante a Fase 0 (não bloqueiam o início; bloqueiam o Gate 0)

| ID | Pendência | Responsável |
|---|---|---|
| P1 | Domínio para o certificado HTTPS (DA-02), necessário para a câmera ler QR no celular | Avante |
| P2 | Notebook do laboratório com Linux (Ubuntu 26.04 recomendado) e uma máquina com Windows 11 para os testes de rede e hardware | Avante |
| P3 | Celular Android, iPhone e tablet para os testes de câmera, push e instalação (DA-05) | Avante |
| P4 | Agenda com 6–8 membros da Avante para entrevistas e com 5 para o teste do protótipo | Avante |
| P5 | Arquivo vetorial original da logo (não bloqueia; os arquivos atuais funcionam) | Avante |
| P6 | Decisões DA-01 (VPN × túnel), DA-04 (backup externo), DA-06 (metas medidas) | Juntos, com base nos testes |
| P7 | Execução dos testes no hardware: eu preparo roteiros e scripts; a execução nos aparelhos é feita por alguém da Avante (ou por mim, se o notebook for conectado a esta conversa pelo app de desktop) | Avante + Claude |

## 6. O que acontece quando você autorizar

1. Criar a branch órfã `definitivo` com os documentos, a pasta `brand/` e a estrutura inicial do monorepo (só com sua autorização para o push).
2. Apresentar, para aprovação, o roteiro dos testes de rede e de hardware em Linux e Windows (Gate 0).
3. Preparar o roteiro de entrevistas com os membros da Avante e começar o protótipo navegável das jornadas J1–J7.
4. Fechar o Gate 0 com relatório PASS/HOLD/FAIL antes de qualquer código de produção (Fase 1).
