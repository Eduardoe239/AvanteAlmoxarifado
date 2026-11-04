# Avante Almoxarifado — produto definitivo

Branch **`definitivo`**: desenvolvimento do aplicativo completo de almoxarifado, patrimônio e empréstimos da **Avante Tech Jr**.
A branch `main` contém o MVP (`lab_almoxarifado`), que continua em uso e **não é alterado** por esta branch.

> **Estado:** Fase 0 — descoberta, requisitos e decisões. Ainda não há código de produção nesta branch.

## O que é
Aplicativo instalável (PWA) para notebooks, celulares e tablets, com servidor em um notebook (Linux ou Windows), acesso pela rede local e pela internet, leitura de QR Code, empréstimos, estoque com histórico imutável, suporte em tempo real e backup criptografado.

## Documentação (ler nesta ordem)
| Documento | Conteúdo |
|---|---|
| [`docs/PLANO_MESTRE_DESENVOLVIMENTO.md`](docs/PLANO_MESTRE_DESENVOLVIMENTO.md) | Requisitos, metas, fases e gates |
| [`docs/ARQUITETURA_E_DECISOES.md`](docs/ARQUITETURA_E_DECISOES.md) | Arquitetura e registro de decisões (ADRs) |
| [`docs/ESPECIFICACAO_UI_UX.md`](docs/ESPECIFICACAO_UI_UX.md) | Experiência, interface e design system |
| [`docs/ESTRATEGIA_QR_CODE.md`](docs/ESTRATEGIA_QR_CODE.md) | Propósito e uso do QR Code |
| [`docs/MATRIZ_FUNCIONALIDADES_MVP.md`](docs/MATRIZ_FUNCIONALIDADES_MVP.md) | Funções do MVP preservadas no produto |
| [`docs/ANALISE_DE_ROTA.md`](docs/ANALISE_DE_ROTA.md) | Alternativas avaliadas e rota escolhida |
| [`docs/GUIA_EXECUCAO_CLAUDE.md`](docs/GUIA_EXECUCAO_CLAUDE.md) | Regras de execução do desenvolvimento |
| [`docs/RELATORIO_PRONTIDAO.md`](docs/RELATORIO_PRONTIDAO.md) | Validação do planejamento antes do início |
| [`brand/`](brand/) | Logo, ícones e regras de uso da marca |

## Regras de contribuição (resumo)
- Trabalho em branches `feat/<ID>-<descricao>` saindo de `definitivo`; entrada só por pull request com CI verde e revisão.
- Nenhum commit nesta branch altera a `main`.
- Commits no padrão Conventional Commits, citando o ID da tarefa.

## Direitos
© 2026 Avante Tech Jr. Todos os direitos reservados. Nenhuma licença de uso, cópia ou distribuição é concedida por este repositório.
