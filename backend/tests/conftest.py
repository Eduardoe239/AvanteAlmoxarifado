import pytest
import os
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from models import Item, Setor, Usuario
from auth import obter_usuario_atual, gerar_hash_senha

# PostgreSQL é o único banco suportado. Para testes, usa um banco separado.
# DATABASE_URL_TEST deve estar definida ou será usado um banco de teste padrão
TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL_TEST",
    "postgresql://postgres:postgres@localhost:5432/almoxarifado_test"
)

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _override_para(db_session, usuario_id: int):
    """
    Fábrica do override de `obter_usuario_atual` para um usuário de teste
    específico. Replica fielmente o comportamento da versão real
    (auth.py:obter_usuario_atual) quanto à checagem de conta desativada —
    o override só pula a decodificação do JWT (não faz sentido testar
    decodificação de token aqui), mas a checagem de `ativo` continua real,
    porque é exatamente isso que testes como
    `test_membro_desativado_nao_consegue_mais_usar_a_sessao` precisam
    exercitar de verdade.
    """

    def _override():
        usuario = db_session.query(Usuario).filter(Usuario.id == usuario_id).first()
        if usuario is None or not usuario.ativo:
            raise HTTPException(
                status_code=401, detail="Não foi possível validar as credenciais."
            )
        return usuario

    return _override


def _sincronizar_sequencias(db):
    """
    Alinha as sequências de auto-incremento do Postgres com o maior id já
    presente em cada tabela. Necessário porque a massa de teste é inserida
    com ids explícitos, e no Postgres isso não move a sequência.
    """
    for tabela in ("setores", "usuarios", "itens", "emprestimos"):
        db.execute(
            text(
                f"SELECT setval(pg_get_serial_sequence('{tabela}', 'id'), "
                f"COALESCE((SELECT MAX(id) FROM {tabela}), 1), true)"
            )
        )
    db.commit()


@pytest.fixture(scope="function")
def db_session():
    # Cria as tabelas do zero em cada teste
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Massa de dados inicial (Mock Data)
    setor_embarcados = Setor(id=1, nome="Embarcados")
    usuario_teste = Usuario(
        id=1,
        username="membro_teste",
        hashed_password=gerar_hash_senha("SenhaForte123"),
        nome_completo="Membro de Teste",
        email="membro.teste@example.com",
        setor_id=1,
        is_admin=False,
        ativo=True,
    )
    admin_teste = Usuario(
        id=2,
        username="admin_teste",
        hashed_password=gerar_hash_senha("SenhaForte123"),
        nome_completo="Admin de Teste",
        email="admin.teste@example.com",
        is_admin=True,
        ativo=True,
    )

    esp32 = Item(
        id=1,
        nome="Placa ESP32",
        patrimonio="ESP-001",
        setor_atual_id=1,
        quantidade_total=5,
        quantidade_disponivel=1,
    )

    db.add_all([setor_embarcados, usuario_teste, admin_teste, esp32])
    db.commit()

    # A massa acima é inserida com IDs explícitos (1, 2...), o que NÃO avança
    # as sequências do Postgres (diferente do SQLite, onde o AUTOINCREMENT
    # acompanha o maior id inserido). Sem este ajuste, o primeiro registro
    # criado via API tentaria usar id=1 e colidiria com a massa de teste —
    # aparecendo como um enganoso 409 "já está em uso" em vez do 201 esperado.
    _sincronizar_sequencias(db)

    yield db

    # Limpa o banco após o teste
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Cliente autenticado como membro comum (não-admin) — usuário id=1."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[obter_usuario_atual] = _override_para(db_session, 1)

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_client(db_session):
    """Cliente autenticado como administrador — usuário id=2. Uso isolado
    (testes que só precisam de uma identidade). Para testes que precisam de
    duas identidades em sequência, use `client` + `como_admin`."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[obter_usuario_atual] = _override_para(db_session, 2)
    # exigir_admin não é mockado de propósito: ele internamente depende de
    # obter_usuario_atual (já mockado acima) e checa usuario.is_admin de
    # verdade — isso garante que a lógica real de autorização é exercitada.

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def como_admin(db_session):
    """
    Retorna uma função que troca a identidade autenticada da requisição,
    no mesmo `client` já em uso, para o admin de teste (id=2).
    Necessário porque `app.dependency_overrides` é global (compartilhado
    entre TestClients do mesmo `app`) — não dá pra ter dois clients com
    identidades diferentes "simultaneamente" no mesmo teste, mas dá pra
    trocar a identidade ativa entre chamadas sequenciais (ex: membro pega
    item, depois admin consulta o painel, tudo com o mesmo `client`).
    """

    def _trocar():
        app.dependency_overrides[obter_usuario_atual] = _override_para(db_session, 2)

    return _trocar


@pytest.fixture(scope="function")
def como_membro(db_session):
    """Simétrico a `como_admin`: troca a identidade ativa de volta para o
    membro comum de teste (id=1)."""

    def _trocar():
        app.dependency_overrides[obter_usuario_atual] = _override_para(db_session, 1)

    return _trocar
