# Avante Almoxarifado — produto definitivo

Branch **`definitivo`**: gestão de estoque, patrimônio e empréstimos da **Avante Tech Jr**, com QR Code, visão computacional na ponta e dispositivos embarcados. O produto também está sendo preparado para venda como sistema de gestão de estoque inteligente.
A branch `main` contém o MVP (`lab_almoxarifado`), que continua em uso e **não é alterado** por esta branch.

> **Estado:** documentação v3.1.0 aprovada em 24/11/2026. Próximo passo: release **R0 — Fundação**. Ainda não há código de produção nesta branch.

## O que é
- **Aplicativo instalável (PWA)** para notebooks, celulares e tablets.
- **Servidor** num computador do próprio cliente (Linux; Windows na Edição Comercial), pensado para rodar até num notebook antigo (2 núcleos, 4 GB DDR3, HD).
- **Acesso** pela rede local e de fora.
- **Estoque** com histórico imutável, empréstimos, QR Code, NF-e, inventário, suporte em tempo real e backup criptografado.
- **Visão computacional** no celular: contagem de peças por foto, busca por foto e leitura de plaquetas, sempre com confirmação humana.
- **Balcão** com leitor de cartão (ESP32) e a **Estação Avante** de autoatendimento.

## Documentação
Comece por [`docs/00_INDICE_E_GOVERNANCA.md`](docs/00_INDICE_E_GOVERNANCA.md), que traz o mapa de todos os volumes, as decisões tomadas e a ordem de leitura.

| | |
|---|---|
| [01 Visão e Escopo](docs/01_VISAO_PRODUTO_E_ESCOPO.md) | [08 QR Code e Etiquetas](docs/08_QR_CODE_E_ETIQUETAS.md) |
| [02 Requisitos](docs/02_REQUISITOS.md) | [09 Qualidade e Testes](docs/09_QUALIDADE_E_TESTES.md) |
| [03 Arquitetura e ADRs](docs/03_ARQUITETURA_E_ADRS.md) | [10 Operação e Backup](docs/10_OPERACAO_BACKUP_E_ATUALIZACAO.md) |
| [04 Hardware e Capacidade](docs/04_HARDWARE_INFRA_E_CAPACIDADE.md) | [11 Produto Comercial](docs/11_PRODUTO_COMERCIAL.md) |
| [05 Visão Computacional e Embarcados](docs/05_VISAO_COMPUTACIONAL_E_EMBARCADOS.md) | [12 Roadmap e Backlog](docs/12_ROADMAP_RELEASES_E_BACKLOG.md) |
| [06 Segurança e LGPD](docs/06_SEGURANCA_PRIVACIDADE_E_LGPD.md) | [13 Guia de Execução (Claude Code)](docs/13_GUIA_DE_EXECUCAO.md) |
| [07 UI, UX e Design System](docs/07_UI_UX_E_DESIGN_SYSTEM.md) | Anexos: [A1](docs/A1_MATRIZ_FUNCIONALIDADES_MVP.md) · [A2](docs/A2_ANALISE_DE_ROTA.md) · [A3](docs/A3_RELATORIO_PRONTIDAO.md) |

Marca: [`brand/`](brand/).

## Desenvolvimento com o Claude Code
O desenvolvimento é executado pelo Claude Code:
- [`CLAUDE.md`](CLAUDE.md) é lido em toda sessão.
- O manual completo é o Volume 13.
- `.claude/` contém:
  - os comandos `/iniciar-tarefa`, `/autorrevisao`, `/revisao-independente` e `/relatorio-entrega`;
  - o agente revisor independente;
  - as travas de permissão (sem push, sem ações destrutivas, sem gravar firmware).

## Regras de contribuição (resumo)
- Uma tarefa por vez, com o ID do backlog (ex.: `R1-07`).
- Trabalho em `feat/<ID>-<descricao>` saindo de `definitivo`. Entrada só por pull request com CI verde e revisão.
- Nenhum commit desta branch altera a `main`.
- Commits no padrão Conventional Commits em português, citando o ID da tarefa.

## Direitos
© 2026 Avante Tech Jr. Todos os direitos reservados. Este repositório não concede nenhuma licença de uso, cópia ou distribuição.
