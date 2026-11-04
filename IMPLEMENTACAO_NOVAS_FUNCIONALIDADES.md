# Avante Almoxarifado — implementação das funcionalidades solicitadas

Esta versão preserva os componentes existentes e adiciona os fluxos abaixo sem redesenhar as páginas já aprovadas.

## Funcionalidades incluídas

- Solicitação de devolução pelo usuário com status `PENDENTE_DEVOLUCAO`; o estoque só é reposto quando o administrador confirma a devolução.
- Área de geração de QR Code para itens cadastrados, com pré-visualização e download PNG.
- Importação de produtos de PDFs de notas fiscais, além do XML. PDFs com texto selecionável usam extração de texto; PDFs digitalizados tentam OCR via Tesseract.
- Conferência manual dos produtos extraídos antes da entrada no estoque.
- Histórico persistente de notas fiscais, com produtos extraídos, tipo do documento, responsável e total cadastrado.
- Central de contato do usuário com registro das mensagens e respostas no painel administrativo.
- Upload de foto de perfil (PNG/JPEG/WebP, até 2 MB), armazenada no PostgreSQL e exibida no perfil/cabeçalho.
- Notificação por e-mail quando um item novo é cadastrado manualmente ou por QR Code, além dos alertas de empréstimos já existentes.
- Configuração SMTP e idioma OCR expostos no `docker-compose.yml`.

## Configuração de e-mail

Defina no arquivo `.env` do projeto:

```env
EMAIL_HABILITADO=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USE_TLS=true
EMAIL_SENDER=seu-email@dominio.com
EMAIL_PASSWORD=senha-de-aplicativo-ou-credencial-smtp
```

Para Gmail, use uma senha de aplicativo. Não coloque credenciais reais no repositório.

## Migração

Foi adicionada a revisão Alembic `c1f8a2d4e6b0_recursos_operacionais.py`, descendente da revisão `8b7e6a1c2d90`. O histórico de migrações foi verificado com `alembic history`, sem heads duplicados no pacote.

Ao iniciar com Docker Compose, o script `start.sh` aplica a migração automaticamente. Faça backup do banco antes de atualizar qualquer ambiente com dados importantes. Não use `docker compose down -v`.

## Limites importantes

- A extração de PDF/DANFE é heurística e pode interpretar colunas de quantidade e preço de forma imperfeita, conforme o layout do fornecedor e a qualidade do OCR. A interface exige revisão antes do cadastro; não trate o resultado extraído como fonte fiscal infalível.
- O envio real de e-mails depende de credenciais SMTP válidas e de `EMAIL_HABILITADO=true`.
- A sintaxe Python e o grafo Alembic foram verificados nesta sessão. A compilação Next.js e os testes integrados com PostgreSQL/SMTP não puderam ser executados neste ambiente, pois a instalação de dependências do frontend excedeu o tempo disponível.
