# Volume 10 — Operação, Backup, Atualização e Incidentes

**Produto:** Avante Almoxarifado · **Versão:** 3.0.0 · **Data:** 17/11/2026 · **Status:** Proposto — aguarda aprovação
**Responsável:** Luís Eduardo de Sousa Barbosa
**Relação:** RNF-06, RNF-07, RNF-13, RNF-14, RNF-21, RNF-22; ADR-002, ADR-007, ADR-012, ADR-013; Volume 04 (hardware) e Volume 06 (segurança).
**Público:** quem administra a instalação (na Avante, o Proprietário e um Administrador substituto; no cliente, o responsável de TI indicado no contrato).

---

## 1. Papéis na operação

| Papel | Quem (Edição Avante) | Responsabilidades |
|---|---|---|
| Proprietário da instalação | Coordenador de Sistemas Embarcados | Decisões de risco, chave do backup, aprovação de atualizações maiores, comunicação de incidentes |
| Administrador substituto | Um membro indicado e treinado | Executar os runbooks quando o Proprietário não estiver disponível |
| Guardião físico | Quem tem a chave do laboratório | Ligar o notebook, conferir cabo e energia, nunca fechar a tampa nem levar o notebook |

**Continuidade:** como o projeto tem um único desenvolvedor, todo procedimento deste volume deve poder ser executado pelo Administrador substituto só com este documento e o manual de operação. Isso é testado na R2 (restauração feita pelo substituto).

## 2. Ferramenta de operação (`avante`)

| Comando | Faz |
|---|---|
| `avante status` | Estado dos serviços, versão, uso de memória e disco, último backup, últimos alertas |
| `avante doctor` | Verificação completa: energia e tampa, horário, certificado, DNS, disco (SMART, espaço, crescimento), temperatura, integridade do banco, backup recente, restauração testada no mês, dispositivos |
| `avante backup now` | Backup imediato (prioridade baixa de I/O) |
| `avante backup list` / `check` | Lista pontos de restauração / verifica a integridade do repositório |
| `avante restore` | Restauração guiada (ponto no tempo, destino, confirmação dupla) |
| `avante update` | Atualização com verificação de assinatura, backup prévio, migração, health check e volta automática (ADR-013) |
| `avante rollback` | Volta para a versão anterior |
| `avante support-access` | Abre/fecha o acesso remoto do fornecedor com prazo e registro (RF-COM-02) |
| `avante export` | Exportação completa dos dados da organização (RF-DAT-03) |

Toda execução é registrada na auditoria com o operador do SO.

## 3. Monitoramento e alertas

| Sinal | Limite de alerta | Canal |
|---|---|---|
| Serviço parado | Qualquer serviço fora por > 1 min | E-mail + push ao Proprietário e ao substituto |
| Backup | Nenhum backup completo em 8 dias ou WAL não enviado há > 30 min | E-mail + push |
| Teste de restauração mensal | Falhou ou não rodou | E-mail + push |
| Disco | > 80% (aviso), > 90% (crítico) | E-mail + push + faixa no painel do Administrador |
| SMART | Qualquer atributo crítico alterado | E-mail + push (crítico) |
| Temperatura | Acima do limite do processador por > 10 min | E-mail |
| Memória | Troca (swap) > 20% por 1 h | E-mail |
| Tempo de resposta | p95 acima da meta do RNF-05 por 15 min | Painel; e-mail se persistir por 1 dia |
| Certificado | Vence em < 14 dias e a renovação falhou | E-mail + push |
| Energia | Servidor na bateria | Push |
| Dispositivo | Sem heartbeat por > 5 min no horário de uso | Painel + push ao Operador do balcão |
| Segurança | Pico de logins falhos, sessão revogada em massa, dispositivo recusado repetidamente | E-mail + push |

Alertas usam o próprio sistema de notificações (e-mail com fila e reenvio). Se o servidor estiver fora do ar, quem avisa é a falta de resposta: o Proprietário configura um verificador externo gratuito de disponibilidade apontando para a rota pública de saúde pela VPN/túnel (decisão DA-OPS-01).

## 4. Backup e restauração

| Item | Regra |
|---|---|
| O que entra | Banco (base semanal + WAL contínuo), arquivos (fotos, anexos, modelos), configuração, certificados e chaves do serviço |
| Destinos | Repositório externo criptografado (S3 compatível, DA-04) **e**, recomendado, um disco USB guardado fora do notebook |
| Frequência | Base semanal (domingo, 2h); WAL contínuo, enviado a cada ≤ 5 min (RPO ≤ 15 min) |
| Retenção | 7 diários, 4 semanais, 12 mensais (configurável) |
| Chave | Com o Proprietário; cópia impressa em envelope lacrado no cofre/armário indicado; sem ela, **não há recuperação** |
| Verificação | `restic check` semanal; **restauração automática mensal** em diretório temporário com contagem de registros; restauração manual completa em outra máquina **a cada semestre** |

## 5. Atualização

1. Releases saem nos canais `beta` (homologação) e `stable` (produção).
2. Atualizações de segurança do SO são automáticas; reinício na janela 1h–5h.
3. Atualização do Avante Almoxarifado: aplicada pelo Proprietário fora do horário de uso, com aviso aos usuários 24 h antes quando houver indisponibilidade prevista.
4. `avante update` faz backup antes, migra, verifica e volta sozinho se falhar.
5. Versões com migração que não pode ser desfeita são marcadas nas notas de versão e exigem confirmação explícita.

## 6. Calendário de manutenção

| Quando | O quê |
|---|---|
| Diário (automático, 1h–5h) | Reconciliação de saldos; limpeza de sessões e arquivos temporários; envio de WAL; `avante doctor` resumido |
| Semanal (automático) | Backup base; `restic check`; SMART curto; relatório de saúde por e-mail ao Proprietário |
| Mensal (automático + leitura humana) | Teste automático de restauração; SMART longo; verificação de bateria; revisão dos alertas do mês; atualização de dependências pendentes |
| Semestral (presencial) | Restauração completa em outra máquina pelo Administrador substituto; limpeza física, ventilação e pasta térmica; inspeção da bateria; revisão de usuários e papéis; teste de queda de energia |
| Anual | Revisão do plano de resposta a incidentes; revisão do inventário de dados pessoais (Volume 06 §4.2); avaliação de troca de hardware (Volume 04 §11) |

## 7. Runbooks

Cada runbook tem versão detalhada, com comandos, no manual de operação. Aqui fica o roteiro de decisão.

### RB-01 — Sistema fora do ar
1. Do celular na rede local, abrir o endereço. Se não abrir, ir ao notebook.
2. Notebook desligado → ligar; aguardar 5 min; testar. Ligado → `avante status`.
3. Serviço parado → `avante doctor` mostra a causa; reiniciar o serviço; se repetir, ver o log indicado.
4. Disco cheio → RB-04. Banco não sobe → RB-05.
5. Registrar o ocorrido no painel de incidentes.

### RB-02 — Queda de energia
1. Ao voltar a energia, conferir se o notebook ligou sozinho (se a BIOS não religa, ligar manualmente).
2. Esperar até 5 min e rodar `avante doctor`.
3. Se houver alerta de integridade, **não** usar o sistema; seguir RB-05.

### RB-03 — HD com falha (alerta SMART)
1. Rodar `avante backup now` imediatamente e confirmar que terminou.
2. Evitar escrita desnecessária; avisar os usuários.
3. Providenciar disco novo (preferencialmente SSD) e seguir RB-06 para restaurar nele.
4. Não tentar "consertar" o disco com ferramentas de reparo antes de ter um backup verificado.

### RB-04 — Disco cheio
1. `avante doctor` mostra o que cresceu (WAL acumulado por falha de envio, logs, anexos).
2. WAL acumulado → resolver o envio ao backup (rede, credencial, espaço do destino). **Nunca** apagar WAL manualmente.
3. Anexos → aplicar a retenção configurada; avaliar disco maior.

### RB-05 — Banco corrompido ou dados errados
1. Parar o acesso (modo manutenção).
2. Identificar o momento do problema pela auditoria.
3. Restaurar no ponto imediatamente anterior em ambiente separado; comparar; só então restaurar em produção, com aprovação do Proprietário.
4. Movimentações feitas depois do ponto restaurado são recuperadas pela auditoria e relançadas como novas movimentações, com motivo.

### RB-06 — Trocar de máquina ou restaurar após perda
1. Instalar o sistema operacional e o pacote na máquina nova (manual de instalação).
2. `avante restore` a partir do backup externo, com a chave.
3. Ajustar o IP reservado no roteador; renovar certificados se necessário; reemparelhar a VPN.
4. `avante doctor`; teste rápido com um usuário; comunicar o retorno.
5. Meta: até 4 h (RNF-07).

### RB-07 — Notebook furtado ou perdido
1. Revogar todas as sessões e credenciais de dispositivos a partir de um backup restaurado em outra máquina.
2. Trocar a chave da VPN, as credenciais do backup externo e os segredos do serviço.
3. Avaliar o incidente de dados pessoais (RB-09).

### RB-08 — Dispositivo do balcão com defeito
1. Painel de dispositivos: ver último heartbeat e erro.
2. Reiniciar o dispositivo; se a credencial for recusada, reemparelhar.
3. Enquanto isso, o balcão continua pelo app (busca por nome ou leitura do QR do perfil).

### RB-09 — Incidente de segurança ou de dados pessoais
1. **Detectar e registrar:** o que, quando, quem percebeu.
2. **Conter:** revogar sessões e credenciais envolvidas; isolar o servidor da rede externa se necessário.
3. **Avaliar:** quais dados e quantas pessoas; se há risco ou dano relevante aos titulares.
4. **Comunicar:** havendo risco ou dano relevante, comunicar a ANPD e os titulares no prazo da regulamentação vigente (verificar a norma em vigor no momento do incidente). Na Edição Comercial, o cliente é o controlador: a Avante avisa o cliente sem demora.
5. **Corrigir a causa** e registrar as lições; atualizar este volume se preciso.

## 8. Decisões em aberto

| ID | Decisão | Quando |
|---|---|---|
| DA-04 | Destino do backup externo e guarda da chave | R0 |
| DA-OPS-01 | Verificador externo de disponibilidade | R1 |
| DA-OPS-02 | Quem é o Administrador substituto | R1 |
