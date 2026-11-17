# Volume 05 — Visão Computacional e Sistemas Embarcados

**Produto:** Avante Almoxarifado · **Versão:** 3.0.0 · **Data:** 17/11/2026 · **Status:** Proposto — aguarda aprovação
**Responsável:** Luís Eduardo de Sousa Barbosa — setor de Sistemas Embarcados
**Relação:** detalha RF-CV, RF-EMB, RNF-23, RNF-24, ADR-024, ADR-025 e ADR-028.

---

## 1. Posicionamento

Na Edição Comercial, o Avante Almoxarifado é vendido como **sistema de gestão de estoque inteligente e automatizado com visão computacional**. Para que essa promessa seja verdadeira e verificável, o produto define com precisão o que é automático:

| O sistema faz sozinho | Uma pessoa confirma |
|---|---|
| Identificar etiquetas (QR, código de barras) em menos de 1 s | Qualquer movimentação de estoque |
| Contar peças pequenas numa foto e marcar cada uma | O número final da contagem |
| Sugerir qual item do catálogo aparece numa foto | O item escolhido |
| Ler plaquetas de patrimônio, part numbers e números de série | O texto preenchido |
| Identificar a pessoa no balcão pelo cartão | Retiradas e devoluções (com PIN no autoatendimento) |
| Sugerir reposição, detectar padrões e alertar | Pedidos de compra e ajustes |

**Por que não automatizar 100%:** um estoque só é confiável se cada registro tem um responsável. A visão computacional erra em condições ruins (luz, reflexo, peças sobrepostas); a confirmação humana transforma esse erro em uma correção de um toque, em vez de um saldo errado.

## 2. Princípios

1. **Na ponta, nunca no servidor** (ADR-024): o notebook-servidor só guarda modelos, vetores e resultados.
2. **Sugere e confirma:** nenhuma movimentação registrada só por inferência.
3. **Sempre há alternativa manual:** todo recurso de visão tem caminho equivalente sem câmera (digitar, buscar, contar à mão).
4. **Medido antes de lançar:** cada recurso tem métrica mínima (RNF-23), conjunto de avaliação e relatório; sem atingir a métrica, o recurso não é ativado.
5. **Sem pessoas nas imagens** (ADR-028) e sem reconhecimento facial.
6. **Licenças limpas** (ADR-016): modelos, pesos e firmware compatíveis com venda.
7. **Funciona offline** depois de baixado; leve o bastante para celulares intermediários.

## 3. Recursos de visão computacional

### 3.1 Leitura de códigos (base, R1)
QR Code, EAN/GTIN e Code 128 decodificados no aparelho (`BarcodeDetector` + zxing-wasm). Especificação completa no Volume 08.

### 3.2 RF-CV-01 — Contagem assistida por foto (R3)
**Problema:** contar 200 resistores, parafusos ou LEDs à mão é lento e erra; acontece no consumo, no recebimento e no inventário.

**Como funciona:**
1. A pessoa espalha as peças numa **bandeja padrão** (fundo fosco de cor contrastante) e fotografa de cima.
2. O app processa no aparelho:
   - **Versão 1 (visão clássica, OpenCV.js):** correção de perspectiva pela borda da bandeja → limiarização adaptativa → limpeza morfológica → separação de peças encostadas (transformada de distância + *watershed*) → filtragem por área, calibrada com uma peça de amostra ("toque em uma peça");
   - **Versão 2 (somente se a v1 não atingir a meta):** detector pequeno, treinado com peças da Avante, exportado em ONNX quantizado.
3. A tela mostra a foto com **um marcador em cada peça** e o total. A pessoa toca para remover marcações erradas ou adicionar peças não detectadas.
4. Ao confirmar, a quantidade vai para a operação (consumo, recebimento ou contagem de inventário) com a origem "contagem por foto" registrada.

**Condições padrão (as da meta do RNF-23):** bandeja padrão, luz difusa, câmera a 25–40 cm, peças não empilhadas, até 300 peças, peças com no mínimo 3 mm. **Meta:** erro absoluto ≤ 2% do total. Fora das condições padrão, o app avisa ("peças sobrepostas — espalhe um pouco") em vez de arriscar.

### 3.3 RF-CV-02 — Reconhecimento visual de item (R3)
**Problema:** "o que é isto e onde fica?" — peças sem etiqueta, itens novos, etiquetas perdidas.

**Como funciona:**
1. Cada item do catálogo tem **3 ou mais fotos de referência** (tiradas no cadastro).
2. Um modelo de extração de características (classe MobileNet/EfficientNet-Lite, quantizado, ≤ 15 MB) transforma cada foto num **vetor**; os vetores de referência ficam no servidor em formato compacto.
3. Na consulta, o aparelho gera o vetor da foto nova e o servidor devolve os **5 itens mais parecidos**, com grau de confiança e foto.
4. A pessoa escolhe o certo (ou "nenhum"); a escolha alimenta as métricas e, com consentimento, a base de referência.

**Meta:** o item certo entre as 5 sugestões em ≥ 90% dos casos, para itens com ≥ 3 fotos de referência. **Usos:** busca por foto, cadastro assistido (sugere categoria e itens parecidos para evitar duplicidade), etiqueta desconhecida, "onde guardo isto?" (mostra o local do item reconhecido).

### 3.4 RF-CV-03 — Leitura de texto (OCR) no aparelho (R3)
Lê plaquetas de patrimônio, part numbers, números de série e lotes, com OCR no navegador (Tesseract.js ou modelo ONNX equivalente, decidido pela avaliação). Cada campo tem validação de formato (ex.: padrão do patrimônio da organização) e a pessoa confirma o texto. **Meta:** ≥ 95% dos campos corretos em plaquetas legíveis.

### 3.5 Recursos futuros (Pós-R4)
- **RF-CV-07 Conferência visual de devolução:** compara foto da retirada e da devolução e destaca diferenças para o operador.
- **RF-CV-08 Monitoramento de compartimentos:** câmera fixa sobre gavetas ou caixas detecta retirada sem registro. Exige relatório de impacto à proteção de dados e enquadramento sem pessoas.

### 3.6 Experiência de uso (resumo; detalhes no Volume 07)
Guia de enquadramento na tela; aviso de condição ruim antes de processar; resultado com marcações editáveis; confiança mostrada em linguagem simples ("alta", "média", "baixa"); um toque para corrigir; botão "fazer manualmente" sempre visível.

## 4. Ciclo de vida de modelos

| Etapa | Regra |
|---|---|
| Dados | Fotos **de itens**, nunca de pessoas; origem registrada; imagens de usuários só com consentimento explícito (RF-CV-05); conjuntos separados de treino, validação e teste, sem sobreposição |
| Treino | Fora do servidor (máquina do desenvolvedor ou serviço gratuito), com script versionado em `vision/`; sementes fixas para reprodutibilidade |
| Exportação | ONNX, quantizado (`int8`/`fp16`), ≤ 15 MB, testado no ONNX Runtime Web |
| Avaliação | Relatório padrão (§5) com métricas nas condições padrão e adversas; comparação com a versão em produção |
| Ficha do modelo | Nome, versão, finalidade, licença dos pesos e do código, origem dos dados, métricas, limitações conhecidas, data |
| Publicação | Arquivo estático com hash, servido pelo próprio servidor; ativação gradual (RF-CV-04) |
| Produção | Taxa de correção humana por versão (RF-CV-06); alerta se piorar 20% sobre a medida de lançamento |
| Reversão | Um comando volta à versão anterior; aparelhos recebem na próxima abertura |

**Licença de modelos pré-treinados:** usar só pesos publicados com licença que permita uso comercial. Quando o pré-treino usou conjuntos de dados com termos restritivos (caso comum em modelos treinados em ImageNet), isso é registrado na ficha do modelo e passa por análise e revisão jurídica antes da venda (ADR-016, Volume 11). Modelos AGPL são proibidos.

## 5. Protocolo de avaliação

| Item | Definição |
|---|---|
| Conjunto de teste | Fotos da Avante, de itens reais, nunca usadas no treino; mínimo de 200 imagens por recurso, com anotação revisada |
| Condições | Padrão (§3.2) e adversas (luz baixa, reflexo, sombra, peças encostadas, celular de entrada) |
| Métricas | Contagem: erro absoluto e % de fotos dentro da meta · Reconhecimento: acerto entre as 1 e entre as 5 sugestões · OCR: exatidão por campo · Todas: tempo de inferência em 3 aparelhos de referência |
| Aparelhos de referência | Um celular de entrada, um intermediário e um tablet (definidos na R0) |
| Critério de lançamento | Atingir RNF-23 nas condições padrão e não ser pior que a versão anterior em nenhuma condição |
| Regressão automática | Um subconjunto pequeno de avaliação roda no CI (ONNX Runtime em CPU) a cada mudança de modelo ou de pré-processamento |

## 6. Dispositivos embarcados

### 6.1 Leitor de cartão de balcão — Edição Avante (R3)

| Item | Especificação |
|---|---|
| Objetivo | Identificar quem está no balcão aproximando um cartão (cartão do RU, crachá ou tag), sem digitar nome |
| Hardware | ESP32 em **módulo com homologação Anatel** + leitor 13,56 MHz (MFRC522 ou PN532) + LED e buzzer; display opcional. Reaproveita o conhecimento e a placa do Avante Ponto |
| Firmware | ESP-IDF (C) com FreeRTOS; watchdog; detecção de queda de tensão; OTA assinado; logs mínimos |
| Comunicação | HTTPS na rede local com credencial do dispositivo (ADR-025); heartbeat a cada 30 s |
| Fluxo | O operador abre a "sessão de balcão" no app, vinculada ao leitor → a pessoa aproxima o cartão → o servidor identifica o usuário → o app do operador mostra a pessoa, seus empréstimos e pendências → o operador escaneia os itens e confirma |
| Retorno local | LED verde + bipe curto (reconhecido) · LED vermelho + bipe longo (cartão não vinculado/bloqueado) · LED amarelo piscando (sem servidor) |
| Segurança | Cartão **identifica, não autentica**: UIDs de cartões comuns podem ser copiados. No balcão com operador, o operador confere a pessoa; no autoatendimento, exige-se PIN (RF-EMB-03) |
| Desempenho | Identificação < 1 s; reconexão < 30 s; operação de 12 h/dia (RNF-24) |

### 6.2 Estação Avante — Edição Comercial Inteligente (R4)

| Item | Especificação |
|---|---|
| Objetivo | Autoatendimento e balcão automatizado: identificar a pessoa, ler etiquetas, **contar peças por visão** e registrar retirada/devolução com confirmação na tela |
| Arquitetura | Computador de placa única ARM 64 bits (≥ 4 GB) com Linux embarcado mínimo, câmera, leitor 13,56 MHz, tela sensível ao toque de 7"–10", **bandeja de contraste e iluminação LED difusa integradas** (garantem as condições padrão da contagem) |
| Software | O mesmo app em **modo estação** (quiosque), com inferência local acelerada; atualização assinada com reversão |
| Fluxo | Cartão + PIN → escanear ou fotografar itens na bandeja → resumo na tela → confirmar → comprovante (tela/e-mail) |
| Sem servidor | Mostra "fora do ar" e não registra nada (RF-EMB-06) |
| Hardware final | Escolhido na R4 com protótipo de bancada, lista de materiais com custos, disponibilidade de fornecimento e licenças (decisão DA-EMB-02) |
| Conformidade | Rádios (Wi-Fi, Bluetooth, NFC/RFID) exigem análise de homologação Anatel do produto final; fonte de alimentação certificada; manual com avisos de segurança (Volume 11) |

### 6.3 Nó de câmera de compartimento (Pós-R4)
Câmera de baixo custo sobre gavetas ou caixas para RF-CV-08. Fora do escopo até a avaliação de privacidade e de viabilidade.

### 6.4 Ciclo de vida dos dispositivos

| Etapa | Como |
|---|---|
| Pareamento | O administrador gera um código de pareamento de uso único no painel; o dispositivo é configurado com ele; o administrador aprova e dá um nome e um local ao dispositivo |
| Credencial | Gerada no pareamento, guardada na memória cifrada do dispositivo (criptografia de flash do ESP32 / armazenamento protegido na estação); revogável a qualquer momento |
| Operação | Heartbeat, versão e erros visíveis no painel de saúde (RF-EMB-04) |
| Atualização | Imagem assinada (Secure Boot do ESP32 / assinatura do pacote na estação); partição dupla com reversão automática se a nova versão não se comunicar em 5 min |
| Desativação | Revogar no painel apaga a credencial do lado do servidor; procedimento de limpeza física documentado |

### 6.5 Padrões de qualidade de firmware

- Versão do ESP-IDF fixada; compilação reproduzível no CI; binário com número de versão e hash.
- Análise estática (cppcheck/clang-tidy) sem alertas altos; testes unitários com Unity no host; testes na bancada (§7).
- Nenhum segredo no código-fonte; credenciais só no pareamento.
- Watchdog de tarefa e de sistema; tratamento explícito de perda de rede, perda de servidor e falha do leitor.
- Inventário de licenças de cada binário (ADR-016).

## 7. Bancada de testes (hardware no laço)

| Cenário | Resultado esperado |
|---|---|
| Cartão vinculado / não vinculado / bloqueado | Retorno correto em < 1 s |
| 1.000 leituras seguidas | Nenhuma perdida ou duplicada |
| Queda de Wi-Fi e retorno | Reconecta em < 30 s, sem registro perdido ou duplicado |
| Servidor fora do ar | Indicação clara; nada registrado |
| Queda de energia durante atualização | Volta na versão anterior funcionando |
| Credencial revogada | Dispositivo recusado; alerta no painel |
| 12 h de operação contínua | Sem travamento nem vazamento de memória (monitorado) |

## 8. Decisões em aberto

| ID | Decisão | Quando |
|---|---|---|
| DA-CV-01 | Bandeja padrão (cor, material, tamanho) | R3, antes da avaliação da contagem |
| DA-CV-02 | Modelo de extração de características e motor de OCR finais | R3, após o protocolo do §5 |
| DA-EMB-01 | Cadastro de cartões compartilhado entre Avante Ponto, Avante Porta e Avante Almoxarifado (um cartão por membro para os três sistemas) ou separado | R3 (exige análise de privacidade e acordo entre os projetos) |
| DA-EMB-02 | Hardware final da Estação Avante | R4 |
