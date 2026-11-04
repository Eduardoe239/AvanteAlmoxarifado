def test_cadastro_de_membro_com_sucesso(client, db_session):
    payload = {
        "username": "novo.membro",
        "senha": "SenhaForte123",
        "nome_completo": "Novo Membro Teste",
        "email": "novo.membro@example.com",
        "setor_id": 1,
    }
    response = client.post("/cadastro", json=payload)
    assert response.status_code == 201
    dados = response.json()
    assert dados["username"] == "novo.membro"
    assert dados["is_admin"] is False
    # A resposta nunca deve conter a senha nem o hash dela
    assert "senha" not in dados
    assert "hashed_password" not in dados


def test_cadastro_recusa_senha_fraca(client):
    payload = {
        "username": "fraco",
        "senha": "123",
        "nome_completo": "Fulano Fraco",
        "email": "fraco@example.com",
        "setor_id": 1,
    }
    response = client.post("/cadastro", json=payload)
    assert response.status_code == 422


def test_cadastro_recusa_email_invalido(client):
    payload = {
        "username": "email.invalido",
        "senha": "SenhaForte123",
        "nome_completo": "Email Invalido",
        "email": "isso-nao-e-um-email",
        "setor_id": 1,
    }
    response = client.post("/cadastro", json=payload)
    assert response.status_code == 422


def test_cadastro_recusa_setor_inexistente(client):
    payload = {
        "username": "sem.setor",
        "senha": "SenhaForte123",
        "nome_completo": "Sem Setor Valido",
        "email": "sem.setor@example.com",
        "setor_id": 9999,
    }
    response = client.post("/cadastro", json=payload)
    assert response.status_code == 400


def test_cadastro_recusa_username_duplicado(client):
    payload = {
        "username": "membro_teste",  # já existe via fixture (id=1)
        "senha": "SenhaForte123",
        "nome_completo": "Outra Pessoa",
        "email": "outra.pessoa@example.com",
        "setor_id": 1,
    }
    response = client.post("/cadastro", json=payload)
    assert response.status_code == 409


def test_cadastro_recusa_email_duplicado(client):
    payload = {
        "username": "usuario.novo",
        "senha": "SenhaForte123",
        "nome_completo": "Usuario Novo",
        "email": "membro.teste@example.com",  # já existe via fixture (id=1)
        "setor_id": 1,
    }
    response = client.post("/cadastro", json=payload)
    assert response.status_code == 409


def test_cadastro_nunca_cria_admin(client):
    """Mesmo que alguém tente forçar is_admin no corpo da requisição, a
    rota pública de autocadastro ignora esse campo (schema não o aceita)."""
    payload = {
        "username": "tentativa.admin",
        "senha": "SenhaForte123",
        "nome_completo": "Tentativa De Admin",
        "email": "tentativa.admin@example.com",
        "setor_id": 1,
        "is_admin": True,  # campo inexistente no schema, deve ser ignorado
    }
    response = client.post("/cadastro", json=payload)
    assert response.status_code == 201
    assert response.json()["is_admin"] is False


def test_setores_listagem_publica(client):
    response = client.get("/setores/")
    assert response.status_code == 200
    nomes = [s["nome"] for s in response.json()]
    assert "Embarcados" in nomes


# --- Painel do administrador ---

def test_membro_comum_nao_acessa_rotas_admin(client):
    """Um usuário autenticado, mas sem is_admin=True, deve tomar 403."""
    response = client.post(
        "/admin/itens/",
        json={"nome": "Item Teste", "setor_id": 1, "quantidade_total": 3},
    )
    assert response.status_code == 403


def test_admin_cadastra_item(admin_client):
    payload = {
        "nome": "Multímetro Digital",
        "patrimonio": "MULT-042",
        "setor_id": 1,
        "quantidade_total": 4,
    }
    response = admin_client.post("/admin/itens/", json=payload)
    assert response.status_code == 201
    dados = response.json()
    assert dados["nome"] == "Multímetro Digital"
    assert dados["quantidade_disponivel"] == 4  # nasce com disponível = total


def test_admin_nao_cadastra_item_com_patrimonio_duplicado(admin_client):
    payload = {
        "nome": "Placa ESP32 Duplicada",
        "patrimonio": "ESP-001",  # já existe via fixture
        "setor_id": 1,
        "quantidade_total": 2,
    }
    response = admin_client.post("/admin/itens/", json=payload)
    assert response.status_code == 409


def test_admin_visualiza_emprestimos(client, como_admin):
    # membro comum registra um empréstimo
    resposta_emprestimo = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 2})
    assert resposta_emprestimo.status_code == 200

    # troca a identidade ativa para o admin antes da próxima chamada
    como_admin()

    response = client.get("/admin/emprestimos/")
    assert response.status_code == 200
    pagina = response.json()
    assert pagina["total"] == 1
    assert pagina["pagina"] == 1
    assert pagina["total_paginas"] == 1
    emprestimos = pagina["itens"]
    assert len(emprestimos) == 1
    assert emprestimos[0]["usuario_nome"] == "Membro de Teste"
    assert emprestimos[0]["setor_nome"] == "Embarcados"
    assert emprestimos[0]["item_nome"] == "Placa ESP32"


def test_admin_cadastra_novo_administrador(admin_client):
    payload = {
        "username": "novo.admin",
        "senha": "SenhaForte123",
        "nome_completo": "Novo Administrador",
        "email": "novo.admin@example.com",
        "setor_id": 1,
    }
    response = admin_client.post("/admin/administradores/", json=payload)
    assert response.status_code == 201
    assert response.json()["is_admin"] is True


def test_membro_comum_nao_cadastra_administrador(client):
    payload = {
        "username": "tentando.admin",
        "senha": "SenhaForte123",
        "nome_completo": "Tentando Ser Admin",
        "email": "tentando.admin@example.com",
        "setor_id": 1,
    }
    response = client.post("/admin/administradores/", json=payload)
    assert response.status_code == 403
