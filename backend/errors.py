"""
Padrão de resposta de erro da API (Plano Mestre, seção 27) e request_id
(F1-06).

Formato novo, presente em TODA resposta de erro:

    {
      "detail": ...,                      # legado, INALTERADO
      "error": {
        "code": "NOT_FOUND",
        "message": "Item não encontrado.",
        "request_id": "3f2c...",
        "details": {}
      }
    }

O campo `detail` continua exatamente como o FastAPI o produzia antes: o
frontend atual (frontend/src/lib/api.ts) e os testes existentes dependem
dele, e a seção 26 do plano proíbe quebrar frontend e backend ao mesmo
tempo sem plano de migração. O bloco `error` é ADITIVO. Quando o frontend
migrar para `error.message`/`error.code`, `detail` pode ser removido.

Os códigos, por enquanto, são derivados do status HTTP (genéricos). Códigos
específicos de domínio (ITEM_NOT_FOUND etc.) entram junto com a
reorganização dos handlers; rotas novas já podem usar `AppError`.
"""
import logging
import re
import uuid

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("almoxarifado")

REQUEST_ID_HEADER = "X-Request-ID"
# Só aceita request_id vindo do cliente se for "seguro" (evita injeção em
# logs/headers). Caso contrário, geramos um novo.
_REQUEST_ID_VALIDO = re.compile(r"^[A-Za-z0-9._-]{8,64}$")

_CODIGOS_POR_STATUS = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    413: "PAYLOAD_TOO_LARGE",
    415: "UNSUPPORTED_MEDIA_TYPE",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMITED",
    500: "INTERNAL_ERROR",
    503: "SERVICE_UNAVAILABLE",
}

_MENSAGENS_GENERICAS = {
    400: "Requisição inválida.",
    401: "Não autenticado.",
    403: "Sem permissão para esta ação.",
    404: "Recurso não encontrado.",
    405: "Método não permitido.",
    409: "Conflito com o estado atual do recurso.",
    422: "Dados inválidos.",
    429: "Muitas requisições. Tente novamente mais tarde.",
    500: "Erro interno do servidor.",
    503: "Serviço indisponível no momento.",
}


class AppError(Exception):
    """
    Erro de negócio com código próprio. Para rotas novas:

        raise AppError(404, "ITEM_NOT_FOUND", "Item não encontrado.")

    O `detail` legado recebe a mesma mensagem, então o frontend atual
    continua exibindo o texto normalmente.
    """

    def __init__(self, status_code: int, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


def _codigo_para_status(status_code: int) -> str:
    if status_code in _CODIGOS_POR_STATUS:
        return _CODIGOS_POR_STATUS[status_code]
    return "CLIENT_ERROR" if status_code < 500 else "SERVER_ERROR"


def _request_id_de(request: Request) -> str:
    rid = getattr(request.state, "request_id", None)
    if not rid:
        rid = uuid.uuid4().hex
        request.state.request_id = rid
    return rid


def _resposta(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    detail,
    details: dict | None = None,
    headers: dict | None = None,
) -> JSONResponse:
    rid = _request_id_de(request)
    corpo = {
        "detail": detail,
        "error": {
            "code": code,
            "message": message,
            "request_id": rid,
            "details": details or {},
        },
    }
    h = dict(headers or {})
    h[REQUEST_ID_HEADER] = rid
    return JSONResponse(status_code=status_code, content=corpo, headers=h)


async def _tratar_http_exception(request: Request, exc: StarletteHTTPException):
    # Mesmo comportamento do handler padrão do FastAPI: status que não
    # admitem corpo (1xx, 204, 304) saem sem JSON.
    if exc.status_code < 200 or exc.status_code in (204, 304):
        return Response(
            status_code=exc.status_code,
            headers={**(getattr(exc, "headers", None) or {}),
                     REQUEST_ID_HEADER: _request_id_de(request)},
        )
    detail = exc.detail
    if isinstance(detail, str):
        message = detail
        details = {}
    else:
        message = _MENSAGENS_GENERICAS.get(exc.status_code, "Erro na requisição.")
        details = {"detail": jsonable_encoder(detail)}
    return _resposta(
        request,
        exc.status_code,
        _codigo_para_status(exc.status_code),
        message,
        detail=jsonable_encoder(detail),
        details=details,
        headers=getattr(exc, "headers", None),
    )


async def _tratar_app_error(request: Request, exc: AppError):
    return _resposta(
        request, exc.status_code, exc.code, exc.message,
        detail=exc.message, details=exc.details,
    )


async def _tratar_validacao(request: Request, exc: RequestValidationError):
    erros = jsonable_encoder(exc.errors())
    return _resposta(
        request,
        422,
        "VALIDATION_ERROR",
        _MENSAGENS_GENERICAS[422],
        detail=erros,  # idêntico ao formato antigo do FastAPI
        details={"errors": erros},
    )


async def _tratar_erro_inesperado(request: Request, exc: Exception):
    rid = _request_id_de(request)
    # Nunca vaza stack trace nem mensagem interna para o cliente; o
    # request_id permite achar o traceback nos logs do servidor.
    logger.error(
        "erro_inesperado request_id=%s metodo=%s caminho=%s",
        rid, request.method, request.url.path, exc_info=exc,
    )
    return _resposta(
        request, 500, "INTERNAL_ERROR", _MENSAGENS_GENERICAS[500],
        detail="Erro interno do servidor.",
    )


class RequestIdMiddleware:
    """
    ASGI puro (sem BaseHTTPMiddleware, que interfere em exceções/streaming).
    Define `request.state.request_id` e devolve o header X-Request-ID.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        recebido = None
        for nome, valor in scope.get("headers", []):
            if nome == b"x-request-id":
                recebido = valor.decode("latin-1")
                break
        rid = recebido if recebido and _REQUEST_ID_VALIDO.match(recebido) else uuid.uuid4().hex
        scope.setdefault("state", {})["request_id"] = rid

        async def send_com_header(mensagem):
            if mensagem["type"] == "http.response.start":
                headers = list(mensagem.get("headers", []))
                if not any(n.lower() == b"x-request-id" for n, _ in headers):
                    headers.append((b"x-request-id", rid.encode("latin-1")))
                mensagem = {**mensagem, "headers": headers}
            await send(mensagem)

        await self.app(scope, receive, send_com_header)


def registrar_tratamento_de_erros(app: FastAPI) -> None:
    app.add_middleware(RequestIdMiddleware)
    app.add_exception_handler(StarletteHTTPException, _tratar_http_exception)
    app.add_exception_handler(RequestValidationError, _tratar_validacao)
    app.add_exception_handler(AppError, _tratar_app_error)
    app.add_exception_handler(Exception, _tratar_erro_inesperado)
