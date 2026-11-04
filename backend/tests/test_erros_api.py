"""
Padrão de erro da API (Plano Mestre, seção 27) e X-Request-ID (F1-06).

Dois grupos:
- integração com o app real (fixture `client`, membro comum), garantindo
  que o formato novo é ADITIVO e o `detail` legado segue idêntico;
- app isolado, para cobrir AppError e o erro 500 inesperado sem depender
  de nenhuma rota de negócio.
"""
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from errors import AppError, REQUEST_ID_HEADER, registrar_tratamento_de_erros


# --- Integração com o app real -------------------------------------------

def test_403_mantem_detail_legado_e_adiciona_bloco_error(client):
    resp = client.post(
        "/admin/itens/",
        json={"nome": "Item", "setor_id": 1, "quantidade_total": 3},
    )
    assert resp.status_code == 403
    corpo = resp.json()
    # legado: exatamente a mensagem que o frontend já consome
    assert corpo["detail"] == "Ação restrita a administradores."
    # novo padrão
    erro = corpo["error"]
    assert erro["code"] == "FORBIDDEN"
    assert erro["message"] == "Ação restrita a administradores."
    assert erro["details"] == {}
    assert erro["request_id"]


def test_request_id_do_corpo_e_igual_ao_do_header(client):
    resp = client.post(
        "/admin/itens/",
        json={"nome": "Item", "setor_id": 1, "quantidade_total": 3},
    )
    assert resp.headers[REQUEST_ID_HEADER] == resp.json()["error"]["request_id"]


def test_422_mantem_detail_como_lista_e_expoe_errors_em_details(client):
    resp = client.post("/emprestimos/", json={})  # corpo sem campos obrigatórios
    assert resp.status_code == 422
    corpo = resp.json()
    assert isinstance(corpo["detail"], list) and corpo["detail"]  # formato antigo do FastAPI
    assert "msg" in corpo["detail"][0]
    assert corpo["error"]["code"] == "VALIDATION_ERROR"
    assert corpo["error"]["details"]["errors"] == corpo["detail"]


def test_rota_inexistente_retorna_404_no_novo_formato(client):
    resp = client.get("/rota-que-nao-existe")
    assert resp.status_code == 404
    corpo = resp.json()
    assert corpo["error"]["code"] == "NOT_FOUND"
    assert corpo["detail"] == "Not Found"


def test_sucesso_tambem_devolve_x_request_id(client):
    resp = client.get("/setores/")
    assert resp.status_code == 200
    assert resp.headers[REQUEST_ID_HEADER]


def test_request_id_valido_enviado_pelo_cliente_e_preservado(client):
    resp = client.get("/setores/", headers={REQUEST_ID_HEADER: "meu-id-de-teste-123"})
    assert resp.headers[REQUEST_ID_HEADER] == "meu-id-de-teste-123"


@pytest.mark.parametrize(
    "invalido",
    ["curto", "tem espaco no meio", "x" * 65, "com/barra/e;ponto-e-virgula"],
)
def test_request_id_invalido_do_cliente_e_substituido(client, invalido):
    resp = client.get("/setores/", headers={REQUEST_ID_HEADER: invalido})
    rid = resp.headers[REQUEST_ID_HEADER]
    assert rid != invalido
    assert len(rid) >= 8


def test_request_id_com_byte_nao_ascii_e_substituido(client):
    # httpx só aceita ASCII em header quando o valor é str; bytes permite
    # simular um cliente que manda um byte fora de ASCII (ex.: 0xE7).
    invalido = b"cafe\xe7-invalido-1234"
    resp = client.get("/setores/", headers={REQUEST_ID_HEADER: invalido})
    assert resp.status_code == 200
    rid = resp.headers[REQUEST_ID_HEADER]
    assert rid.isascii() and len(rid) >= 8
    assert rid != invalido.decode("latin-1")


def test_dois_requests_recebem_request_ids_diferentes(client):
    a = client.get("/setores/").headers[REQUEST_ID_HEADER]
    b = client.get("/setores/").headers[REQUEST_ID_HEADER]
    assert a != b


# --- App isolado ----------------------------------------------------------

class _Corpo(BaseModel):
    quantidade: int


def _app_isolado() -> FastAPI:
    app = FastAPI()
    registrar_tratamento_de_erros(app)

    @app.get("/http-str")
    def http_str():
        raise HTTPException(status_code=404, detail="Item não encontrado.")

    @app.get("/http-dict")
    def http_dict():
        raise HTTPException(status_code=409, detail={"campo": "patrimonio"})

    @app.get("/http-headers")
    def http_headers():
        raise HTTPException(
            status_code=401, detail="Não autenticado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.get("/app-error")
    def app_error():
        raise AppError(404, "ITEM_NOT_FOUND", "Item não encontrado.", {"item_id": 7})

    @app.post("/valida")
    def valida(corpo: _Corpo):
        return corpo

    @app.get("/explode")
    def explode():
        raise RuntimeError("segredo-interno: senha=hunter2")

    return app


@pytest.fixture()
def iso():
    # raise_server_exceptions=False: queremos ver a resposta 500 real,
    # não a exceção relançada pelo TestClient.
    return TestClient(_app_isolado(), raise_server_exceptions=False)


def test_http_exception_com_string(iso):
    resp = iso.get("/http-str")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Item não encontrado."
    assert resp.json()["error"]["message"] == "Item não encontrado."
    assert resp.json()["error"]["code"] == "NOT_FOUND"


def test_http_exception_com_detail_nao_string(iso):
    resp = iso.get("/http-dict")
    assert resp.status_code == 409
    corpo = resp.json()
    assert corpo["detail"] == {"campo": "patrimonio"}
    assert corpo["error"]["code"] == "CONFLICT"
    assert corpo["error"]["details"] == {"detail": {"campo": "patrimonio"}}
    assert isinstance(corpo["error"]["message"], str) and corpo["error"]["message"]


def test_headers_da_http_exception_sao_preservados(iso):
    resp = iso.get("/http-headers")
    assert resp.status_code == 401
    assert resp.headers["WWW-Authenticate"] == "Bearer"
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


def test_app_error_usa_codigo_proprio_e_detail_legado(iso):
    resp = iso.get("/app-error")
    assert resp.status_code == 404
    corpo = resp.json()
    assert corpo["error"]["code"] == "ITEM_NOT_FOUND"
    assert corpo["error"]["details"] == {"item_id": 7}
    assert corpo["detail"] == "Item não encontrado."


def test_validacao_pydantic_no_app_isolado(iso):
    resp = iso.post("/valida", json={"quantidade": "abc"})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
    assert resp.json()["error"]["details"]["errors"]


def test_erro_inesperado_devolve_500_generico_sem_vazar_detalhes(iso):
    resp = iso.get("/explode")
    assert resp.status_code == 500
    texto = resp.text
    assert "hunter2" not in texto
    assert "RuntimeError" not in texto
    assert "Traceback" not in texto
    erro = resp.json()["error"]
    assert erro["code"] == "INTERNAL_ERROR"
    assert erro["request_id"]
    assert resp.headers[REQUEST_ID_HEADER] == erro["request_id"]


def test_erro_inesperado_e_registrado_no_log_com_request_id(iso, caplog):
    with caplog.at_level("ERROR", logger="almoxarifado"):
        resp = iso.get("/explode")
    rid = resp.json()["error"]["request_id"]
    assert any(rid in r.getMessage() for r in caplog.records)
