from freezegun import freeze_time
from models import Item


# Congela o relógio do sistema exatamente nesta data e hora para os testes
@freeze_time("2026-08-31 10:00:00")
def test_calculo_exato_de_dias_de_emprestimo(client):
    """
    Garante que o cálculo de devolução e o +1 dia de tolerância estão precisos.
    """
    payload = {
        "item_id": 1,  # Placa ESP32
        "dias_solicitados": 5,
    }

    response = client.post("/emprestimos/", json=payload)

    assert response.status_code == 200
    dados = response.json()

    # Validações estritas de datas
    assert dados["data_retirada"] == "2026-08-31T10:00:00"
    assert dados["data_devolucao_prevista"] == "2026-09-05T10:00:00"  # + 5 dias exatos
    assert dados["data_limite_tolerancia"] == "2026-09-06T10:00:00"  # + 1 dia de tolerância da regra
    assert dados["status"] == "EM_ANDAMENTO"


def test_barrar_emprestimo_acima_do_limite_de_dias(client):
    """Garante que o Pydantic barra dias_solicitados acima de 30."""
    response = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 35})
    assert response.status_code == 422
    assert "dias_solicitados" in response.text


def test_barrar_emprestimo_com_zero_dias(client):
    """Garante que 0 dias (ou negativo) é rejeitado — mínimo é 1."""
    response = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 0})
    assert response.status_code == 422
    assert "dias_solicitados" in response.text


def test_barrar_emprestimo_com_dias_negativo(client):
    response = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": -5})
    assert response.status_code == 422


def test_permitir_exatamente_30_dias(client):
    """Limite superior é inclusivo: 30 dias deve ser aceito."""
    response = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 30})
    assert response.status_code == 200


def test_permitir_exatamente_1_dia(client):
    """Limite inferior é inclusivo: 1 dia deve ser aceito."""
    response = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 1})
    assert response.status_code == 200


def test_race_condition_estoque_zerado(client):
    """
    Garante que o banco de dados e a transação impedem empréstimo sem estoque.
    """
    # 1º Empréstimo: Pega a última unidade do ESP32 disponível
    client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 1})

    # 2º Empréstimo: Tenta pegar o mesmo item que agora deve ter estoque 0
    response = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 1})

    # O backend deve responder com Bad Request (400) bloqueando a ação.
    # A mensagem informa o disponível vs. o solicitado (comportamento novo,
    # após a introdução de empréstimo por quantidade).
    assert response.status_code == 400
    assert "Disponível: 0" in response.json()["detail"]


def test_emprestimo_vinculado_ao_usuario_autenticado(client):
    """O empréstimo deve ser registrado em nome de quem está logado (id=1
    no client de teste), sem que o cliente possa informar outro usuário."""
    response = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 1})
    assert response.status_code == 200
    # A resposta não expõe usuario_id (schema público), mas o painel admin
    # confirma isso — ver test_admin.py::test_emprestimo_aparece_no_painel_admin.


def test_item_inexistente_retorna_404(client):
    response = client.post("/emprestimos/", json={"item_id": 9999, "dias_solicitados": 1})
    assert response.status_code == 404


# --- Devolução e cálculo de atraso ---

@freeze_time("2026-08-31 10:00:00")
def test_membro_devolve_proprio_emprestimo(client):
    resp_criacao = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 5})
    emprestimo_id = resp_criacao.json()["id"]

    resp_devolucao = client.post(f"/emprestimos/{emprestimo_id}/devolver")
    assert resp_devolucao.status_code == 200
    dados = resp_devolucao.json()
    assert dados["status"] == "DEVOLVIDO"
    assert dados["data_devolucao_real"] == "2026-08-31T10:00:00"


def test_devolucao_libera_estoque(client, db_session):
    # esp32 nasce com quantidade_disponivel=1 (fixture) — pega a última unidade
    resp_criacao = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 5})
    emprestimo_id = resp_criacao.json()["id"]

    item_antes = db_session.query(Item).filter(Item.id == 1).first()
    assert item_antes.quantidade_disponivel == 0

    client.post(f"/emprestimos/{emprestimo_id}/devolver")

    db_session.expire_all()
    item_depois = db_session.query(Item).filter(Item.id == 1).first()
    assert item_depois.quantidade_disponivel == 1


def test_nao_pode_devolver_duas_vezes(client):
    resp_criacao = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 5})
    emprestimo_id = resp_criacao.json()["id"]

    client.post(f"/emprestimos/{emprestimo_id}/devolver")
    segunda_tentativa = client.post(f"/emprestimos/{emprestimo_id}/devolver")

    assert segunda_tentativa.status_code == 400
    assert segunda_tentativa.json()["detail"] == "Este empréstimo já foi devolvido."


def test_membro_nao_devolve_emprestimo_de_outra_pessoa(client, como_admin, como_membro):
    # o admin (usuario id=2) pega um item emprestado
    como_admin()
    resp_criacao = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 5})
    emprestimo_id = resp_criacao.json()["id"]

    # volta pra identidade do membro comum (id=1) e tenta devolver o
    # empréstimo que é do admin
    como_membro()
    resposta = client.post(f"/emprestimos/{emprestimo_id}/devolver")
    assert resposta.status_code == 404  # não revela que o empréstimo existe e é de outra pessoa


def test_admin_forca_devolucao_de_qualquer_emprestimo(client, como_admin):
    resp_criacao = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 5})
    emprestimo_id = resp_criacao.json()["id"]

    como_admin()
    resposta = client.post(f"/admin/emprestimos/{emprestimo_id}/devolver")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "DEVOLVIDO"


def test_membro_nao_acessa_devolucao_admin(client):
    resp_criacao = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 5})
    emprestimo_id = resp_criacao.json()["id"]

    resposta = client.post(f"/admin/emprestimos/{emprestimo_id}/devolver")
    assert resposta.status_code == 403


@freeze_time("2026-08-31 10:00:00")
def test_status_atrasado_calculado_dinamicamente(client, db_session):
    """
    Empresta por 1 dia (tolerância vai até 2026-09-02 10:00). Avança o
    relógio para depois desse limite sem nunca chamar /devolver — o status
    deve virar ATRASADO sozinho, calculado no momento da consulta.
    """
    resp_criacao = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 1})
    emprestimo_id = resp_criacao.json()["id"]
    assert resp_criacao.json()["status"] == "EM_ANDAMENTO"

    with freeze_time("2026-09-03 10:00:01"):  # 1 segundo depois do limite de tolerância
        resposta = client.get("/emprestimos/meus/")
        emprestimo_atualizado = next(e for e in resposta.json() if e["id"] == emprestimo_id)
        assert emprestimo_atualizado["status"] == "ATRASADO"


@freeze_time("2026-08-31 10:00:00")
def test_status_nao_fica_atrasado_dentro_do_prazo_de_tolerancia(client):
    resp_criacao = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 1})
    emprestimo_id = resp_criacao.json()["id"]

    # ainda dentro do prazo de tolerância (+1 dia após devolução prevista)
    with freeze_time("2026-09-02 09:59:00"):
        resposta = client.get("/emprestimos/meus/")
        emprestimo_atualizado = next(e for e in resposta.json() if e["id"] == emprestimo_id)
        assert emprestimo_atualizado["status"] == "EM_ANDAMENTO"


def test_emprestimo_atrasado_ainda_pode_ser_devolvido(client):
    with freeze_time("2026-08-31 10:00:00"):
        resp_criacao = client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 1})
        emprestimo_id = resp_criacao.json()["id"]

    with freeze_time("2026-09-05 10:00:00"):  # bem depois do prazo
        resposta = client.post(f"/emprestimos/{emprestimo_id}/devolver")
        assert resposta.status_code == 200
        assert resposta.json()["status"] == "DEVOLVIDO"


def test_listar_meus_emprestimos_nao_mostra_de_outra_pessoa(client, como_admin, como_membro):
    # o admin (usuario id=2) pega um item emprestado
    como_admin()
    client.post("/emprestimos/", json={"item_id": 1, "dias_solicitados": 5})

    # o membro comum (id=1), que não pegou nada, não deve ver o empréstimo do admin
    como_membro()
    resposta = client.get("/emprestimos/meus/")
    assert resposta.status_code == 200
    assert resposta.json() == []
