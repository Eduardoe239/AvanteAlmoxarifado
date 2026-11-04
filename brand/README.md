# Marca — Avante Almoxarifado (Avante Tech Jr)

Arquivos de marca usados pelo aplicativo. As regras de uso completas estão em `docs/ESPECIFICACAO_UI_UX.md` §6.4.

| Arquivo | Onde usar |
|---|---|
| `logo-avantetechjr-ciano.svg` / `.png` | Logo completa sobre fundos **escuros** (barra lateral, login, tema escuro, splash) |
| `logo-avantetechjr-navy.svg` / `.png` | Logo completa sobre fundos **claros** (tema claro, e-mails, PDFs, etiquetas) |
| `logo-avantetechjr-branca.svg` / `.png` | Sobre o azul de ação ou fotos escuras |
| `simbolo-avante-{ciano,navy,branca}.svg` / `.png` | Só o "A": cabeçalho compacto, etiquetas pequenas |
| `icone-app-192.png`, `icone-app-512.png`, `icone-app-maskable-512.png` | Ícones do app instalado (PWA) |
| `favicon-32.png` | Ícone da aba do navegador |

## Regras rápidas
- Ciano (`#13F1FC`) **só sobre fundo escuro**. Sobre branco o contraste é 1,40:1: use a versão navy.
- Não redesenhar, distorcer, girar, aplicar sombra ou trocar cores.
- Abaixo de 96 px de largura, usar só o símbolo.
- O ciano é cor de marca, não de interface: botões e links usam os tokens de ação.

## Origem e limitação
Gerados em 03/11/2026 a partir da imagem da logo enviada pelo responsável (437 × 432 px), pelo script `tools/logo_build.py` (fundo removido pelo modelo do degradê, vetorização com potrace). Nessa resolução, as trilhas de circuito do símbolo (cerca de 1 px) não podem ser vetorizadas com fidelidade, por isso o símbolo é a **versão simplificada, sem trilhas**. Quando o arquivo vetorial original (SVG/AI/PDF) da Avante Tech Jr for obtido, basta substituir estes arquivos mantendo os mesmos nomes; nenhum código muda.

`tools/verificar_contraste.py` calcula o contraste WCAG de todas as combinações de cores do design system.
