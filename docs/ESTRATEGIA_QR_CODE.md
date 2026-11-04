# Estratégia de QR Code — Avante Almoxarifado

**Versão:** 1.0 · **Data:** 03/11/2026
**Relação:** detalha RF-QR-01..14 e RF-INV-06 do Plano Mestre v2.3 (a experiência do leitor está em `ESPECIFICACAO_UI_UX.md` §8.5) e substitui a alternativa em aberto da ADR-011.

---

## 1. Para que o QR serve (e para que não serve)

No MVP, o QR foi usado como **contador**: cada leitura somava +1 ao estoque. Isso gera contagem duplicada, reativa itens desativados e não registra quem fez o quê (achado INT-01). Também não responde à pergunta "por que usar QR?".

No produto definitivo, o QR é a **identidade física de um objeto do almoxarifado**. Ele liga o objeto real à ficha digital dele. Escanear um QR significa: **"é este aqui"**. O sistema então mostra o que é, onde deveria estar, com quem está, o histórico, e quais ações fazem sentido agora, para quem escaneou.

### 1.1 Problemas reais que o QR resolve
| Problema no dia a dia | Sem QR | Com QR |
|---|---|---|
| Dez multímetros iguais: qual foi emprestado a quem? | Patrimônio anotado à mão, erros frequentes | Cada unidade tem etiqueta própria; o empréstimo registra a unidade exata |
| Fila no balcão | Procurar o item na lista, digitar, conferir | Escanear, confirmar, pronto (meta: retirada em menos de 10 s por item) |
| Devolução | Achar o empréstimo certo na lista | Escanear a unidade: o sistema já sabe qual empréstimo encerrar |
| "Onde guardo isto?" / "Onde está aquilo?" | Memória de quem organizou | Etiqueta na gaveta: escaneou, vê o conteúdo; o item mostra o local dele |
| Inventário físico | Planilha, contagem manual, dias de trabalho | Escanear gaveta por gaveta; divergências calculadas automaticamente |
| Consumíveis (resistores, parafusos) | Ninguém registra o que pegou | QR na caixa: "retirar 10 unidades" em dois toques |
| Manutenção e histórico | Informação espalhada | Escanear o equipamento mostra ocorrências, manutenções e responsáveis anteriores |
| Primeiro acesso ao sistema | Explicar endereço, instalar, configurar | Cartaz com QR de conexão: a câmera do celular abre o app da organização |

### 1.2 Quando **não** usar QR
- **Não etiquetar cada unidade de consumível barato.** Etiqueta vai na **caixa/compartimento** (QR de item quantitativo ou de localização).
- **Não usar a leitura como contagem.** Contagem é uma ação explícita, com quantidade confirmada.
- **Não colocar informação no QR.** Ele carrega só um identificador; os dados ficam no servidor, protegidos por login.

## 2. Tipos de etiqueta

| Tipo | Letra | Onde fica | O que identifica |
|---|---|---|---|
| **Unidade** | `U` | Colada no equipamento (osciloscópio, notebook, kit Arduino patrimoniado) | Uma unidade física individual (modo UNITARIO) |
| **Localização** | `L` | Prateleira, armário, gaveta, caixa organizadora, sala | Um local da hierarquia |
| **Item a granel** | `I` | Caixa/compartimento de consumível | Item de catálogo QUANTITATIVO naquele local |
| **Lote** | `K` | Embalagem de lote com validade (reagentes, baterias) | Um lote específico |
| **Kit** | `T` | Maleta/caixa que agrupa várias unidades | Um conjunto emprestado como um todo (ex.: "Kit robótica 03") |
| **Conexão** | `C` | Cartaz no laboratório, e-mail de convite | O endereço do servidor da organização, para instalar o app |

Crachá de pessoa (`P`) fica como opção futura (Could): acelera o balcão, mas exige análise de privacidade.

## 3. Formato da etiqueta

### 3.1 Conteúdo do QR
```
https://<endereço-da-organização>/q/<CÓDIGO>
exemplo: https://lab-avante.<dominio-do-produto>/q/U7K3M9QX2H8PD4TNVR
```
- **Por que URL:** a câmera nativa de qualquer celular abre o link direto no app (PWA instalado) ou no navegador — ninguém precisa abrir um leitor antes. Isso remove a maior barreira de uso.
- **Independência de domínio:** o leitor do app **ignora o domínio** e usa só o `<CÓDIGO>`. Se o cliente mudar de endereço, as etiquetas continuam válidas dentro do app; o domínio antigo pode redirecionar.
- **`<CÓDIGO>`** = letra do tipo + 16 caracteres Base32 Crockford (80 bits aleatórios) + 1 caractere verificador. Sem 0/O ou 1/I/L ambíguos, nada sequencial, nada adivinhável.
- **Nada de dados pessoais ou de negócio** no QR.

### 3.2 Texto impresso abaixo do QR
- Código curto agrupado para digitação: `U-7K3M-9QX2-H8PD-4TNV-R`. O verificador detecta erro de digitação na hora.
- Nome do objeto (opcional, configurável) e nº de patrimônio quando existir.
- Logotipo da organização (opcional).

### 3.3 Impressão
| Parâmetro | Regra |
|---|---|
| Correção de erro | Nível Q (25%) — resiste a arranhões e sujeira |
| Tamanho mínimo | 20 × 20 mm para unidades; 30 × 30 mm para localizações lidas à distância |
| Zona de silêncio | 4 módulos de margem branca |
| Material recomendado | Etiqueta de poliéster ou laminada para equipamentos; papel adesivo para caixas internas |
| Formatos de saída | PDF A4 com modelos de folhas de etiqueta comuns no Brasil (padrão Pimaco), PDF para impressora térmica (ex.: 50 × 30 mm e 40 × 25 mm) e PNG avulso |
| Validação | Cada folha gerada inclui teste automático de legibilidade (decodificação do PDF gerado) antes de liberar a impressão |

## 4. Ciclo de vida da etiqueta

```
GERADA ──(vincular a objeto)──► ATIVA ──(dano/perda/substituição)──► REVOGADA
   │                              │
   └─ etiquetas pré-impressas     └─ histórico preserva todas as etiquetas que o objeto já teve
```
- **Etiquetas pré-impressas ("virgens"):** imprimir um rolo de 100 etiquetas antes; no cadastro, escanear uma e vinculá-la ao objeto. É o jeito mais rápido de etiquetar um acervo existente.
- **Uma etiqueta ativa por objeto** (unidade, local, lote, kit); revogar uma etiqueta exige motivo.
- **Etiqueta revogada escaneada** → aviso claro ("Etiqueta substituída em 12/03; use a nova") e link para o objeto.

## 5. O que acontece ao escanear

### 5.1 Regra geral
1. O aparelho decodifica o QR (a imagem nunca vai para o servidor).
2. O app envia só o código; o servidor resolve **objeto + estado + permissões de quem escaneou**.
3. O app mostra a **ficha do objeto** e as **ações contextuais** permitidas.
4. **Nada muda no estoque sem um toque de confirmação.** Toda ação confirmada gera movimentação auditada com chave de idempotência (repetir o envio não duplica).

### 5.2 Ações contextuais por tipo, estado e papel
| Escaneado | Situação | Solicitante | Operador / Gestor |
|---|---|---|---|
| Unidade | Disponível | **Solicitar empréstimo** (ou retirar direto, se a política permitir autoatendimento) | **Registrar retirada para…** (pessoa), mover de local, enviar para manutenção |
| Unidade | Emprestada **para quem escaneou** | **Devolver** / renovar / relatar problema | Receber devolução (com conferência) |
| Unidade | Emprestada para outra pessoa | Ver previsão de devolução / entrar na fila de reserva | Receber devolução; ver responsável e prazo |
| Unidade | Em manutenção / baixada / perdida | Ver estado | Mudar estado conforme as transições permitidas; "encontrada" para PERDIDO |
| Localização | — | Ver o que **deveria** estar ali e o que está disponível | Ver conteúdo; **guardar itens aqui** (escanear itens em sequência); iniciar contagem do local |
| Item a granel | — | **Retirar N** (consumo), se permitido | Retirar, repor, ajustar com motivo |
| Lote | — | Ver validade | Consumir do lote; bloquear lote vencido |
| Kit | Disponível | Solicitar o kit inteiro | Retirar kit (confere o conteúdo); devolução com checklist de componentes |
| Conexão | Fora do app | Abre a página da organização para instalar/entrar | Idem |
| Código desconhecido | — | "Etiqueta não reconhecida — avise o almoxarifado" | **Cadastro assistido:** vincular a objeto existente ou criar novo (abre formulário) |
| Revogada | — | Aviso de substituição | Aviso + atalho para o objeto |
| Etiqueta de outra organização | — | "Esta etiqueta pertence a outra organização" | Idem (sem revelar nada sobre ela) |

### 5.3 Modos de leitura em sequência
| Modo | Uso | Comportamento |
|---|---|---|
| **Carrinho de retirada** | Pessoa leva vários itens | Escaneia tudo, revisa a lista, confirma uma vez → um empréstimo com várias unidades |
| **Devolução em lote** | Pessoa devolve vários itens | Escaneia; o sistema agrupa por empréstimo; confere e confirma |
| **Recebimento** | Mercadoria chegando (com ou sem NF-e) | Escaneia/vincula etiquetas virgens às novas unidades; quantidades confirmadas |
| **Guardar/transferir** | Organizar o almoxarifado | Escaneia o local de destino e depois os itens → transferência |
| **Inventário** | Contagem física | Escaneia o local e depois os itens; para granel, digita a quantidade contada; vários aparelhos ao mesmo tempo |
| **Vincular etiquetas** | Etiquetar acervo existente | Escaneia a etiqueta virgem e escolhe o objeto |

Em todos os modos: lista visível do que foi lido, **desfazer** antes de confirmar, aviso sonoro/vibração diferente para sucesso, repetição e erro; leitura repetida do mesmo código na mesma sessão é sinalizada, não somada (exceto quando o modo pede quantidade explicitamente).

## 6. Leitura em cada dispositivo

| Dispositivo | Como lê | Observações |
|---|---|---|
| Celular / tablet | Câmera traseira no app; ou câmera nativa do sistema (abre o link) | Exige HTTPS válido (ADR-007); lanterna e zoom quando suportados |
| Notebook com webcam | Câmera no app, com seleção de câmera | Útil em balcão sem leitor |
| Notebook / balcão com **leitor USB ou Bluetooth** | Leitor em modo teclado: o app detecta a digitação rápida terminada em Enter em qualquer tela | Mais rápido para alto volume; funciona em qualquer navegador |
| Tablet fixo no balcão | **Modo balcão**: tela permanente de leitura, sessão do operador, bloqueio automático por inatividade | Autoatendimento opcional |
| Qualquer um, sem câmera | Digitação do código curto ou busca | Verificador evita erro |

Tecnologia: `BarcodeDetector` nativo onde existir; `zxing-wasm` como alternativa (Safari, Firefox). O mesmo leitor aceita **códigos de barras do fabricante (EAN/GTIN, Code 128)** impressos em embalagens: o sistema sugere o item de catálogo associado àquele código, o que acelera o cadastro e a reposição de consumíveis.

## 7. Compatibilidade com etiquetas do MVP

Durante a importação (Fase 10), cada código antigo (`AVT-...`, payload JSON, `NFE-...`) é registrado em uma tabela de mapeamento para a unidade ou o item correspondente. O leitor reconhece esses formatos e resolve pelo mapeamento, mostrando a sugestão "reetiquetar". Um relatório lista o que ainda usa etiqueta antiga. O suporte a formatos antigos é desativável quando o acervo estiver reetiquetado.

## 8. Segurança e privacidade

- O QR é só um ponteiro: sem sessão válida, o servidor não revela nada (exceto o tipo "Conexão", que é público por natureza).
- Resolução de código com limite de taxa por usuário (impede varredura).
- Imagens da câmera nunca saem do aparelho.
- Toda ação disparada a partir de uma leitura é auditada com dispositivo e sessão.
- Página pública de "achados e perdidos" (alguém de fora escaneia um equipamento perdido) fica como opção futura (Could), desligada por padrão e exibindo apenas o nome da organização e um contato.

## 9. Métricas de sucesso do QR

| Métrica | Meta inicial (revisar após o piloto) |
|---|---|
| Tempo de retirada de 1 item pelo balcão | < 10 s do escaneamento à confirmação |
| Taxa de leitura com sucesso na 1ª tentativa (etiqueta em bom estado) | ≥ 95% |
| Contagens duplicadas por leitura repetida | 0 (teste automatizado) |
| Divergência de inventário após 3 meses de uso | Medida e acompanhada no painel |

## 10. Requisitos correspondentes

RF-QR-01 (tipos e formato) · RF-QR-02 (decodificação no aparelho) · RF-QR-03 (digitação e leitores USB/BT) · RF-QR-04 (ficha e ações contextuais com confirmação) · RF-QR-05 (cadastro assistido) · RF-QR-06 (idempotência no servidor) · RF-QR-07 (impressão e validação) · RF-QR-08 (revogação/substituição) · RF-QR-09 (etiquetas do MVP) · RF-QR-10 (modos em sequência) · RF-QR-11 (etiquetas pré-impressas) · RF-QR-12 (códigos de barras do fabricante) · RF-QR-13 (modo balcão) · RF-QR-14 (QR de conexão).
