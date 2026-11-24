# Volume 06 — Segurança, Privacidade e LGPD

**Produto:** Avante Almoxarifado · **Versão:** 3.1.0 · **Data:** 24/11/2026 · **Status:** Aprovado em 24/11/2026
**Responsável:** Luís Eduardo de Sousa Barbosa
**Relação:** RNF-08, RNF-09, ADR-005, ADR-007, ADR-012, ADR-016, ADR-025, ADR-028.
**Aviso:** as seções sobre LGPD descrevem o desenho técnico e organizacional; os textos jurídicos (política de privacidade, termos, contratos) passam por revisão de advogado antes da venda (Volume 11).

---

## 1. Objetivos de segurança

1. Ninguém acessa ou altera dados sem estar autenticado e autorizado para aquilo.
2. Nenhuma alteração de estoque fica sem autor, data e motivo, e nenhuma pode ser apagada.
3. Os dados sobrevivem a falha de disco, furto do notebook e erro humano (backup criptografado e testado).
4. O servidor, mesmo acessível de fora, não expõe nenhuma porta diretamente à internet.
5. Dispositivos embarcados não abrem caminho de ataque para o restante do sistema.
6. Dados pessoais são os mínimos necessários e tratados conforme a LGPD.

Referência de verificação: **OWASP ASVS 4.0 nível 2**, com checklist por release.

## 2. Modelo de ameaças (STRIDE)

| Ameaça | Exemplos | Controles |
|---|---|---|
| **Falsificação de identidade** | Senha roubada; força bruta; sessão reaproveitada; **cartão copiado** | Argon2id; MFA obrigatório para papéis privilegiados; limites por conta e IP; sessões revogáveis; cartão só identifica e exige PIN no autoatendimento (ADR-025) |
| **Adulteração** | Alterar saldo ou histórico; dispositivo falso enviando eventos; firmware modificado | Ledger append-only; auditoria encadeada por hash; papéis de banco sem UPDATE/DELETE; credencial por dispositivo com escopo; Secure Boot e OTA assinado |
| **Repúdio** | "Não fui eu que dei baixa" | Auditoria com ator, dispositivo, IP, sessão e request_id |
| **Vazamento de informação** | Notebook furtado; backup copiado; evento em tempo real enviado a quem não pode ver; imagens com pessoas | Backup criptografado; criptografia de disco quando há TPM (ADR-012); autorização por escopo; filtragem de eventos no servidor; política de imagens (ADR-028) |
| **Negação de serviço** | Upload gigante; muitas requisições; muitas conexões em tempo real; dispositivo com defeito enviando sem parar | Limites antes de processar; rate limiting por usuário, IP e dispositivo; teto de conexões SSE; tarefas pesadas no worker; orçamento de recursos (Volume 04) |
| **Elevação de privilégio** | Membro acessando rota de gestor; IDOR; dispositivo chamando rota de usuário | RBAC com escopo verificado no serviço; testes horizontais e verticais por rota; escopo de dispositivo restrito; serviços do SO sem privilégio |

## 3. Controles por camada

### 3.1 Identidade e sessão
- Senhas Argon2id; mínimo de 10 caracteres; bloqueio de senhas vazadas (lista local); colar e gerenciadores de senha permitidos.
- Sessão opaca no servidor, cookie `__Host-` com `Secure`, `HttpOnly`, `SameSite=Strict`; expiração por inatividade e absoluta; revogação imediata (RF-IAM-03).
- MFA TOTP (e passkeys na R2); reautenticação para ações sensíveis.
- Recuperação de senha por link de uso único.

### 3.2 Aplicação web
- CSP estrita sem `unsafe-inline`; HSTS; `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` (câmera só na própria origem), `frame-ancestors 'none'`.
- CSRF: token de sincronização + verificação de `Origin`.
- Validação de toda entrada no servidor; consultas parametrizadas; XML sem entidades externas; templates de e-mail com escape automático.
- Uploads: tipo real detectado, limites de bytes e pixels antes de decodificar, reencodificação sem metadados (ADR-008).
- Mensagens de erro sem detalhes internos; `request_id` para rastrear.

### 3.3 Servidor e rede
- Firewall negando tudo; 443 só na rede local e na VPN; SSH só por chave, de preferência só pela VPN.
- PostgreSQL ouvindo só em `localhost`; papéis separados (migração × aplicação × relatórios somente leitura).
- Serviços com usuário próprio e sandbox (ADR-002); segredos em arquivos com permissão restrita.
- Atualizações automáticas de segurança do SO; janela de reinício fora do expediente.

### 3.4 Dispositivos embarcados
- Pareamento aprovado por administrador; credencial única por dispositivo; revogação imediata.
- TLS validando o certificado do servidor (sem "aceitar qualquer certificado").
- Escopo mínimo: o leitor de cartão só pode enviar "cartão apresentado" e o próprio heartbeat.
- Secure Boot, criptografia de flash e OTA assinado com reversão.
- Rate limiting por dispositivo; alertas de comportamento anômalo (ex.: leituras em excesso).

### 3.5 Cartões (RU, crachá, tags)
- Guardar o identificador do cartão **com hash e sal** no banco, nunca em texto puro; o vínculo é feito por comparação de hash.
- Cartão nunca é o único fator para autoatendimento (PIN) nem para ações sensíveis (login).
- Cartão perdido: o usuário ou o operador desvincula na hora.

### 3.6 Cadeia de suprimentos
- Dependências travadas por hash; varredura de vulnerabilidades e de licenças no CI; SBOM a cada release.
- Pacotes e firmware assinados; chaves de assinatura fora do repositório, com acesso só do responsável.
- Nenhum segredo no Git; varredura de segredos bloqueante.

### 3.7 Testes de segurança
- Testes automatizados de autorização para todas as rotas (inclusive de dispositivos).
- Varredura dinâmica (OWASP ZAP baseline) a cada release.
- Checklist ASVS L2 revisado por release; pentest interno antes da R2 (uso real completo) e externo independente antes da venda (R4).

## 4. Privacidade e LGPD

### 4.1 Papéis
| Situação | Controlador | Operador |
|---|---|---|
| Edição Avante | Avante Tech Jr | — |
| Edição Comercial, dados do cliente | O cliente | A Avante (ou a empresa que vender o produto) **só quando** acessar os dados para suporte, com consentimento e registro (RF-COM-02) |

### 4.2 Inventário de dados pessoais
| Dado | Finalidade | Base legal (a validar juridicamente) | Retenção |
|---|---|---|---|
| Nome, e-mail, setor, papel | Identificar quem usa e responde por materiais | Legítimo interesse / execução de contrato | Enquanto houver vínculo; depois, anonimização mantendo o histórico |
| Foto de perfil (opcional) | Reconhecimento visual entre membros | Consentimento | Até o titular remover |
| Identificador do cartão (com hash) | Identificação no balcão | Legítimo interesse, com opção de não usar cartão | Enquanto vinculado |
| PIN do autoatendimento (com hash) | Segundo fator na estação | Legítimo interesse | Enquanto ativo |
| Registros de acesso (IP, dispositivo, data) | Segurança e auditoria | Cumprimento de obrigação e legítimo interesse | 6 meses (referência do Marco Civil para registros de acesso a aplicações) |
| Mensagens e anexos de suporte | Atendimento | Execução de contrato / legítimo interesse | 2 anos após o fechamento (configurável) |
| Histórico de empréstimos e movimentações | Rastreabilidade do patrimônio | Legítimo interesse | Permanente, com anonimização do titular quando aplicável |

Imagens de visão computacional não são dados pessoais por desenho (ADR-028): só itens, nunca pessoas.

### 4.3 Direitos do titular
Confirmação de tratamento, acesso e portabilidade (exportação dos próprios dados — RF-IAM-13), correção pelo perfil, anonimização ao encerrar a conta, informação sobre compartilhamentos e revogação de consentimento (foto, cartão). Prazos e canal definidos na política de privacidade.

### 4.4 Cookies
Só é usado o cookie **estritamente necessário** de sessão; não há cookies de rastreamento ou de terceiros. Isso é informado na política de privacidade. Nenhuma ferramenta de analytics externa.

### 4.5 Relatório de impacto à proteção de dados
Obrigatório antes de ativar: cartões compartilhados entre sistemas da Avante (DA-EMB-01), câmeras fixas (RF-CV-08) e qualquer coleta nova de dado pessoal.

### 4.6 Incidentes
Plano de resposta no Volume 10: detectar, conter, avaliar risco aos titulares, comunicar à ANPD e aos titulares quando houver risco ou dano relevante, registrar e corrigir a causa.

## 5. Riscos aceitos (registrados)

| Risco | Por que é aceito | Compensação | Quem aceita |
|---|---|---|---|
| Notebook da Avante sem criptografia de disco (se não houver TPM 2.0) | Criptografia com senha no boot impede o religamento automático após queda de energia | Backups criptografados, segredos protegidos, notebook em local trancado, dados de baixa sensibilidade | Responsável, na R0, após verificar o hardware |
| UID de cartões comuns pode ser copiado | Os cartões já existentes (RU) não têm autenticação forte | Cartão só identifica; PIN no autoatendimento; operador confere no balcão | Responsável, na R3 |
| Repositório público durante o desenvolvimento | Decisão do responsável; CI gratuito | Sem segredos, sem dados reais, sem falhas não corrigidas publicadas; privado antes da venda | Responsável (03/11/2026) |
