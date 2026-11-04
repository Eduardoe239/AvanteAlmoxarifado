# Atualização incremental — Perfil e Central de Suporte

## Alterações
- Avatar do perfil ampliado.
- Chamados mostram foto do membro no painel administrativo.
- Chamados aceitam até quatro imagens PNG/JPEG/WebP de até 1 MB cada.
- Histórico de mensagens/respostas persistido em JSON na tabela mensagens_contato.
- Usuário pode concluir, reabrir ou informar que o problema não foi resolvido.
- Painel administrativo separa chamados concluídos dos ativos.
- Migração Alembic `7f4a2c9e1b60_suporte_historico_anexos.py`.

## Antes de atualizar
Faça backup do PostgreSQL e preserve `.env` e volumes Docker. Não use `docker compose down -v`.

## Validação
Os arquivos Python passaram por `py_compile`. Não foi possível executar build Next.js, testes de integração ou validar a migração contra um PostgreSQL real neste ambiente. Faça `docker compose up -d --build` em uma cópia de teste e confira os logs antes de promover a versão.
