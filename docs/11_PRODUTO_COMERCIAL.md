# Volume 11 — Produto Comercial

**Produto:** Avante Almoxarifado · **Versão:** 3.0.0 · **Data:** 17/11/2026 · **Status:** Proposto — aguarda aprovação
**Responsável:** Luís Eduardo de Sousa Barbosa
**Relação:** RF-COM, RF-DAT, RF-EMB-07, RF-ADM-04; ADR-014, ADR-016, ADR-022, ADR-023; Volumes 01, 04, 05 e 06.
**Aviso:** este volume organiza as decisões de negócio e as obrigações a cumprir. Preço, contrato e textos legais são **decisões do responsável e da diretoria da Avante Tech Jr**, com revisão de advogado; nada aqui é parecer jurídico.

---

## 1. O que é vendido

| Item | Essencial | Inteligente |
|---|---|---|
| Software instalado no computador do cliente (Linux ou Windows) | Sim | Sim |
| Aplicativo (PWA) para celular, tablet e computador | Sim | Sim |
| QR Code, etiquetas, empréstimos, estoque, NF-e, inventário, suporte, relatórios | Sim | Sim |
| Visão computacional no celular (contagem, reconhecimento, leitura de plaquetas) | Sim | Sim |
| Automação (reposição sugerida, alertas, regras) | Sim | Sim |
| **Estação Avante** (hardware de autoatendimento com câmera, leitor de cartão, tela e bandeja iluminada) | — | Sim (1 ou mais) |
| Implantação assistida (importação de planilhas, configuração, treinamento) | Opcional | Incluída |
| Suporte e atualizações | Conforme plano (§5) | Conforme plano (§5) |

**Posicionamento:** "gestão de estoque inteligente com visão computacional, que roda no seu próprio computador". Diferenciais verificáveis: dados ficam no cliente; funciona em hardware antigo (Perfil Mínimo); contagem por imagem com meta publicada (RNF-23); implantação a partir da planilha existente; histórico auditável.

**Promessas proibidas no material comercial:** "100% automático", "sem erro", "reconhece qualquer peça", métricas não medidas no protocolo do Volume 05 §5, e qualquer comparação com concorrente sem fonte.

## 2. Clientes-alvo (hipóteses a validar)

1. Laboratórios universitários e de escolas técnicas (componentes, ferramentas, equipamentos emprestados).
2. Empresas juniores e núcleos estudantis.
3. Pequenas oficinas, makerspaces e assistências técnicas.

**Validação antes da R4:** entrevistas com pelo menos 5 potenciais clientes de fora da Avante (problema, como controlam hoje, quanto pagariam, quem decide a compra), registradas sem dados pessoais desnecessários.

## 3. Requisitos de hardware publicados

| Perfil | Uso | Requisitos |
|---|---|---|
| Mínimo | Até ~30 pessoas com acesso, 10 simultâneas | x86-64, 2 núcleos, 4 GB, HD com 120 GB livres, rede cabeada |
| Recomendado | Até ~100 pessoas, 30 simultâneas | 4 núcleos, 8 GB, SSD |
| Certificado | Garantia de desempenho | Lista de modelos testados pela Avante (publicada na R4) |

Sistemas suportados: os da política de versões (ADR-022). O instalador verifica o hardware e se recusa abaixo do mínimo, explicando o motivo (RF-COM-01). Aparelhos dos usuários: os da matriz do Volume 09 §4.

## 4. Licença do software

- Modelo comercial (assinatura × perpétua com suporte) — **decisão DA-03**.
- Implementação: licença assinada verificada offline, com edição, limites e validade (ADR-014).
- Ao expirar: período de carência e depois **somente leitura**. Nunca bloquear o acesso aos dados do cliente, nunca apagar nada, sem telemetria obrigatória.
- A Edição Avante não verifica licença.

## 5. Suporte, versões e garantia

| Tema | Regra proposta |
|---|---|
| Versões suportadas | A versão atual (N) e a anterior (N-1) recebem correções de segurança; versões mais antigas são orientadas a atualizar |
| Ciclo | Uma versão menor a cada 2–3 meses; correções de segurança quando necessário |
| Canal de suporte | Pelo próprio módulo de suporte do sistema, de cliente para fornecedor, além de e-mail; horário comercial |
| Níveis de atendimento | Crítico (sistema fora do ar ou perda de dados): primeira resposta no mesmo dia útil · Alto: 2 dias úteis · Normal: 5 dias úteis (valores finais definidos no contrato) |
| Acesso remoto do fornecedor | Só com autorização do Proprietário do cliente, por janela de tempo, papel específico, auditado e revogável (RF-COM-02) |
| Garantia da Estação Avante | Prazo e cobertura definidos no contrato; peças de reposição listadas na lista de materiais |
| Fim de vida | Aviso com 12 meses de antecedência; exportação completa garantida (RF-DAT-03) |

**Capacidade real de suporte:** com um único desenvolvedor, o número de clientes ativos fica limitado à capacidade de atendimento. A venda começa com **um cliente piloto**; o limite seguinte é decidido após medir as horas de suporte por cliente (decisão DA-COM-04).

## 6. Implantação no cliente

1. Verificação de hardware (relatório do instalador).
2. Instalação do pacote (`.deb` ou `.msi`) seguindo o manual.
3. Assistente de implantação (RF-COM-04): organização, marca, almoxarifados, políticas, e-mail.
4. **Importação das planilhas** do cliente com simulação antes de gravar (RF-DAT-01, RF-DAT-02).
5. Geração e impressão de etiquetas.
6. Rede e acesso externo (VPN ou túnel, ADR-007); backup externo configurado e **restauração testada** antes do aceite.
7. Treinamento por papel (1 h para operadores, 30 min para membros).
8. Termo de aceite.

## 7. Conformidade e obrigações antes da primeira venda

| Tema | Obrigação | Responsável |
|---|---|---|
| Forma jurídica da venda | Confirmar com a diretoria da Avante Tech Jr e o estatuto se a empresa júnior pode vender e dar suporte a software e hardware, e como emitir nota fiscal | Responsável + diretoria |
| Propriedade intelectual | Registrar por escrito que o código, os modelos e o hardware pertencem à Avante Tech Jr (ou a quem for definido), com termo de cessão dos colaboradores; avaliar registro do software no INPI; manter separação clara de qualquer outro projeto pessoal ou de terceiros que use visão computacional | Responsável + diretoria |
| Licenças de terceiros | Inventário de licenças (software, modelos, firmware, fontes) sem pendências; avisos de atribuição no produto (ADR-016) | Desenvolvedor |
| LGPD | Política de privacidade, termos de uso, contrato de tratamento de dados (cliente controlador, fornecedor operador no suporte), registro das operações de tratamento (Volume 06) | Responsável + advogado |
| Contrato | Objeto, licença, suporte, níveis de serviço, limitação de responsabilidade, garantia, rescisão, devolução dos dados | Advogado |
| Código de Defesa do Consumidor | Quando o cliente for consumidor final: informação clara, garantia legal, direito de arrependimento em venda fora do estabelecimento | Advogado |
| **Anatel** | A Estação Avante tem rádio (Wi-Fi/Bluetooth e leitor de 13,56 MHz). Usar módulos homologados **não** dispensa a análise do produto final: avaliar com um organismo de certificação designado a necessidade de homologação do equipamento e a forma correta de identificação (etiqueta com os códigos dos módulos) antes de vender | Responsável + organismo de certificação |
| Segurança elétrica | Fonte de alimentação certificada; manual com avisos de segurança | Responsável |
| Descarte | Orientação de descarte de eletrônicos e baterias no manual | Responsável |
| Repositório | Tornar o repositório **privado** antes da venda (ou definir formalmente uma licença de código), revisar o histórico em busca de segredos e documentos internos | Responsável |

## 8. Marca

O produto é vendido como "Avante Almoxarifado" com a logo da Avante Tech Jr, salvo decisão de outro nome. A troca de nome e identidade é feita no ponto único de marca (RF-APP-09), sem mudar código. Antes de usar outro nome, verificar disponibilidade de marca no INPI e de domínio.

## 9. Preço (estrutura para decisão)

O preço não é definido neste documento. A planilha de decisão deve considerar: custo de hardware da Estação Avante (lista de materiais + montagem + garantia), horas de implantação, horas de suporte por cliente por mês, custo do backup externo e do domínio, impostos da forma jurídica escolhida, e o valor percebido medido nas entrevistas (§2).

## 10. Decisões em aberto

| ID | Decisão | Quando |
|---|---|---|
| DA-03 | Modelo de licença (assinatura × perpétua + suporte) e comportamento ao expirar | R4 |
| DA-COM-01 | Forma jurídica da venda e emissão de nota fiscal | Antes da R4 |
| DA-COM-02 | Titularidade da propriedade intelectual e termos de cessão | Antes da R4 |
| DA-COM-03 | Preço e planos | R4 |
| DA-COM-04 | Número máximo de clientes ativos por capacidade de suporte | Após o cliente piloto |
| DA-EMB-02 | Hardware final da Estação Avante (Volume 05) | R4 |
