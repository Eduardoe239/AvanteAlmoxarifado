# Revisão de UI/UX — Avante Almoxarifado

## Objetivo

Reorganizar o frontend para que o sistema seja compreensível no uso diário do almoxarifado, com uma hierarquia visual inspirada na referência enviada: navegação lateral persistente, área de trabalho clara, ações principais evidentes e estados de operação explícitos.

## O que foi atualizado

- **Painel administrativo:** navegação por áreas (Visão geral, Itens e estoque, Leitor QR, Notas fiscais, Empréstimos e Usuários), busca da navegação, estado de conexão/sincronização, layout responsivo e atalhos contextuais.
- **Visão geral:** indicadores carregados a partir das APIs existentes, visão de empréstimos e atrasos, acesso rápido às tarefas frequentes e atualização manual.
- **Catálogo de itens:** busca por nome, patrimônio, QR, área e setor; filtro por status; alinhamento entre cabeçalho e colunas; atualização explícita; estados vazios/erro; edição com valores atuais; possibilidade de limpar campos opcionais e confirmação inline antes da remoção.
- **Empréstimos:** corrigido o vínculo do seletor de item com o React Hook Form, normalizada a comparação do ID, melhorados os estados vazios e os erros recuperáveis, e removida a aparência de formulário disponível quando não há unidades para emprestar.
- **Usuários e perfil:** formulários tipados, valores atuais ao entrar no modo de edição, validação de nome completo, opção de senha como alteração opcional, feedback para falha ao carregar setores e confirmação ao desativar o acesso.
- **Consistência:** rótulos de status mais legíveis, formatação compartilhada de datas UTC, cabeçalho de navegação, metadata do app, indicadores de foco, redução de movimento e ajustes para telas estreitas.
- **Cadastro por QR:** texto auxiliar explica a regra existente que usa o patrimônio como identificador quando o campo do QR fica vazio.

## Escopo e preservação

As alterações foram concentradas no frontend e neste documento. Rotas, schemas, migrations, banco de dados, Docker Compose e arquivos de ambiente do backend não foram modificados por esta revisão. O ZIP não transporta os dados persistentes do Docker: continue usando o volume atual do banco e evite comandos destrutivos como `docker compose down -v` quando quiser preservar os registros.

## Como executar

Na pasta `frontend`:

```bash
npm ci
npm run dev
```

Use a URL local indicada pelo Next.js e mantenha o backend atual em execução, conforme a configuração de API do projeto.

## Validação realizada

- Transpilação/sintaxe dos arquivos `.ts` e `.tsx` com o compilador TypeScript: sem diagnósticos de sintaxe na checagem final.
- Verificação dos imports relativos/aliases locais e integridade do ZIP.
- **Build de produção e testes de navegador não foram confirmados neste ambiente:** a instalação das dependências não terminou pela rede e a tentativa offline não encontrou um pacote no cache local. Após `npm ci` bem-sucedido, valide com `npm run build` e teste os fluxos com o backend conectado antes de publicar.

## Refatoração específica — perfil e estoque (15/10/2026)

- **Meu perfil:** reorganizado em resumo de identidade com avatar por iniciais, nome de usuário, setor e papel; informações pessoais em estado de leitura/edição; nome de usuário explicitamente somente leitura; alteração de senha em fluxo separado, com validação de senha atual, força e confirmação; feedbacks de sucesso/erro e atualização do cabeçalho depois de salvar.
- **Estoque e itens:** visão superior com contadores calculados da listagem real da API; abas independentes para inventário e cadastro; busca insensível a acentos por nome, patrimônio, QR, área, setor e ID; filtros por status e setor; ordenação e paginação; disponibilidade visual por item; ações de edição em modal e confirmações de desativação/remoção; estados explícitos de carregamento, erro, tentativa de recuperação e lista vazia.
- **Responsividade e acessibilidade:** tabela com rótulos de campos em visualização móvel, controles rotulados, mensagens associadas aos campos, estados ARIA para abas/diálogos, suporte ao Escape no modal de edição e foco visível.
- **Escopo desta rodada:** foram alterados somente `frontend/src/components/MeuPerfil.tsx`, `frontend/src/app/perfil/page.tsx`, `frontend/src/components/admin/GerenciarItens.tsx`, `frontend/src/components/admin/CadastroItemForm.tsx`, o trecho de estoque em `frontend/src/app/admin/page.tsx` e estilos adicionados ao final de `frontend/src/app/globals.css`. Backend, migrations, banco, Docker Compose e demais seções de navegação não foram alterados nesta rodada.

## Validação complementar desta rodada

- Transpilação sintática de 19 arquivos `.ts`/`.tsx`: sem diagnósticos de sintaxe.
- A instalação das dependências necessárias para executar o build não foi concluída no ambiente; por isso o `tsc --noEmit`, o build Next.js e os testes de navegador seguem pendentes de execução em um ambiente com `npm ci` concluído.

## Como aplicar a atualização visual no Docker

Para atualizar o sistema que já está em execução, use o ZIP somente do frontend e substitua apenas a pasta `frontend` do projeto. Preserve a pasta `backend`, `docker-compose.yml`, o `.env` da raiz e os volumes existentes. No terminal aberto na raiz do projeto, execute:

```bat
docker compose build frontend
docker compose up -d --no-deps --force-recreate frontend
docker compose logs --tail=80 frontend
```

Esses comandos reconstruem e recriam somente o frontend. Não executam migrations nem recriam o banco.
