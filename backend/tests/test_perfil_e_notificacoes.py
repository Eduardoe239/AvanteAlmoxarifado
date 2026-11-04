from datetime import timedelta

from models import Emprestimo, Item, Usuario
from tasks import verificar_e_enviar_alertas_devolucao, _agora_naive_utc


# --- Perfil próprio (PATCH /me) ---

def test_membro_edita_proprio_nome_e_email(client):
    resposta = client.patch(
        "/me", json={"nome_completo": "Membro Atualizado", "email": "novo.membro@example.com"}
    )
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["nome_completo"] == "Membro Atualizado"
    assert dados["email"] == "novo.membro@example.com"


def test_membro_nao_muda_senha_sem_informar_a_atual(client):
    resposta = client.patch("/me", json={"nova_senha": "OutraSenha123"})
    assert resposta.status_code == 400


def test_membro_nao_muda_senha_com_senha_atual_errada(client):
    resposta = client.patch(
        "/me", json={"senha_atual": "SenhaErrada999", "nova_senha": "OutraSenha123"}
    )
    assert resposta.status_code == 401


def test_membro_muda_a_propria_senha(client):
    resposta = client.patch(
        "/me", json={"senha_atual": "SenhaForte123", "nova_senha": "OutraSenha456"}
    )
    assert resposta.status_code == 200

    # a senha nova funciona de verdade no login real (sem mock de auth)
    login = client.post("/login", data={"username": "membro_teste", "password": "OutraSenha456"})
    assert login.status_code == 200


def test_nova_senha_fraca_e_recusada_no_proprio_perfil(client):
    """A política de senha forte vale igual no /me e nas rotas de admin."""
    resposta = client.patch("/me", json={"senha_atual": "SenhaForte123", "nova_senha": "123"})
    assert resposta.status_code == 422


def test_membro_nao_usa_email_de_outra_pessoa(client):
    resposta = client.patch("/me", json={"email": "admin.teste@example.com"})
    assert resposta.status_code == 409


def test_membro_altera_o_proprio_setor(client, db_session):
    from models import Setor

    db_session.add(Setor(id=2, nome="Projetos"))
    db_session.commit()

    resposta = client.patch("/me", json={"setor_id": 2})
    assert resposta.status_code == 200
    assert resposta.json()["setor_id"] == 2


def test_setor_inexistente_e_recusado_no_proprio_perfil(client):
    resposta = client.patch("/me", json={"setor_id": 9999})
    assert resposta.status_code == 400


def test_perfil_nao_permite_trocar_username_nem_virar_admin(client):
    """Campos fora do schema são ignorados — o /me não é caminho de escalada
    de privilégio nem de troca de identidade."""
    resposta = client.patch(
        "/me", json={"username": "outro_nome", "is_admin": True, "nome_completo": "Nome Novo"}
    )
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["username"] == "membro_teste"
    assert dados["is_admin"] is False


# --- Autodesativação de conta ---

def test_membro_desativa_a_propria_conta(client):
    resposta = client.post("/me/desativar-conta", json={"senha": "SenhaForte123"})
    assert resposta.status_code == 204

    # a sessão para de funcionar na requisição seguinte
    assert client.get("/itens/").status_code == 401


def test_autodesativacao_exige_senha_correta(client):
    resposta = client.post("/me/desativar-conta", json={"senha": "SenhaErrada999"})
    assert resposta.status_code == 401


def test_autodesativacao_exige_corpo_com_senha(client):
    resposta = client.post("/me/desativar-conta", json={})
    assert resposta.status_code == 422


def test_ultimo_admin_nao_pode_se_autodesativar(admin_client):
    """
    Proteção contra lockout: as rotas administrativas impedem um admin de
    desativar a si mesmo, mas a rota de autoatendimento existe justamente
    para isso — então precisa barrar explicitamente o último admin ativo,
    senão o sistema ficaria sem ninguém capaz de administrá-lo.
    """
    resposta = admin_client.post("/me/desativar-conta", json={"senha": "SenhaForte123"})
    assert resposta.status_code == 400
    assert "único administrador" in resposta.json()["detail"]


def test_admin_pode_se_autodesativar_havendo_outro_admin(admin_client, db_session):
    from auth import gerar_hash_senha

    db_session.add(
        Usuario(
            username="admin_reserva",
            hashed_password=gerar_hash_senha("SenhaForte123"),
            nome_completo="Admin Reserva",
            email="reserva@example.com",
            is_admin=True,
            ativo=True,
        )
    )
    db_session.commit()

    resposta = admin_client.post("/me/desativar-conta", json={"senha": "SenhaForte123"})
    assert resposta.status_code == 204


# --- Anti-spam do alerta de atraso ---

def _criar_emprestimo_atrasado(db_session, dias_atras: int = 3) -> Emprestimo:
    agora = _agora_naive_utc()
    item = db_session.query(Item).filter(Item.id == 1).first()
    emprestimo = Emprestimo(
        item_id=item.id,
        usuario_id=1,
        quantidade=1,
        data_retirada=agora - timedelta(days=dias_atras + 2),
        dias_solicitados=1,
        data_devolucao_prevista=agora - timedelta(days=dias_atras + 1),
        data_limite_tolerancia=agora - timedelta(days=dias_atras),
        status="EM_ANDAMENTO",
    )
    db_session.add(emprestimo)
    db_session.commit()
    db_session.refresh(emprestimo)
    return emprestimo


def test_alerta_de_atraso_nao_repete_dentro_de_24h(db_session, monkeypatch):
    """
    O scheduler roda de hora em hora. Sem controle de frequência, a mesma
    pessoa receberia 24 e-mails por dia até devolver o item. Este teste
    garante que uma segunda execução logo em seguida não reenvia nada.
    """
    emprestimo = _criar_emprestimo_atrasado(db_session)

    enviados = []

    def _falso_envio(**kwargs):
        enviados.append(kwargs["email_destinatario"])
        return True

    monkeypatch.setattr("tasks.enviar_email_atraso_devolucao", _falso_envio)

    verificar_e_enviar_alertas_devolucao(db_session)
    assert len(enviados) == 1

    # segunda execução do scheduler, minutos depois: não deve reenviar
    verificar_e_enviar_alertas_devolucao(db_session)
    assert len(enviados) == 1

    db_session.refresh(emprestimo)
    assert emprestimo.ultimo_alerta_atraso is not None


def test_alerta_de_atraso_reenvia_apos_24h(db_session, monkeypatch):
    emprestimo = _criar_emprestimo_atrasado(db_session)

    enviados = []

    def _falso_envio(**kwargs):
        enviados.append(kwargs["email_destinatario"])
        return True

    monkeypatch.setattr("tasks.enviar_email_atraso_devolucao", _falso_envio)

    verificar_e_enviar_alertas_devolucao(db_session)
    assert len(enviados) == 1

    # simula a passagem de mais de um dia desde o último alerta
    emprestimo.ultimo_alerta_atraso = _agora_naive_utc() - timedelta(hours=25)
    db_session.commit()

    verificar_e_enviar_alertas_devolucao(db_session)
    assert len(enviados) == 2


def test_falha_de_envio_nao_marca_como_enviado(db_session, monkeypatch):
    """
    Se o SMTP falhar, o alerta precisa ser reprocessado na próxima
    execução — não pode ser silenciosamente perdido.
    """
    emprestimo = _criar_emprestimo_atrasado(db_session)

    monkeypatch.setattr("tasks.enviar_email_atraso_devolucao", lambda **kwargs: False)

    verificar_e_enviar_alertas_devolucao(db_session)

    db_session.refresh(emprestimo)
    assert emprestimo.ultimo_alerta_atraso is None


def test_emprestimo_devolvido_nao_gera_alerta(db_session, monkeypatch):
    emprestimo = _criar_emprestimo_atrasado(db_session)
    emprestimo.status = "DEVOLVIDO"
    emprestimo.data_devolucao_real = _agora_naive_utc()
    db_session.commit()

    enviados = []
    monkeypatch.setattr(
        "tasks.enviar_email_atraso_devolucao",
        lambda **kwargs: enviados.append(kwargs) or True,
    )

    verificar_e_enviar_alertas_devolucao(db_session)
    assert enviados == []
