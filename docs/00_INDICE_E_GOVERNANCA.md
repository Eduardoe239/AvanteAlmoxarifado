# Volume 00 — Índice e Governança da Documentação

**Produto:** Avante Almoxarifado — gestão de estoque, patrimônio e empréstimos com QR Code, visão computacional e dispositivos embarcados
**Organização:** Avante Tech Jr · **Versão do conjunto:** 3.0.0 · **Data:** 17/11/2026 · **Status:** Proposto — aguarda aprovação
**Responsável:** Luís Eduardo de Sousa Barbosa — Coordenador de Sistemas Embarcados

---

## 1. Volumes

| Nº | Volume | Responde a | Ler quando |
|---|---|---|---|
| 00 | Índice e Governança (este) | Onde está cada coisa, quais decisões foram tomadas, como a documentação muda | Sempre primeiro |
| 01 | [Visão do Produto e Escopo](01_VISAO_PRODUTO_E_ESCOPO.md) | O que é, para quem, edições, restrições, o que fica fora | Antes de qualquer decisão de escopo |
| 02 | [Requisitos](02_REQUISITOS.md) | 154 requisitos funcionais e 24 não funcionais, com prioridade e release | Ao planejar qualquer tarefa |
| 03 | [Arquitetura e ADRs](03_ARQUITETURA_E_ADRS.md) | Como o sistema é construído e por quê (ADR-001 a ADR-028) | Ao mexer em estrutura, dependências ou plataforma |
| 04 | [Hardware, Infraestrutura e Capacidade](04_HARDWARE_INFRA_E_CAPACIDADE.md) | Perfis de hardware, orçamento de memória, PostgreSQL para HD, energia, rede | Antes de instalar e ao avaliar desempenho |
| 05 | [Visão Computacional e Embarcados](05_VISAO_COMPUTACIONAL_E_EMBARCADOS.md) | Contagem, reconhecimento, OCR, modelos, leitor de cartão, Estação Avante | R3 e decisões de produto inteligente |
| 06 | [Segurança, Privacidade e LGPD](06_SEGURANCA_PRIVACIDADE_E_LGPD.md) | Ameaças, controles, dados pessoais, riscos aceitos | Em toda mudança de autenticação, dados ou integração |
| 07 | [UI, UX e Design System](07_UI_UX_E_DESIGN_SYSTEM.md) | Experiência, telas, jornadas, acessibilidade, processo no Claude Design | Antes de desenhar ou implementar telas |
| 08 | [QR Code e Etiquetas](08_QR_CODE_E_ETIQUETAS.md) | Para que serve o QR, formato, ciclo de vida, leitura | Em tudo que envolve etiquetas e leitura |
| 09 | [Qualidade e Testes](09_QUALIDADE_E_TESTES.md) | Camadas de teste, testes no notebook real, critérios de cada release, Definição de Pronto | Em toda tarefa e em toda saída de release |
| 10 | [Operação, Backup, Atualização e Incidentes](10_OPERACAO_BACKUP_E_ATUALIZACAO.md) | Monitoramento, backup, calendário de manutenção, runbooks | Ao instalar e operar |
| 11 | [Produto Comercial](11_PRODUTO_COMERCIAL.md) | Edições à venda, suporte, licença, implantação, obrigações legais e regulatórias | Antes da R4 e de qualquer conversa de venda |
| 12 | [Roadmap, Releases e Backlog](12_ROADMAP_RELEASES_E_BACKLOG.md) | R0–R4, backlog da R0, capacidade, aposentadoria do MVP | Ao escolher a próxima tarefa |
| 13 | [Guia de Execução para o Claude Code](13_GUIA_DE_EXECUCAO.md) | Como o desenvolvimento é executado: limites, protocolo, autorrevisão, relatório | Em toda sessão de desenvolvimento |
| A1 | [Matriz de Funcionalidades do MVP](A1_MATRIZ_FUNCIONALIDADES_MVP.md) | Toda função do MVP e o requisito que a preserva | Na R2 (aposentadoria do MVP) |
| A2 | [Análise de Rota](A2_ANALISE_DE_ROTA.md) | Alternativas avaliadas e caminho escolhido | Ao questionar uma escolha de rota |
| A3 | [Relatório de Prontidão](A3_RELATORIO_PRONTIDAO.md) | Validação deste conjunto e condições para iniciar | Antes de autorizar o início |

Fora de `docs/`:
- `CLAUDE.md` e `.claude/`: instruções, comandos, revisor e travas de permissão do Claude Code.
- `brand/`: logo e ícones.

**Ordem de leitura para quem chega:** 00 → 01 → 12 → 02 → 03 → 04, e depois o volume da tarefa.

## 2. Mapa da versão anterior (2.3) para a atual (3.0.0)

| Documento anterior | Agora está em |
|---|---|
| `PLANO_MESTRE_DESENVOLVIMENTO.md` §1–3 | Volume 01 |
| `PLANO_MESTRE_DESENVOLVIMENTO.md` §4–5 | Volume 02 (requisitos com coluna de release) |
| `PLANO_MESTRE_DESENVOLVIMENTO.md` §7 (fases 0–13) | Volume 12 (releases R0–R4) e Volume 09 §6 (critérios) |
| `PLANO_MESTRE_DESENVOLVIMENTO.md` §8 e §10 | Volume 09 |
| `PLANO_MESTRE_DESENVOLVIMENTO.md` §9 | Volume 02 §4 |
| `ARQUITETURA_E_DECISOES.md` | Volume 03 (ADRs) e Volume 06 (ameaças) |
| `ESPECIFICACAO_UI_UX.md` | Volume 07 |
| `ESTRATEGIA_QR_CODE.md` | Volume 08 |
| `GUIA_EXECUCAO_CLAUDE.md` | Volume 13 + `CLAUDE.md` + `.claude/` |
| `MATRIZ_FUNCIONALIDADES_MVP.md` | Anexo A1 |
| `ANALISE_DE_ROTA.md` | Anexo A2 |
| `RELATORIO_PRONTIDAO.md` | Anexo A3 |
| (não existia) | Volumes 04, 05, 10 e 11 |

**Fases × releases:**

| Fases antigas | Release |
|---|---|
| 0–1 | R0 |
| 2–7 (parte) | R1 |
| 4–8, 10 (resto) | R2 |
| (novo) | R3 |
| 9 (Windows) e 13 | R4 |

## 3. Registro de decisões do responsável

| ID | Data | Decisão |
|---|---|---|
| D-01 | 03/11/2026 | Transformar o MVP no produto definitivo profissional, usado na Avante e preparado para venda |
| D-02 | 03/11/2026 | Servidor em notebook do laboratório; venda por instalação local em cada cliente |
| D-03 | 03/11/2026 | Acesso pela rede local e de fora; servidor com internet sempre |
| D-04 | 03/11/2026 | Servidor adaptável a Linux e Windows |
| D-05 | 03/11/2026 | Mesmo repositório GitHub, branch `definitivo`; a `main` mantém o MVP |
| D-06 | 03/11/2026 | É um aplicativo que os usuários instalam e com o qual interagem (ex.: suporte) |
| D-07 | 03/11/2026 | Preservar e melhorar todas as funcionalidades do MVP; redesenhar o propósito do QR Code |
| D-08 | 03/11/2026 | Nome "Avante Almoxarifado"; logo da Avante Tech Jr sem fundo; trocar só se vendido com outro nome |
| D-09 | 03/11/2026 | Membros da Avante participam dos testes de usuário |
| D-10 | 03/11/2026 | Repositório público, sem o relatório de auditoria do MVP |
| D-11 | 17/11/2026 | Servidor da Avante: notebook antigo, memória DDR3, **HD**; requisitos mínimos básicos |
| D-12 | 17/11/2026 | Um único desenvolvedor (o responsável) |
| D-13 | 17/11/2026 | Cerca de 30 pessoas com acesso, não simultâneas |
| D-14 | 17/11/2026 | Produto vendido também como **sistema embarcado** de gestão de estoque inteligente/automatizado com **visão computacional** |
| D-15 | 17/11/2026 | Telas e protótipos desenhados no **Claude Design** |
| D-16 | 17/11/2026 | O **Claude Code** é o executor do desenvolvimento, guiado por `CLAUDE.md` e pelo Volume 13 |
| D-17 | 17/11/2026 | Documentação refatorada em volumes (v3.0.0), com o padrão de qualidade dos projetos Avante Ponto e Avante Porta |
| D-18 | 17/11/2026 | **Modelo de interface aprovado**: protótipo navegável no Claude Design (celular, notebook, Estação Avante e design system) é o padrão visual e de interação de todo o sistema (Volume 07 §17.1) |
| D-19 | 17/11/2026 | Capacidade do desenvolvedor: **12 h por semana** (Volume 12 §2) |
| D-20 | 17/11/2026 | Protótipo testado com usuários e funcionando (R0-13 concluída; registro a anexar) |

## 4. Decisões em aberto (consolidado)

| ID | Decisão | Volume | Quando |
|---|---|---|---|
| DA-01 | Acesso remoto: VPN WireGuard × túnel | 03 (ADR-007) | R0-07 |
| DA-02 | Domínio do produto e padrão de nome por cliente | 03 (ADR-007) | R0-07 |
| DA-03 | Modelo de licença | 11 | R4 |
| DA-04 | Destino do backup externo e guarda da chave | 10 | R0-09 |
| DA-05 | Matriz de aparelhos reais | 09 | R0-08 |
| DA-06 | Confirmar as metas † com medição no notebook | 02, 04 | R0-05 |
| DA-07 | Duração e critérios do período paralelo e do piloto | 12 | Fim da R1 |
| DA-08 | Publicação em lojas de aplicativos | 01 | Pós-R4 |
| DA-CV-01 | Bandeja padrão da contagem | 05 | R3 |
| DA-CV-02 | Modelo de extração e motor de OCR | 05 | R3 |
| DA-EMB-01 | Cadastro de cartões compartilhado com Avante Ponto e Avante Porta | 05 | R3 |
| DA-EMB-02 | Hardware final da Estação Avante | 05, 11 | R4 |
| DA-OPS-01 | Verificador externo de disponibilidade | 10 | R1 |
| DA-OPS-02 | Administrador substituto | 10 | R1 |
| DA-COM-01 | Forma jurídica da venda e nota fiscal | 11 | Antes da R4 |
| DA-COM-02 | Titularidade da propriedade intelectual | 11 | Antes da R4 |
| DA-COM-03 | Preço e planos | 11 | R4 |
| DA-COM-04 | Limite de clientes por capacidade de suporte | 11 | Após o cliente piloto |
| UX-DA-03, UX-DA-04 | Ilustração dos estados vazios; sons padrão | 07 | R0, R1 |
| ADR-012 | Criptografia de disco conforme o hardware | 03, 06 | R0-04 |

## 5. Regras de governança

1. **Fonte única:** cada assunto tem um volume dono. Os outros volumes apontam para ele, sem repetir.
2. **Identificadores estáveis:**
   - IDs de requisitos (RF-, RNF-), ADRs, decisões (D-, DA-) e tarefas (R0-01…) nunca são reutilizados.
   - Um item removido fica marcado como "removido em vX, motivo".
3. **Versionamento:**
   - O conjunto segue SemVer.
   - Mudança de escopo, requisito ou ADR aumenta a versão menor; correção de texto aumenta o patch.
   - Cada volume registra a própria versão e a data.
4. **Mudança de ADR aceita** se faz por nova ADR que a substitui; a antiga fica com o status "Substituída por ADR-0xx".
5. **Nunca enfraquecer para aprovar:** os volumes não são alterados para fazer uma entrega passar. Uma meta só muda com medição e decisão registrada.
6. **Aprovação:** o status passa de "Proposto" para "Aprovado" quando o responsável aprova o conjunto (tarefa R0-01). Daí em diante, mudanças entram por commit com o motivo na mensagem.
7. **Repositório público:**
   - Nenhum volume contém segredos, dados pessoais reais ou detalhes de falhas não corrigidas.
   - O diagnóstico do MVP é interno e não é publicado.
