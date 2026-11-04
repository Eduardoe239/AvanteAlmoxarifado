# Lab Almoxarifado

Sistema de controle de empréstimos do almoxarifado do laboratório.

## Estrutura

- `backend/` — API em FastAPI (Python)
- `frontend/` — Interface em Next.js (TypeScript)

## O que foi feito nesta rodada

### Setor editável no perfil e vinculado aos administradores

- **`PATCH /me` agora aceita `setor_id`.** Qualquer usuário pode corrigir o
  próprio setor pela aba "Meu Perfil" — antes o campo era só informativo ali,
  e mudar de setor dependia de pedir a um admin. O setor é validado contra a
  lista fixa (setor inexistente devolve 400). O que continua fora do
  autoatendimento é `username` e `is_admin`: identidade e privilégio não se
  alteram por conta própria.
- **`POST /admin/administradores/` passou a exigir `setor_id`.** Antes o
  admin nascia sempre com `setor_id=None`, o que deixava a coluna "Setor" do
  painel vazia para toda a equipe administrativa. Agora um administrador é
  vinculado a um setor como qualquer outra pessoa da organização.
- **Edição de setor liberada para administradores no painel.** O formulário
  inline de edição de usuário escondia o seletor de setor quando a linha era
  de um admin (`{!usuario.is_admin && ...}`); como admins agora têm setor,
  o seletor aparece para todo mundo.
- **95/95 testes passando** (eram 89), rodando contra PostgreSQL real. Os 6
  novos cobrem: alterar o próprio setor, recusar setor inexistente no
  perfil, admin criado já vinculado ao setor e aparecendo resolvido na
  listagem, cadastro de admin sem setor recusado (422), com setor inválido
  recusado (400), e edição do setor de um admin por outro admin.


### Correção de bugs críticos + perfil próprio + anti-spam das notificações

Esta rodada partiu de uma versão já modificada por você (Postgres-only,
empréstimo por quantidade, `email_service.py`, `tasks.py` com APScheduler e
a página de perfil). A análise encontrou **três bugs que quebravam o
sistema em produção**:

1. **Todos os endpoints de empréstimo retornavam 500.** Os schemas
   `EmprestimoResponse` e `EmprestimoAdminResponse` passaram a exigir o
   campo `quantidade`, mas os construtores de resposta no `main.py` não o
   preenchiam. Ninguém conseguia pegar item emprestado nem ver o painel.
   Corrigido nos dois construtores.
2. **A migração `5e66d94ccf2e` abortava num banco limpo.** Ela usava
   `server_default=False` (bool do Python) onde o Alembic exige expressão
   SQL, estourando `ArgumentError` no `alembic upgrade head`. Não aparecia
   em quem já tinha as colunas no banco local. Trocado por
   `sa.text('false')`.
3. **O frontend não compilava** — três erros de TypeScript no código novo
   de perfil: `usuario.eh_admin` (o campo é `is_admin`), `usuario.setor?.nome`
   (o tipo `Usuario` só carrega `setor_id`; o nome agora é resolvido pela
   lista de setores) e `<Header />` sem as props obrigatórias.

Além disso, na rota de autoatendimento:

- **`/me/deativar-conta` → `/me/desativar-conta`** (erro de digitação) e o
  corpo passou de `dict` cru para um schema `ConfirmacaoSenha` tipado, para
  a validação e a documentação automática funcionarem.
- **Lockout do último administrador bloqueado.** As rotas administrativas
  impedem um admin de desativar a si mesmo, mas a rota de autoatendimento
  existe justamente para isso — e permitia que o único admin do sistema se
  desativasse, deixando a instalação sem ninguém capaz de administrá-la
  (não há rota pública para promover admin). Agora é barrado com uma
  mensagem explicando o que fazer antes.

**Anti-spam do alerta de atraso:** o `tasks.py` reenviava o e-mail de
atraso a cada execução do scheduler — que roda de hora em hora — ou seja,
24 e-mails por dia para a mesma pessoa até a devolução (o próprio comentário
no código assumia a pendência). Agora há a coluna `ultimo_alerta_atraso`
(migração `7a1c3f9d2b04`) limitando o reenvio a **no máximo um por dia**, e
o registro só é marcado quando o envio de fato teve sucesso — assim uma
falha temporária de SMTP é reprocessada na execução seguinte em vez de o
aviso ser silenciosamente perdido.

**Isolamento dos testes com Postgres:** a massa de teste é inserida com IDs
explícitos, o que não avança as sequências do Postgres (diferente do
SQLite). O primeiro registro criado via API colidia em `id=1` e aparecia
como um enganoso `409 "já está em uso"`. O `conftest.py` agora sincroniza
as sequências após montar a massa.

**Variáveis de SMTP documentadas** no `.env.example` (`EMAIL_HABILITADO`,
`SMTP_SERVER`, `SMTP_PORT`, `EMAIL_USE_TLS`, `EMAIL_SENDER`,
`EMAIL_PASSWORD`) — antes não havia como descobrir os nomes sem ler o
código.

**89/89 testes passando** (eram 73), agora **rodando contra PostgreSQL
real**, não mais SQLite. 16 testes novos cobrem edição do próprio perfil,
troca de senha com confirmação da senha atual, autodesativação, proteção
do último admin e o controle de frequência dos e-mails de atraso.

### O que finalmente pôde ser testado contra Postgres de verdade

O ambiente desta sessão permitiu instalar PostgreSQL, então as pendências
que eu vinha declarando como "não verificadas por falta de infra" foram
efetivamente validadas:

- Cadeia completa de migrações num banco zerado, incluindo a FK
  `ON DELETE SET NULL`, com `downgrade` e `upgrade` de volta.
- Fluxo end-to-end com servidor real: cadastro, login, item com estoque,
  empréstimo por quantidade (estoque decrementado corretamente),
  `PATCH /me`, autodesativação e bloqueio do último admin.


### Edição e exclusão completa de usuário, e-mail (preparação p/ notificações), rebranding e navegação

- **Painel de usuário deixou de ser só ativar/desativar** — agora tem:
  - `PATCH /admin/usuarios/{id}`: edição completa (username, nome completo,
    e-mail, setor, e opcionalmente resetar a senha). Admin pode editar
    inclusive a própria conta (só desativar/excluir a si mesmo continua
    bloqueado). Testado de ponta a ponta: editei nome+setor+email da conta
    de um membro e resetei a senha dele, e a nova senha funcionou pra
    logar de verdade.
  - `DELETE /admin/usuarios/{id}`: exclusão de verdade (diferente de
    desativar) — mas o **histórico de empréstimos da pessoa é preservado**,
    porque um sistema de controle de patrimônio não pode perder auditoria.
    A referência ao usuário excluído nos empréstimos antigos vira `NULL`
    (`ON DELETE SET NULL`) e o painel mostra "(usuário removido)" no lugar
    do nome. Bloqueado apenas para auto-exclusão (mesma proteção contra
    lockout da desativação).
  - Frontend: cada linha da tabela de usuários agora tem Editar (formulário
    inline), Desativar/Reativar, e Excluir — este último com uma
    confirmação explícita antes de executar (não é um clique só).
- **Dois bugs reais encontrados e corrigidos nesse processo**:
  1. Uma checagem de "não pode desativar o último admin ativo" que eu
     tinha escrito era código morto — a proteção de "não pode desativar a
     própria conta" já garante matematicamente que sempre sobra pelo menos
     um admin ativo (quem chama a rota precisa ser admin ativo). Removi a
     checagem redundante.
  2. **`database.py` de produção não habilitava `PRAGMA foreign_keys=ON`
     no SQLite** — sem isso, o `ON DELETE SET NULL` da exclusão de usuário
     nunca disparava de verdade fora dos testes (só funcionava porque os
     testes tinham essa configuração feita separadamente). Corrigido e
     reconfirmado com servidor real rodando: agora `usuario_id` vira `null`
     de verdade no histórico após uma exclusão.
- **E-mail obrigatório no cadastro** (membro e admin), preparando o terreno
  pra notificação por e-mail que será implementada futuramente — a
  intenção explícita é: quando a notificação por e-mail existir de fato,
  todo mundo já vai ter um e-mail válido cadastrado. Contas antigas sem
  e-mail (criadas via `scripts/create_admin.py` sem `--email`, por exemplo)
  continuam funcionando normalmente e podem ser completadas depois pelo
  próprio painel de edição.
- **Rebranding**: página de login agora é "Avante Almoxarifado" (era
  "Sistema do Laboratório"); a aba de autocadastro virou "Cadastro" (era
  "Cadastrar"); a página de pegar item emprestado agora é só "Almoxarifado"
  em todo lugar (título, e o link de navegação que volta pra ela a partir
  do painel admin).
- **Navegação em formato de botão de verdade** — os links entre o painel
  admin e a página de empréstimo (nos dois sentidos) e o botão de sair
  foram redesenhados: antes eram texto sublinhado, agora são botões com
  borda, fundo e estado de hover, e o "Sair" ganhou um ícone.
- **73/73 testes passando** (eram 56 — 17 novos cobrindo edição, exclusão,
  preservação de histórico, e-mail obrigatório e duplicado).

### Edição/desativação de item e usuário, paginação e notificação de atraso

Resolvia as pendências #5, #6 e #7 da entrega anterior, nesta ordem:

**Edição e desativação de item:**
- `PATCH /admin/itens/{id}`: edição parcial (o admin só envia o que quer
  mudar — usa `model_dump(exclude_unset=True)` no Pydantic, então dá pra
  editar só o nome sem mexer nos outros campos). `quantidade_total` não
  pode ser reduzida abaixo do que já está emprestado agora: se o item tem
  5 unidades no total e 4 estão com alguém, tentar reduzir pra 2 dá 400.
  Quando a redução é válida, `quantidade_disponivel` é recalculada
  preservando a contagem de unidades já emprestadas (testado em
  `test_admin_edita_nome_e_quantidade_do_item`,
  `test_admin_nao_reduz_quantidade_abaixo_do_emprestado`).
- `POST /admin/itens/{id}/desativar` e `.../reativar`: item desativado
  some do catálogo (`GET /itens/` só mostra `ATIVO`), impedindo novos
  empréstimos — mas quem já tinha pegado o item continua podendo devolver
  normalmente (`test_item_desativado_ainda_pode_ser_devolvido`).
- `GET /admin/itens/` (novo): lista TODOS os itens, inclusive os
  `INATIVO` — diferente de `GET /itens/`, que só mostra `ATIVO`. Sem essa
  rota, o admin não teria como encontrar um item desativado de novo pra
  reativar.

**Desativação de usuário:**
- `GET /admin/usuarios/`: lista todos os usuários com setor já resolvido.
- `POST /admin/usuarios/{id}/desativar` e `.../reativar`: usuário
  desativado não consegue mais logar nem usar uma sessão já aberta — a
  checagem de `ativo` acontece a cada requisição, não só no login
  (testado em `test_membro_desativado_nao_consegue_mais_usar_a_sessao`,
  que verifica isso rodando com o mesmo cookie de sessão antes e depois da
  desativação). Proteção contra lockout: um admin não pode desativar a
  própria conta (`test_admin_nao_desativa_a_propria_conta`) — essa única
  regra já garante matematicamente que nunca fica zero admin ativo no
  sistema, então não existe (nem precisa existir) uma checagem separada de
  "último admin ativo": quem chama a rota já precisa ser um admin ativo, e
  como ele não pode se autodesativar, sempre sobra ele mesmo.

**Paginação:**
- `GET /admin/emprestimos/` agora devolve um envelope paginado
  (`{itens, total, pagina, tamanho_pagina, total_paginas}`) em vez de uma
  lista crua — parâmetros `pagina` e `tamanho_pagina` (máx. 100) via query
  string. Testado com 5 empréstimos e página de tamanho 2
  (`test_paginacao_de_emprestimos`) e pedir uma página além do total
  (`test_paginacao_pagina_vazia_alem_do_total`, devolve lista vazia, não
  erro).

**Notificação de atraso:**
- `GET /admin/emprestimos/atrasados/resumo` (novo): resumo só do que está
  atrasado agora, pensado pra um banner que aparece assim que o admin abre
  o painel — sem precisar vasculhar a lista paginada procurando linhas
  vermelhas. Testado com `freezegun` simulando o relógio real avançando até
  passar do prazo (`test_resumo_atrasados_detecta_emprestimo_vencido`).
  **Importante ser direto sobre o que isso é e não é**: é uma notificação
  dentro da própria aplicação (você só vê se abrir o painel), não um
  e-mail nem push notification — isso exigiria credenciais de um serviço
  de SMTP ou push que este projeto não tem configurado, e eu não iria
  inventar uma integração falsa só pra dizer que "resolvi". Pro membro, o
  princípio é o mesmo: a seção "Meus empréstimos" já mostra um banner
  vermelho no topo se ele tiver algo atrasado, assim que a página carrega.
- **56/56 testes passando** (eram 31 na entrega anterior — 25 novos
  cobrindo tudo isso).

### Devolução de item + cálculo automático de atraso

Resolvia a pendência #5 da entrega anterior ("sem devolução de item nem
cálculo de atraso automatizado"):

- **`POST /emprestimos/{id}/devolver`**: o próprio membro marca como
  devolvido um empréstimo que é seu. Devolve a unidade ao estoque
  (`quantidade_disponivel += 1`, com `min()` contra `quantidade_total` como
  defesa extra), grava `data_devolucao_real`. Tentar devolver de novo dá
  400 (`test_nao_pode_devolver_duas_vezes`). Tentar devolver empréstimo de
  outra pessoa dá 404 — não 403, pra não revelar que o ID existe e é de
  outra pessoa (`test_membro_nao_devolve_emprestimo_de_outra_pessoa`).
- **`POST /admin/emprestimos/{id}/devolver`**: o admin confirma a devolução
  de qualquer empréstimo (útil quando o membro esqueceu, perdeu acesso, ou
  entregou o item fisicamente na mão do responsável do laboratório).
  Membro comum toma 403 nessa rota (`test_membro_nao_acessa_devolucao_admin`).
- **Status `ATRASADO` é sempre calculado dinamicamente na leitura, nunca
  gravado no banco** — não existe (nem precisa existir) um job/cron
  rodando periodicamente. O banco só guarda dois estados reais
  (`EM_ANDAMENTO`, `DEVOLVIDO`); toda vez que um empréstimo é consultado
  (`GET /emprestimos/meus/` ou `GET /admin/emprestimos/`), o backend
  compara a data atual com `data_limite_tolerancia` e decide se mostra
  `ATRASADO` ou `EM_ANDAMENTO` na hora. Testado com precisão de segundo
  via `freezegun`: 1 segundo antes do limite ainda é `EM_ANDAMENTO`, 1
  segundo depois já é `ATRASADO`
  (`test_status_atrasado_calculado_dinamicamente`,
  `test_status_nao_fica_atrasado_dentro_do_prazo_de_tolerancia`). Um
  empréstimo atrasado ainda pode ser devolvido normalmente
  (`test_emprestimo_atrasado_ainda_pode_ser_devolvido`).
- **`GET /emprestimos/meus/`** (novo): o membro vê só os próprios
  empréstimos — nunca os de outra pessoa (`test_listar_meus_emprestimos_nao_mostra_de_outra_pessoa`).
- Migração nova (`alembic/versions/..._adicionar_data_devolucao_real.py`)
  adicionando a coluna `data_devolucao_real` (nullable) — testada com
  `alembic upgrade head` de ponta a ponta, incluindo o cenário real
  (empréstimo → estoque desce → devolução → estoque volta → segunda
  devolução bloqueada → admin vê `DEVOLVIDO` no painel).
- **Frontend**: página principal ganhou a seção "Meus empréstimos" (
  `src/components/MeusEmprestimos.tsx`) — lista o que está em aberto com
  botão "Marcar como devolvido", e um histórico recolhível do que já foi
  devolvido. O painel admin (`ListaEmprestimos.tsx`) ganhou uma coluna de
  ação com "Confirmar devolução" para qualquer empréstimo ainda não
  devolvido.
- **31/31 testes passando** (eram 21 na entrega anterior — 10 novos
  cobrindo devolução, isolamento entre usuários e cálculo de atraso).

### Nova funcionalidade: setores, autocadastro de membros e painel admin

Esta era a entrega principal pedida — cadastro de equipamentos, distinção
por setor, autocadastro de membros e painel administrativo. Mudanças de
schema significativas:

- **Setores fixos** (`Setor`): Embarcados, Projetos, Gestão de Pessoas,
  Comercial, Financeiro, Diretoria Executiva — seedados via migração
  Alembic (`alembic/versions/..._seed_setores_fixos.py`), não editáveis
  pela aplicação. `GET /setores/` é pública (sem autenticação) porque o
  formulário de autocadastro precisa dela antes do usuário ter uma sessão.
- **`Usuario` agora carrega `nome_completo` e `setor_id`** — o antigo model
  `Requisitante` (com campo `curso`, que não fazia mais sentido pra setores
  como Comercial/Financeiro) foi removido. Quem pega um item emprestado
  passou a ser o próprio usuário autenticado da sessão, não mais um
  registro separado escolhido num dropdown.
- **`POST /cadastro`** (pública): autocadastro de membro comum. Sempre cria
  `is_admin=False` — mesmo que o corpo da requisição tente forçar
  `is_admin: true`, o schema Pydantic não aceita esse campo nessa rota
  (testado: `test_cadastro_nunca_cria_admin`). Validações: senha forte
  (mín. 8 caracteres, letra + número), username só com caracteres seguros,
  nome completo com nome e sobrenome, setor precisa existir, username
  precisa ser único (checado a nível de banco via constraint, não só na
  aplicação — seguro mesmo sob concorrência).
- **`POST /emprestimos/` não recebe mais `requisitante_id`** — só `item_id`
  e `dias_solicitados`. Quem pegou o item é sempre derivado da sessão
  autenticada (dependency `obter_usuario_atual`), nunca de um campo que o
  cliente poderia manipular para registrar o empréstimo em nome de outra
  pessoa.
- **Limite de dias: mínimo 1, máximo 30, validado nas duas pontas** —
  Pydantic (`Field(ge=1, le=30)`) no backend e Zod (`.min(1).max(30)`) no
  frontend, com a mesma mensagem. Testado explicitamente: 0 dias rejeitado,
  dias negativos rejeitados, 31 dias rejeitado, exatamente 1 e exatamente
  30 aceitos (testes `test_barrar_emprestimo_com_zero_dias`,
  `test_barrar_emprestimo_com_dias_negativo`,
  `test_barrar_emprestimo_acima_do_limite_de_dias`,
  `test_permitir_exatamente_1_dia`, `test_permitir_exatamente_30_dias`).
- **Painel do administrador** — três rotas, todas atrás de `exigir_admin`
  (retornam 403 para qualquer usuário sem `is_admin=True`, testado em
  `test_membro_comum_nao_acessa_rotas_admin` e
  `test_membro_comum_nao_cadastra_administrador`):
  - `POST /admin/itens/`: cadastra um item no catálogo (nome, patrimônio
    opcional, setor, quantidade total). `quantidade_disponivel` nasce igual
    a `quantidade_total`. Patrimônio duplicado é rejeitado (409).
  - `GET /admin/emprestimos/`: lista todos os empréstimos com nome de quem
    pegou, setor e nome do item já resolvidos (o admin não precisa cruzar
    IDs manualmente).
  - `POST /admin/administradores/`: cria um novo administrador. Só existe
    essa rota (protegida) — nunca uma rota pública equivalente, pelo mesmo
    motivo do `scripts/create_admin.py` original: criar admin não pode ser
    algo que qualquer requisição externa consiga disparar.
- **Frontend**: tela de login ganhou uma aba "Cadastrar" (nome completo,
  setor, usuário, senha, confirmar senha — com as mesmas validações do
  backend espelhadas em Zod, pra dar feedback instantâneo sem round-trip).
  Página principal simplificada (só escolhe item + dias, sem mais dropdown
  de requisitante). Painel `/admin` novo, com verificação de acesso via
  `GET /me` — se não for admin, redireciona embora antes de renderizar
  qualquer coisa sensível.
- **21/21 testes passando**, incluindo os novos cenários de cadastro,
  autorização do painel admin e limites de dias.

### Backend (rodadas anteriores)
- Autenticação JWT real (`auth.py`): login com usuário/senha, hash de senha
  com bcrypt, tokens assinados e verificados de verdade. Substitui o
  `verificar_admin` antigo, que só checava se *algum* texto era enviado como
  token — não validava nada.
- **`POST /login` seta um cookie `httpOnly`** em vez de devolver o JWT no
  corpo da resposta — o corpo retorna só os dados do usuário. O JavaScript
  do frontend nunca vê o JWT diretamente.
- CORS configurado via variável de ambiente `ALLOWED_ORIGINS` (testado: libera
  a origem do frontend e bloqueia origens não autorizadas).
- `datetime.utcnow()` (depreciado) trocado por `datetime.now(UTC)` em todo o
  código.
- `SECRET_KEY` obrigatória via ambiente — a aplicação recusa subir sem ela.
- `scripts/create_admin.py`: cria/atualiza um usuário administrador via CLI.
- **Migrações de banco com Alembic configuradas de verdade** — schema
  regenerado do zero nesta rodada para refletir a remoção de
  `Requisitante` e a adição de `nome_completo`/`setor_id` em `Usuario`
  (projeto ainda em fase de desenvolvimento, sem dados reais em produção
  até agora — por isso optei por regenerar a migração inicial em vez de
  encadear uma migração de "rename" complexa).
- `docker-compose.yml`: sobe Postgres real + backend + frontend juntos, já
  com `alembic upgrade head` rodando automaticamente no start do container.

### Frontend (rodadas anteriores)
- Projeto Next.js montado do zero.
- **Sessão via cookie `httpOnly` em vez de `localStorage`** — o JavaScript
  do frontend nunca tem acesso direto ao JWT.
- **Next.js atualizado de 14.2.15 para 16.3.4** — a versão inicial tinha uma
  vulnerabilidade crítica conhecida. `npm audit`: **0 vulnerabilidades**.
- `npm run build` roda limpo, com checagem de TypeScript incluída.

### Deploy
- `Dockerfile` do backend corrigido para não depender do `alembic upgrade
  head` (que não está configurado — ver pendências abaixo).
- `Dockerfile` novo para o frontend (multi-stage, imagem final enxuta).
- `.env.example` (backend) e `.env.local.example` (frontend) — nenhum
  segredo real commitado.

## Como rodar localmente

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edite o .env: gere uma SECRET_KEY com
# python -c "import secrets; print(secrets.token_hex(32))"
# Se for acessar via http://localhost puro (sem HTTPS), defina no .env:
# COOKIE_SECURE=false — senão o navegador recusa o cookie de sessão.
alembic upgrade head
python scripts/create_admin.py admin sua_senha --admin --email seu@email.com
uvicorn main:app --reload
```

### Com Docker Compose (backend + frontend + Postgres real)
```bash
# na raiz do projeto
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
export POSTGRES_PASSWORD=troque-por-uma-senha-forte
docker compose up --build
# em outro terminal, com os containers no ar:
docker compose exec backend python scripts/create_admin.py admin sua_senha --admin --email seu@email.com
```

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
# confirme que NEXT_PUBLIC_API_URL aponta para o backend (ex: http://localhost:8000)
npm run dev
```

Acesse `http://localhost:3000`. O primeiro administrador foi criado via
`create_admin.py` acima — faça login com ele para acessar `/admin` e
cadastrar os itens do catálogo. Membros comuns se cadastram sozinhos pela
aba "Cadastrar" na própria tela de login (não precisam de admin pra isso).

## Pendências reais antes de produção

Fui direto nisso ao longo do trabalho, mas resumindo tudo num lugar só:

1. **Envio real de e-mail não foi testado com um servidor SMTP.** A
   lógica de quando enviar, para quem e com que frequência está testada
   (16 testes, com o envio mockado), e as variáveis estão documentadas no
   `.env.example` — mas nenhum e-mail saiu de verdade, porque isso exige
   credenciais de um provedor SMTP que este ambiente não tem. Configure
   `EMAIL_HABILITADO=true` e as credenciais, e faça um teste real antes de
   confiar nos avisos automáticos.

2. **Sem testes automatizados no frontend.** O backend tem 104 testes,
   todos passando (104 passed, Python 3.12, Windows, PostgreSQL 16 em
   container, dependências de `requirements.txt` com versões travadas;
   verificado em 2026-09-27). Os números anteriores deste README (89, 95)
   ficaram desatualizados. O frontend não tem nenhum teste automatizado ainda.
3. **`docker build` não foi testado.** A suíte, as migrações e o fluxo
   end-to-end foram validados contra Postgres real, mas rodando fora de
   container. A sintaxe do `docker-compose.yml` está validada; rode
   `docker compose up --build` antes de confiar na imagem.

4. **CSRF: mitigado, mas não com token dedicado.** Cookie `SameSite=Lax` +
   CORS restrito à origem do frontend (nunca `*`) já bloqueiam a maioria dos
   ataques CSRF comuns contra APIs chamadas via `fetch`/JSON (navegadores
   exigem preflight nesses casos, e o preflight falha pra origem não
   autorizada). Não implementei um token CSRF dedicado por cima disso — é
   uma camada extra de defesa que vale considerar se o sistema crescer muito
   em criticidade, mas não é uma lacuna aberta como as outras.
5. **Sem interface para autodesativação de conta.** A rota
   `/me/desativar-conta` existe, está testada e protegida, mas o frontend
   ainda não a expõe em lugar nenhum — hoje só dá pra chamá-la pela API.

6. **Sem paginação na lista de itens nem de usuários do painel admin**
   (só a lista de empréstimos foi paginada). Não é urgente com poucos
   itens/usuários, mas escala do mesmo jeito que a lista de empréstimos
   escalaria se não tivesse sido paginada.
7. **`@app.on_event` está depreciado.** O FastAPI avisa em todo boot que
   `on_event("startup"/"shutdown")` deve virar um handler de `lifespan`.
   Funciona normalmente hoje, mas vai quebrar numa versão futura do
   framework — é a única dívida técnica que aparece nos warnings da suíte.

## Automação por QR Code — Avante Almoxarifado

A versão atual adiciona um fluxo de identificação por câmera pensado para
hardware antigo/Linux:

- **ROI fixa:** o backend processa somente a região central configurada em
  `backend/qr_service.py` (20% a partir da esquerda, 15% do topo, 60% da
  largura e 70% da altura).
- **QR Code local:** OpenCV faz a decodificação sem enviar imagens para
  serviços externos.
- **OCR de fallback:** Tesseract pode localizar o patrimônio impresso no
  cartão quando o decoder QR não conseguir concluir a leitura. O OCR não é
  usado como substituto matemático do decoder de QR.
- **Sem armazenamento da imagem:** a captura é processada em memória e
  descartada após a leitura.
- **Campos automáticos:** código/patrimônio, nome, área e setor podem vir do QR.
- **Entrada automática:** o leitor não abre formulário. Se o QR já existe no estoque, soma 1 unidade ao total e ao disponível; se for novo, cadastra 1 unidade usando os dados do próprio QR. O mesmo QR permanece bloqueado enquanto continuar diante da câmera, evitando múltiplas contagens acidentais.
- **Formato recomendado do QR:** JSON com `nome`, `patrimonio`, `codigo_qr`, `area` e `setor_id` (ou `setor_nome`).
- **Campos manuais:** setor, área e quantidade podem ser completados pelo
  responsável antes do cadastro.
- **PostgreSQL:** `codigo_qr` e `area` foram adicionados ao item por migração
  Alembic `8b7e6a1c2d90`.
- **Operações administrativas:** editar, desativar, reativar e remover. A
  remoção física de um item com histórico de empréstimos é bloqueada para
  preservar a auditoria; nesses casos, use desativação.
- **Integração futura/externa:** o endpoint `/qr/scan` retorna o item existente
  quando o código já estiver cadastrado, permitindo que o Avante Almoxarifado
  use o mesmo identificador no seu fluxo.

### Formato recomendado dos cartões

Para testes simples, use como conteúdo do QR:

`AVT-001`

`AVT-002`

`AVT-003`

Também é aceito JSON, por exemplo:

`{"patrimonio":"AVT-001","nome":"Notebook","area":"Laboratório"}`

### Gerar cartões de teste

No backend:

```bash
python scripts/gerar_qrcodes.py --quantidade 20 --saida ../qrcodes
```

### Executar as migrações

```bash
cd backend
alembic upgrade head
```

### Fluxo de teste visual

1. Entrar no painel administrativo.
2. Abrir **Leitor de QR Code**.
3. Permitir acesso à câmera.
4. Posicionar o cartão dentro da ROI branca.
5. Aguardar a identificação.
6. Se o item não existir, completar setor/área/quantidade e cadastrar.
7. Se já existir, conferir patrimônio, estoque e status.
8. Usar o gerenciamento de itens para editar, desativar, reativar ou remover.

Para o computador de baixa potência, a captura do navegador é limitada a
aproximadamente 640×480 e o backend reduz imagens maiores antes do
processamento. O intervalo de leitura automática é de aproximadamente 1
segundo para evitar processamento contínuo desnecessário.

## Melhoria do leitor QR — versão de robustez

O leitor de QR foi reforçado para cartões pequenos e inclinados sem abandonar a ROI fixa. A rotina agora utiliza tentativas graduais de escala, tons de cinza, preservação de módulos com `INTER_NEAREST`, contraste local e rotações de até ±45°.

Também foram adicionados testes automatizados focados em QR normal, QR inclinado, QR pequeno, QR fora da ROI e imagem inválida em `backend/tests/test_qr_service.py`.

Os testes sintéticos realizados nesta versão obtiveram 200/200 leituras em condições normais e leitura de QR de 60–100 px com inclinação de até 45°. QR extremamente pequeno (50 px) ainda pode falhar quando combinado com inclinação forte; isso deve ser validado com a câmera e a distância reais do computador-alvo.
