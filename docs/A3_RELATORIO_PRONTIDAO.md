# Anexo A3 — Relatório de Prontidão para o Início do Desenvolvimento

**Produto:** Avante Almoxarifado · **Versão:** 3.0.0 · **Data:** 17/11/2026 · **Status:** Proposto — aguarda aprovação
**Substitui:** Relatório de Prontidão de 03/11/2026 (conjunto 2.3).
**Pergunta:** a documentação está completa, consistente e executável para iniciar o desenvolvimento, considerando:
- notebook antigo (DDR3, HD) como servidor e banco;
- cerca de 30 pessoas com acesso;
- um único desenvolvedor com o Claude Code;
- venda como sistema de estoque inteligente com visão computacional e embarcados?

**Veredito:** **PRONTO PARA INICIAR A R0**, depois da aprovação do conjunto e da autorização do responsável (§4).
- Nenhuma pendência bloqueia o início.
- As pendências do §5 se resolvem **durante** a R0, e são exatamente o que os critérios de saída da R0 verificam (Volume 09 §6).
- A R0 começa provando o hardware (R0-04, R0-05) antes de qualquer funcionalidade. Assim, se o notebook não aguentar, isso aparece cedo e com dados.

---

## 1. Lacunas apontadas em 17/11/2026 e como foram fechadas

| Lacuna | Onde foi resolvida |
|---|---|
| Sem requisitos mínimos de hardware | Volume 04 §2: Perfis Mínimo, Recomendado e Certificado. RF-COM-01 cobre a verificação pelo instalador |
| Sem orçamento de recursos para o notebook | Volume 04 §4: memória por serviço (≈ 860 MB normal, ≈ 1.630 MB pico), PostgreSQL ajustado para HD e disciplina de disco. RNF-20 e RNF-22 |
| Meta de desempenho para 20 usuários, sem relação com a realidade | RNF-05 revisto: 10 simultâneos (cerca de ⅓ de ~30 pessoas) e 60 conexões em tempo real, medido no Perfil Mínimo. Teste de carga no notebook real na R0-05 |
| HD sem tratamento | Volume 04 §4.3 e §7 (SMART, disciplina de I/O); Volume 10, RB-03 |
| Sem importação de planilhas nem exportação completa | RF-DAT-01..03 |
| Sem acesso remoto do fornecedor para suporte | RF-COM-02; Volume 11 §5 |
| Sem política de versões suportadas | Volume 11 §5 (N e N-1) |
| Sem backlog nem modelo de capacidade para um desenvolvedor | Volume 12: backlog da R0 com 20 tarefas, tamanhos e calibração; WIP = 1 |
| Visão computacional e embarcados sem especificação | Volume 05; RF-CV, RF-EMB, RF-AUT; RNF-23, RNF-24; ADR-024, 025, 027, 028 |
| Requisitos legais e regulatórios da venda | Volume 11 §7: forma jurídica, propriedade intelectual, LGPD, contrato, CDC, Anatel, segurança elétrica |
| Operação sem runbooks | Volume 10: monitoramento, calendário de manutenção e 9 runbooks |
| Instruções para o Claude Code | Volume 13, `CLAUDE.md`, comandos, agente revisor e travas de permissão em `.claude/` |
| Dependência de uma só pessoa | Administrador substituto (Volume 10 §1), procedimentos executáveis só com o manual e restauração feita pelo substituto na R2 |

## 2. Conjunto validado

**Documentos:**
- Volumes 00 a 13 e anexos A1 a A3.
- `CLAUDE.md` e `.claude/`: 4 comandos, 1 agente e `settings.json`.
- `brand/`.

**Números:**
- 154 requisitos funcionais e 24 não funcionais.
- 28 ADRs.
- 13 jornadas de usuário.
- 20 tarefas na R0.

## 3. Validação executada (resultados reais da última execução)

### 3.1 Verificações automáticas

| # | Verificação | Resultado |
|---|---|---|
| 1 | Todo RF citado em qualquer documento (inclusive intervalos `..`) existe no Volume 02 | 0 faltando |
| 2 | Todo RNF citado existe | 0 faltando |
| 3 | Toda ADR citada existe | 0 faltando |
| 4 | Toda referência "Volume NN §x" aponta para seção existente; todo volume e anexo citado existe | 0 faltando |
| 5 | Todo requisito M ou S tem release (R0–R4) | 0 sem release |
| 6 | A release de cada requisito no Volume 02 coincide com o conteúdo das releases no Volume 12 | 0 divergências |
| 7 | Nenhuma referência aos arquivos antigos (fora do mapa do Volume 00) nem termos antigos "Fase N", "Gate N", "Marco M" | 0 ocorrências |
| 8 | Nenhum identificador do diagnóstico interno do MVP nos documentos públicos; relatório do diagnóstico fora do Git | 0 ocorrências; arquivo ausente do repositório |
| 9 | Soma do orçamento de memória (Volume 04 §4.1) | Normal 350+300+120+40+50 = 860 MB; pico (backup sem tarefa pesada do worker) 500+450+120+100+60+400 = 1.630 MB; com o SO, ≈ 2,0 GB, dentro do RNF-20 |
| 10 | Contraste WCAG das combinações do design system | 30/30 aprovadas |
| 11 | `.claude/settings.json` é JSON válido | OK |

### 3.2 Problemas encontrados e corrigidos durante a validação

| # | Problema | Correção |
|---|---|---|
| 1 | Volume 01 ainda usava a numeração antiga de fases ao falar da confirmação de carga | Trocado por "R0" |
| 2 | RF-IMP-02 citava um identificador do diagnóstico interno do MVP | Substituído por descrição do defeito |
| 3 | Volume 08 citava um identificador do diagnóstico interno do MVP | Substituído por descrição do defeito |
| 4 | Volume 07: UX-DA-01 com prazo na numeração antiga de fases | Apontado para a tarefa R0-14 |
| 5 | Anexo A1 citava o arquivo antigo da estratégia de QR | Apontado para o Volume 08 |
| 6 | Anexo A1 tinha identificadores do diagnóstico interno | Trocados por "corrige defeito encontrado no MVP" |
| 7 | Volume 07: subseções novas inseridas antes da 8.8 | Reordenadas (8.8, 8.9, 8.10) |
| 8 | ADR-016 não tratava pesos pré-treinados em conjuntos com termos restritivos | Regra de registro na ficha do modelo e revisão jurídica antes da venda |

### 3.3 Limites da validação (declarados)

- **Revisão:**
  - A consistência foi verificada por script e por releitura das seções críticas.
  - Não houve revisão por uma segunda pessoa.
  - A primeira tarefa (R0-01) é a sua leitura e aprovação.
- **Metas marcadas com †** (desempenho, disponibilidade, recuperação, visão computacional): são propostas baseadas em estimativa e só se confirmam medindo no notebook real (R0-05) e no protocolo de avaliação (R3).
- **Notebook:** o modelo exato ainda não é conhecido. A presença de TPM 2.0, o religamento automático pela BIOS e a saúde do HD são verificados na R0-02 e na R0-04.
- **Capacidade:** as horas por semana disponíveis não foram informadas. Por isso, o Volume 12 não promete datas antes da calibração (R0-20).
- **Questões legais e regulatórias:** o Volume 11 lista obrigações para orientar decisões e não substitui advogado nem organismo de certificação.
- **Versões de plataforma:** foram conferidas em novembro de 2026 e mudam com o tempo; a ADR-022 define como mantê-las atualizadas.

## 4. Condições para iniciar a R0

| # | Condição | Situação |
|---|---|---|
| C1 | Aprovação do conjunto v3.0.0 (ou ajustes) | Aguardando o responsável |
| C2 | Autorização para publicar a documentação na branch `definitivo` (push) | Aguardando o responsável |
| C3 | Autorização explícita para iniciar a R0 com o Claude Code | Aguardando o responsável |

## 5. Pendências da R0 (não bloqueiam o início; bloqueiam a saída da R0)

| Pendência | Tarefa |
|---|---|
| Acesso físico ao notebook, modelo, BIOS e saúde do HD | R0-02, R0-04 |
| Teste de carga no notebook dentro do orçamento | R0-05 |
| Domínio e escolha entre VPN e túnel | R0-07 |
| Celulares (Android e iPhone) e tablet para os testes | R0-08 |
| Destino do backup externo e guarda da chave | R0-09 |
| Agenda com 6–8 membros para entrevistas e 5 para o teste do protótipo | R0-10, R0-13 |
| Protótipo no Claude Design aprovado | R0-12 |
| Arquivo vetorial original da logo | R0-14 |
| Horas por semana disponíveis | R0-20 |
