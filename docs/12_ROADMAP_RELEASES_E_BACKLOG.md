# Volume 12 — Roadmap, Releases e Backlog

**Produto:** Avante Almoxarifado · **Versão:** 3.0.0 · **Data:** 17/11/2026 · **Status:** Proposto — aguarda aprovação
**Responsável:** Luís Eduardo de Sousa Barbosa
**Relação:** ADR-026; critérios de saída no Volume 09 §6; forma de executar no Volume 13.

---

## 1. Como o trabalho é organizado

- **Desenvolvedor único, com o Claude Code como executor.** O responsável define a tarefa, aprova planos e designs, revisa e aceita; o Claude Code implementa, testa e relata seguindo o Volume 13. O gargalo real é o **tempo de revisão do responsável**, e o plano é dimensionado para ele.
- **Releases incrementais (R0 → R4).** Cada release entrega valor utilizável e termina com os critérios do Volume 09 §6 aprovados. Não se começa uma release com a anterior pendente.
- **Uma tarefa por vez (WIP = 1).** Uma tarefa só começa quando a anterior está aceita ou formalmente em espera.
- **Fatias verticais.** Cada tarefa de funcionalidade entrega banco, API, tela, testes e documentação juntos.
- **O MVP continua funcionando** até a R2, sem nenhuma alteração (ADR-001, ADR-026).

## 2. Modelo de capacidade

| Tamanho | Esforço de foco do responsável (planejar, revisar, testar em aparelho, aceitar) | Exemplos |
|---|---|---|
| P | ≈ 2 h | Ajuste de tela, nova validação, relatório simples |
| M | ≈ 4 h | Funcionalidade com uma tela e uma regra de negócio |
| G | ≈ 8 h | Fluxo completo (ex.: empréstimo com aprovação e devolução) |
| GG | Proibido | Dividir em tarefas menores antes de começar |

**Calibração:** as 4 primeiras semanas da R0 medem as horas reais por tamanho e as horas por semana disponíveis (**H**). A partir daí, a previsão de cada release = soma dos tamanhos ÷ H, com margem de 30% para imprevistos, provas e férias. A previsão é refeita ao fim de cada release e registrada no Anexo A3. **Datas não são prometidas antes da calibração.**

**Ritmo sustentável:** semanas de provas reduzem H; a previsão considera o calendário acadêmico. Nenhuma tarefa de risco alto é aceita na pressa.

## 3. Releases

### R0 — Fundação
**Objetivo:** provar que o notebook aguenta, que a rede e a câmera funcionam, que o design está aprovado e que a base técnica está pronta.

| ID | Tarefa | Tam. | Saída |
|---|---|---|---|
| R0-01 | Aprovar os volumes v3.0.0 e responder às decisões em aberto que já podem ser respondidas | P | Registro no Volume 00 |
| R0-02 | Preparar o notebook: inventário do hardware, `memtest86+`, SMART inicial, BIOS (religamento automático, virtualização), instalação do Debian 13 ou Ubuntu Server sem interface gráfica | M | Ficha do notebook (Volume 04 §3) |
| R0-03 | Reavaliar PostgreSQL 19 × 18 e fixar as versões (ADR-022) | P | Registro na ADR-022 |
| R0-04 | Script `ops/verificar-hardware.sh` e execução no notebook; decisão de criptografia (ADR-012) assinada | M | Relatório + decisão de risco |
| R0-05 | Teste de carga sintético no notebook: PostgreSQL ajustado (Volume 04 §4.2) + API mínima + 100 mil movimentações geradas + k6 | G | Relatório dentro do orçamento (RNF-05, RNF-20) ou plano de mitigação |
| R0-06 | Medição HD × SSD (opcional, se houver SSD disponível) | P | Dados para a decisão do Volume 04 §10 |
| R0-07 | Validação de rede: domínio (DA-02), certificado por DNS-01, HTTPS na rede local e fora, VPN ou túnel (DA-01), proteção de DNS rebinding do roteador | G | Relatório e escolha registrada na ADR-007 |
| R0-08 | Câmera lendo QR por HTTPS em Android e iPhone, dentro e fora da rede; Web Push; definição da matriz de aparelhos (DA-05) | M | Matriz no Volume 09 §4 |
| R0-09 | Backup: destino externo e guarda da chave (DA-04); backup e restauração de banco vazio | M | Procedimento testado |
| R0-10 | Pesquisa com usuários: entrevistas com 6–8 membros de 3+ papéis; observação do balcão e de um inventário | M | Personas, jornadas atuais, dores priorizadas |
| R0-11 | Classificação de cartões para validar a navegação | P | Mapa de navegação aprovado |
| R0-12 | ✅ **Aprovado em 17/11/2026 (D-18).** **Claude Design:** design system visual (cores sóbrias, tipografia, componentes) e protótipo navegável de J1–J7 em celular e notebook | G | Protótipo aprovado pelo responsável |
| R0-13 | Teste do protótipo com 5 usuários e ajustes | M | Relatório de usabilidade e protótipo revisado |
| R0-14 | Obter o arquivo vetorial original da logo da Avante Tech Jr | P | Arquivo em `brand/` |
| R0-15 | Fundação do backend: estrutura modular, camada de plataforma, configuração, logs estruturados, `request_id`, health checks, migrations iniciais, Argon2id calibrado no processador real | G | Código + testes |
| R0-16 | Fundação do frontend: SPA/PWA, tokens fiéis ao design aprovado, temas claro/escuro, componentes base no Storybook, ponto único de marca | G | Design system v0.1 em código |
| R0-17 | CI bloqueante: lint, tipos, testes, migrations (vazio e N-1), build, SAST, dependências, segredos, licenças, SBOM, job de desempenho; testes da camada de plataforma também em Windows | G | CI verde sem etapa mascarada |
| R0-18 | Pacote `.deb` mínimo + `avante status`/`doctor` básicos, instalando em VM limpa e no notebook | G | Instalação reproduzível |
| R0-19 | Revisão do modelo de ameaças (Volume 06) com a infraestrutura real | P | Volume 06 atualizado |
| R0-20 | Calibração de capacidade (§2) | P | H e horas por tamanho registrados |

### R1 — Núcleo (uso real em paralelo ao MVP)
**Conteúdo:** identidade e segurança (RF-IAM, exceto IAM-05); organização (RF-ORG); catálogo (RF-CAT-01..07); unidades e saldos (RF-INV-01..05); movimentações com ledger (RF-MOV-01..06); empréstimos (RF-EMP-01..07); QR e etiquetas (RF-QR-01..08, 10, 11, 14); políticas (RF-POL); aplicativo e tempo real (RF-APP-01..07, 09); notificações (RF-NOT-01, 02, 04, 05); suporte (RF-SUP-01..07, 10); colaboração (RF-COL-01); relatórios (RF-REL-01, 03, 04); auditoria (RF-AUD); administração (RF-ADM-01..03, 05, 06); verificação básica de hardware (RF-COM-01).

**Ordem sugerida das fatias:** identidade → organização → catálogo → unidades e ledger → QR e etiquetas → empréstimos → políticas → notificações → suporte → relatórios → administração → 1ª rodada de usabilidade → período paralelo de 4 semanas.

### R2 — Completo (MVP aposentado)
**Conteúdo:** passkeys (RF-IAM-05); kits (RF-INV-06); restante de catálogo, movimentações e empréstimos (RF-CAT-08, RF-MOV-07, RF-EMP-08, 09); QR avançado e modo balcão (RF-QR-09, 12, 13); documentos fiscais (RF-DOC); inventário físico (RF-CNT-01..03); notificações e suporte restantes (RF-NOT-03, 06, RF-SUP-08, 09); RF-COL-02; RF-REL-02; modo quiosque (RF-EMB-08); **importação do MVP** (RF-IMP); revisão heurística, acessibilidade, 2ª usabilidade e pentest interno.

**Critérios para aposentar o MVP:** (1) checklist de paridade do Anexo A1 100%; (2) importação ensaiada em ambiente isolado com totais conciliados e aprovada pelo responsável; (3) importação final feita com o MVP em modo somente leitura; (4) duas semanas de uso exclusivo do produto novo sem incidente de dados; (5) dump final do MVP arquivado em backup criptografado; (6) aviso aos membros. Só então o MVP é desligado — a branch `main` permanece intocada como histórico.

### R3 — Inteligente
**Conteúdo:** visão computacional (RF-CV-01..06) seguindo o Volume 05; leitor de cartão de balcão e dispositivos (RF-EMB-01..06); automação (RF-AUT-01..03); relatório de impacto para cartões (DA-EMB-01); usabilidade de J11–J13. Um recurso de visão que não atinge a meta do RNF-23 **fica desativado** e não bloqueia o restante da release.

### R4 — Comercial
**Conteúdo:** servidor em Windows com `.msi` assinado e paridade completa; licença (RF-ADM-04, ADR-014); importação de planilhas e exportação completa (RF-DAT); acesso de suporte do fornecedor, termos e assistente de implantação (RF-COM-01 completo, RF-COM-02..04); Estação Avante (RF-EMB-07); obrigações do Volume 11 §7; pentest externo; cliente piloto externo.

### Pós-R4 (planejado, sem compromisso de data)
RF-EMP-10, RF-CNT-04, RF-APP-08, RF-AUT-04, RF-CV-07, RF-CV-08.

## 4. Riscos do roadmap

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Notebook não aguenta a carga | Média | Alto | R0-05 antes de qualquer funcionalidade; plano de SSD/8 GB; critérios de migração (Volume 04 §11) |
| HD falha durante o uso | Média | Alto | SMART, backup externo com RPO de 15 min, RB-03, restauração testada |
| Pouco tempo do desenvolvedor (estudos, outros projetos) | Alta | Alto | Releases pequenas e úteis; WIP = 1; calibração de capacidade; Claude Code como executor |
| Dependência de uma pessoa | Alta | Alto | Documentação executável, Administrador substituto treinado (Volume 10), Claude Code guiado por `CLAUDE.md` |
| Visão computacional não atinge a meta | Média | Médio | Visão clássica primeiro; bandeja padrão; recurso desativado se não atingir; o produto vale sem ele |
| Requisitos legais da venda (forma jurídica, Anatel, LGPD) | Média | Alto | Volume 11 §7 antes da R4; Essencial pode ser vendida antes da Estação |
| Repositório público expor algo sensível | Baixa | Alto | Varredura de segredos bloqueante; nenhum dado real; privado antes da venda |
| Escopo crescer | Alta | Médio | Mudança de escopo só por decisão registrada no Volume 00 |
