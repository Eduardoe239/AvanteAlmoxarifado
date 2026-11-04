from freezegun import freeze_time


# --- Listagem completa de itens (admin, inclui inativos) ---

def test_admin_lista_itens_incluindo_inativos(client, como_admin):
    como_admin()
    client.post("/admin/itens/1/desativar")
    resposta = client.get("/admin/itens/")
    assert resposta.status_code == 200
    itens = resposta.json()
    item1 = next(i for i in itens if i["id"] == 1)
    assert item1["status"] == "INATIVO"


def test_membro_comum_nao_lista_itens_admin(client):
    resposta = client.get("/admin/itens/")
    assert resposta.status_code == 403


# --- Edição de item ---

def test_admin_edita_nome_e_quantidade_do_item(admin_client):
    resposta = admin_client.patch("/admin/itens/1", json={"nome": "ESP32 Devkit V1", "quantidade_total": 10})
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["nome"] == "ESP32 Devkit V1"
    assert dados["quantidade_total"] == 10
    # fixture: total=5, disponível=1 => 4 unidades já emprestadas.
    # novo total 10 - 4 emprestadas = 6 disponíveis
    assert dados["quantidade_disponivel"] == 6


def test_admin_nao_reduz_quantidade_abaixo_do_emprestado(admin_client):
    # fixture: item 1 tem total=5, disponível=1 (4 unidades já emprestadas)
    resposta = admin_client.patch("/admin/itens/1", json={"quantidade_total": 2})
    assert resposta.status_code == 400


def test_admin_edita_apenas_o_campo_enviado(admin_client):
    resposta = admin_client.patch("/admin/itens/1", json={"nome": "Novo Nome"})
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["nome"] == "Novo Nome"
    assert dados["patrimonio"] == "ESP-001"  # não deveria ter mudado
    assert dados["quantidade_total"] == 5  # não deveria ter mudado


def test_admin_edita_item_recusa_patrimonio_duplicado(admin_client):
    admin_client.post(
        "/admin/itens/",
        json={"nome": "Multímetro", "patrimonio": "MULT-01", "setor_id": 1, "quantidade_total": 2},
    )
    resposta = admin_client.patch("/admin/itens/1", json={"patrimonio": "MULT-01"})
    assert resposta.status_code == 409


def test_admin_edita_item_inexistente_retorna_404(admin_client):
    resposta = admin_client.patch("/admin/itens/9999", json={"nome": "Fantasma"})
    assert resposta.status_code == 404


def test_membro_comum_nao_edita_item(client):
    resposta = client.patch("/admin/itens/1", json={"nome": "Hackeado"})
    assert resposta.status_code == 403


# --- Desativação/reativação de item ---
# Nota: nunca misturar `admin_client` e `client` no mesmo teste — ambos
# compartilham o mesmo `app.dependency_overrides` global, então o segundo
# fixture instanciado sobrescreve a identidade do primeiro silenciosamente.
# Testes que precisam de duas identidades usam sempre `client` + `como_admin`
# (e `como_membro` pra voltar), nunca dois clients "simultâneos".

def test_admin_desativa_item_some_do_catalogo(client, como_admin):
    como_admin()
    resposta = client.post("/admin/itens/1/desativar")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "INATIVO"

    # o item some da listagem (GET /itens/ não tem restrição de papel,
    # continuamos com a mesma identidade admin pra checar)
    catalogo = client.get("/itens/")
    assert all(item["id"] != 1 for item in catalogo.json())


def test_item_desativado_ainda_pode_ser_devolvido(client, como_admin, como_membro):
    # membro pega o item ainda ativo
    resp_emprestimo = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 5})
    emprestimo_id = resp_emprestimo.json()["id"]

    # admin desativa o item (ex: quebrou)
    como_admin()
    resposta_desativar = client.post("/admin/itens/1/desativar")
    assert resposta_desativar.status_code == 200

    # volta pra identidade do membro pra devolver o próprio empréstimo
    como_membro()
    resposta = client.post(f"/emprestimos/{emprestimo_id}/devolver")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "DEVOLVIDO"


def test_admin_reativa_item(client, como_admin):
    como_admin()
    client.post("/admin/itens/1/desativar")
    resposta = client.post("/admin/itens/1/reativar")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "ATIVO"

    catalogo = client.get("/itens/")
    assert any(item["id"] == 1 for item in catalogo.json())


def test_membro_comum_nao_desativa_item(client):
    resposta = client.post("/admin/itens/1/desativar")
    assert resposta.status_code == 403


# --- Gestão de usuários ---

def test_admin_lista_usuarios(admin_client):
    resposta = admin_client.get("/admin/usuarios/")
    assert resposta.status_code == 200
    usuarios = resposta.json()
    usernames = [u["username"] for u in usuarios]
    assert "membro_teste" in usernames
    assert "admin_teste" in usernames
    membro = next(u for u in usuarios if u["username"] == "membro_teste")
    assert membro["setor_nome"] == "Embarcados"
    assert membro["ativo"] is True


def test_membro_comum_nao_lista_usuarios(client):
    resposta = client.get("/admin/usuarios/")
    assert resposta.status_code == 403


def test_admin_desativa_membro(admin_client):
    resposta = admin_client.post("/admin/usuarios/1/desativar")
    assert resposta.status_code == 200
    assert resposta.json()["ativo"] is False


def test_membro_desativado_nao_consegue_mais_usar_a_sessao(client, como_admin, como_membro):
    """
    O membro (identidade padrão de `client`, id=1) é desativado pelo admin
    no meio do teste — a PRÓXIMA requisição feita com a identidade dele
    (mesmo sem ter "deslogado") deve ser recusada, porque
    `obter_usuario_atual` recarrega o usuário do banco a cada chamada e
    checa `ativo` toda vez, nunca confiando em um estado cacheado.
    """
    como_admin()
    resposta_desativar = client.post("/admin/usuarios/1/desativar")
    assert resposta_desativar.status_code == 200

    como_membro()
    resposta = client.get("/itens/")
    assert resposta.status_code == 401


def test_admin_nao_desativa_a_propria_conta(admin_client):
    resposta = admin_client.post("/admin/usuarios/2/desativar")  # admin_teste tem id=2
    assert resposta.status_code == 400


def test_admin_reativa_membro(admin_client):
    admin_client.post("/admin/usuarios/1/desativar")
    resposta = admin_client.post("/admin/usuarios/1/reativar")
    assert resposta.status_code == 200
    assert resposta.json()["ativo"] is True


def test_membro_comum_nao_desativa_usuario(client):
    resposta = client.post("/admin/usuarios/2/desativar")
    assert resposta.status_code == 403


def test_desativar_usuario_inexistente_retorna_404(admin_client):
    resposta = admin_client.post("/admin/usuarios/9999/desativar")
    assert resposta.status_code == 404


# --- Edição de usuário ---

def test_admin_edita_nome_e_email_do_membro(admin_client):
    resposta = admin_client.patch(
        "/admin/usuarios/1", json={"nome_completo": "Membro Renomeado", "email": "renomeado@example.com"}
    )
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["nome_completo"] == "Membro Renomeado"
    assert dados["email"] == "renomeado@example.com"
    assert dados["username"] == "membro_teste"  # não deveria ter mudado


def test_admin_edita_apenas_o_campo_de_usuario_enviado(admin_client):
    resposta = admin_client.patch("/admin/usuarios/1", json={"nome_completo": "Só o Nome Mudou"})
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["nome_completo"] == "Só o Nome Mudou"
    assert dados["email"] == "membro.teste@example.com"  # preservado


def test_admin_completa_email_de_conta_antiga_sem_email(admin_client, db_session):
    """Simula uma conta criada antes do e-mail existir/ser obrigatório
    (ex: via scripts/create_admin.py sem --email) — o admin completa
    depois pelo painel."""
    from models import Usuario

    conta_antiga = Usuario(
        id=99,
        username="conta.antiga",
        hashed_password="hash-qualquer",
        nome_completo="Conta Antiga",
        email=None,
        is_admin=True,
        ativo=True,
    )
    db_session.add(conta_antiga)
    db_session.commit()

    resposta = admin_client.patch("/admin/usuarios/99", json={"email": "conta.antiga@example.com"})
    assert resposta.status_code == 200
    assert resposta.json()["email"] == "conta.antiga@example.com"


def test_admin_edita_recusa_username_duplicado(admin_client):
    resposta = admin_client.patch("/admin/usuarios/1", json={"username": "admin_teste"})
    assert resposta.status_code == 409


def test_admin_edita_recusa_email_duplicado(admin_client):
    resposta = admin_client.patch("/admin/usuarios/1", json={"email": "admin.teste@example.com"})
    assert resposta.status_code == 409


def test_admin_edita_recusa_setor_inexistente(admin_client):
    resposta = admin_client.patch("/admin/usuarios/1", json={"setor_id": 9999})
    assert resposta.status_code == 400


def test_admin_reseta_senha_do_membro(client, como_admin, como_membro):
    como_admin()
    resposta = client.patch("/admin/usuarios/1", json={"nova_senha": "NovaSenhaForte456"})
    assert resposta.status_code == 200

    # a nova senha funciona pra logar de verdade (sem mock de auth) — usa o
    # endpoint real /login, que não depende de override de identidade
    como_membro()
    login_resp = client.post(
        "/login", data={"username": "membro_teste", "password": "NovaSenhaForte456"}
    )
    assert login_resp.status_code == 200


def test_admin_edita_item_inexistente_retorna_404_usuario(admin_client):
    resposta = admin_client.patch("/admin/usuarios/9999", json={"nome_completo": "Fantasma Fantasma"})
    assert resposta.status_code == 404


def test_admin_pode_editar_a_propria_conta(admin_client):
    resposta = admin_client.patch("/admin/usuarios/2", json={"nome_completo": "Admin Renomeado"})
    assert resposta.status_code == 200
    assert resposta.json()["nome_completo"] == "Admin Renomeado"


def test_membro_comum_nao_edita_usuario(client):
    resposta = client.patch("/admin/usuarios/2", json={"nome_completo": "Hackeado"})
    assert resposta.status_code == 403


# --- Exclusão de usuário ---

def test_admin_exclui_membro(admin_client):
    resposta = admin_client.delete("/admin/usuarios/1")
    assert resposta.status_code == 204

    # o usuário realmente sumiu — listagem não mostra mais
    usuarios = admin_client.get("/admin/usuarios/").json()
    assert all(u["id"] != 1 for u in usuarios)


def test_excluir_usuario_preserva_historico_de_emprestimo(client, como_admin):
    """
    Ponto crítico: excluir um usuário NÃO pode apagar o histórico de
    empréstimos dele — só a referência à pessoa vira NULL (ON DELETE SET
    NULL), e o painel admin mostra "(usuário removido)" no lugar do nome.
    Perder esse histórico seria inaceitável num sistema de controle de
    patrimônio.
    """
    resp_emprestimo = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 3})
    assert resp_emprestimo.status_code == 200
    emprestimo_id = resp_emprestimo.json()["id"]

    como_admin()
    resposta_exclusao = client.delete("/admin/usuarios/1")
    assert resposta_exclusao.status_code == 204

    pagina = client.get("/admin/emprestimos/").json()
    emprestimo = next(e for e in pagina["itens"] if e["id"] == emprestimo_id)
    assert emprestimo["usuario_nome"] == "(usuário removido)"
    assert emprestimo["usuario_id"] is None
    # o resto do histórico continua intacto
    assert emprestimo["item_nome"] == "Placa ESP32"
    assert emprestimo["dias_solicitados"] == 3


def test_admin_nao_exclui_a_propria_conta(admin_client):
    resposta = admin_client.delete("/admin/usuarios/2")
    assert resposta.status_code == 400


def test_excluir_usuario_inexistente_retorna_404(admin_client):
    resposta = admin_client.delete("/admin/usuarios/9999")
    assert resposta.status_code == 404


def test_membro_comum_nao_exclui_usuario(client):
    resposta = client.delete("/admin/usuarios/2")
    assert resposta.status_code == 403


# --- Paginação ---

def test_paginacao_de_emprestimos(client, como_admin):
    como_admin()
    # aumenta o estoque do item pra caber vários empréstimos ao mesmo tempo
    client.patch("/admin/itens/1", json={"quantidade_total": 20})

    for _ in range(5):
        resp = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 1})
        assert resp.status_code == 200

    resposta = client.get("/admin/emprestimos/?pagina=1&tamanho_pagina=2")
    assert resposta.status_code == 200
    pagina = resposta.json()
    assert pagina["total"] == 5
    assert pagina["tamanho_pagina"] == 2
    assert pagina["total_paginas"] == 3
    assert len(pagina["itens"]) == 2


def test_paginacao_pagina_vazia_alem_do_total(client, como_admin):
    como_admin()
    client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 1})
    resposta = client.get("/admin/emprestimos/?pagina=99&tamanho_pagina=10")
    assert resposta.status_code == 200
    assert resposta.json()["itens"] == []


# --- Resumo de atrasados (notificação proativa do admin) ---

def test_resumo_atrasados_vazio_quando_nada_atrasado(client, como_admin):
    client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 5})
    como_admin()
    resposta = client.get("/admin/emprestimos/atrasados/resumo")
    assert resposta.status_code == 200
    assert resposta.json()["total_atrasados"] == 0


def test_resumo_atrasados_detecta_emprestimo_vencido(client, como_admin):
    with freeze_time("2026-08-31 10:00:00"):
        client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 1})

    with freeze_time("2026-09-05 10:00:00"):
        como_admin()
        resposta = client.get("/admin/emprestimos/atrasados/resumo")
        assert resposta.status_code == 200
        dados = resposta.json()
        assert dados["total_atrasados"] == 1
        assert dados["itens"][0]["status"] == "ATRASADO"


def test_membro_comum_nao_acessa_resumo_atrasados(client):
    resposta = client.get("/admin/emprestimos/atrasados/resumo")
    assert resposta.status_code == 403


# --- Setor de administradores ---

def test_admin_criado_fica_vinculado_ao_setor(admin_client):
    payload = {
        "username": "admin.setor",
        "senha": "SenhaForte123",
        "nome_completo": "Admin Com Setor",
        "email": "admin.setor@example.com",
        "setor_id": 1,
    }
    resposta = admin_client.post("/admin/administradores/", json=payload)
    assert resposta.status_code == 201
    assert resposta.json()["setor_id"] == 1

    # e o setor aparece resolvido na listagem do painel
    usuarios = admin_client.get("/admin/usuarios/").json()
    criado = next(u for u in usuarios if u["username"] == "admin.setor")
    assert criado["setor_nome"] == "Embarcados"
    assert criado["is_admin"] is True


def test_cadastro_de_admin_exige_setor(admin_client):
    payload = {
        "username": "admin.sem.setor",
        "senha": "SenhaForte123",
        "nome_completo": "Admin Sem Setor",
        "email": "admin.sem.setor@example.com",
    }
    resposta = admin_client.post("/admin/administradores/", json=payload)
    assert resposta.status_code == 422


def test_cadastro_de_admin_recusa_setor_inexistente(admin_client):
    payload = {
        "username": "admin.setor.ruim",
        "senha": "SenhaForte123",
        "nome_completo": "Admin Setor Ruim",
        "email": "admin.setor.ruim@example.com",
        "setor_id": 9999,
    }
    resposta = admin_client.post("/admin/administradores/", json=payload)
    assert resposta.status_code == 400


def test_admin_edita_setor_de_outro_admin(admin_client, db_session):
    """O setor de um administrador é editável como o de qualquer usuário."""
    from models import Setor

    db_session.add(Setor(id=3, nome="Comercial"))
    db_session.commit()

    # admin_teste (id=2) foi criado sem setor na fixture
    resposta = admin_client.patch("/admin/usuarios/2", json={"setor_id": 3})
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["setor_id"] == 3
    assert dados["setor_nome"] == "Comercial"
    assert dados["is_admin"] is True
