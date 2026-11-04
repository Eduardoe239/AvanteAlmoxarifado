import re

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime


# --- Setor ---

class SetorResponse(BaseModel):
    id: int
    nome: str

    model_config = ConfigDict(from_attributes=True)


# --- Usuário / Autenticação ---

class UsuarioResponse(BaseModel):
    id: int
    username: str
    nome_completo: str | None = None
    email: str | None = None
    setor_id: int | None = None
    is_admin: bool
    foto_perfil: str | None = None

    model_config = ConfigDict(from_attributes=True)


def _validar_senha_forte(senha: str) -> str:
    if len(senha) < 8:
        raise ValueError("A senha deve ter pelo menos 8 caracteres.")
    if not re.search(r"[A-Za-z]", senha):
        raise ValueError("A senha deve conter pelo menos uma letra.")
    if not re.search(r"[0-9]", senha):
        raise ValueError("A senha deve conter pelo menos um número.")
    return senha


def _validar_nome_completo(nome: str) -> str:
    nome = nome.strip()
    if len(nome.split()) < 2:
        raise ValueError("Informe nome e sobrenome.")
    return nome


def _validar_username_formato(username: str) -> str:
    username = username.strip()
    if not re.fullmatch(r"[a-zA-Z0-9._-]+", username):
        raise ValueError(
            "O usuário deve conter apenas letras, números, ponto, hífen ou underscore."
        )
    return username


class UsuarioCadastro(BaseModel):
    """
    Autocadastro de membro comum (não-admin) na tela de login. `email` é
    obrigatório a partir desta versão — preparação para a notificação por
    e-mail que será implementada futuramente (ver ResumoAtrasados e o
    changelog do README). O nome de usuário precisa ser único; o nome
    completo NÃO precisa (várias pessoas podem se chamar igual — é o
    username que identifica a conta de forma única).
    """
    username: str = Field(..., min_length=3, max_length=100)
    senha: str
    nome_completo: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    setor_id: int = Field(..., gt=0)

    @field_validator("username")
    @classmethod
    def validar_username(cls, v: str) -> str:
        return _validar_username_formato(v)

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, v: str) -> str:
        return _validar_senha_forte(v)

    @field_validator("nome_completo")
    @classmethod
    def validar_nome_completo(cls, v: str) -> str:
        return _validar_nome_completo(v)


class AdminCadastro(BaseModel):
    """Criação de um novo administrador, feita por um administrador já
    autenticado, através do painel — nunca via endpoint público. `email`
    também obrigatório aqui pelo mesmo motivo do UsuarioCadastro, e
    `setor_id` para que o admin apareça vinculado a um setor como qualquer
    outra pessoa da organização."""
    username: str = Field(..., min_length=3, max_length=100)
    senha: str
    nome_completo: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    setor_id: int = Field(..., gt=0)

    @field_validator("username")
    @classmethod
    def validar_username(cls, v: str) -> str:
        return _validar_username_formato(v)

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, v: str) -> str:
        return _validar_senha_forte(v)

    @field_validator("nome_completo")
    @classmethod
    def validar_nome_completo(cls, v: str) -> str:
        return _validar_nome_completo(v)


# --- Item ---

class ItemResponse(BaseModel):
    id: int
    nome: str
    patrimonio: str | None = None
    codigo_qr: str | None = None
    area: str | None = None
    setor_atual_id: int | None = None
    quantidade_total: int
    quantidade_disponivel: int
    status: str

    model_config = ConfigDict(from_attributes=True)


class ItemCreate(BaseModel):
    """Cadastro de item no catálogo, feito por um administrador."""
    nome: str = Field(..., min_length=2, max_length=150)
    patrimonio: str | None = Field(None, max_length=50)
    codigo_qr: str | None = Field(None, max_length=120)
    area: str | None = Field(None, max_length=120)
    setor_id: int = Field(..., gt=0)
    quantidade_total: int = Field(..., gt=0, le=100000)

    @field_validator("nome", "patrimonio")
    @classmethod
    def strip_texto(cls, v: str | None) -> str | None:
        return v.strip() if v else v


class ItemUpdate(BaseModel):
    """
    Edição de um item já cadastrado. Todos os campos são opcionais — o
    admin só envia o que quer mudar (PATCH parcial, não PUT com
    substituição total). `quantidade_total` é validado no endpoint contra
    a quantidade atualmente emprestada (não pode reduzir abaixo do que já
    está com alguém).
    """
    nome: str | None = Field(None, min_length=2, max_length=150)
    patrimonio: str | None = Field(None, max_length=50)
    codigo_qr: str | None = Field(None, max_length=120)
    area: str | None = Field(None, max_length=120)
    setor_id: int | None = Field(None, gt=0)
    quantidade_total: int | None = Field(None, gt=0, le=100000)

    @field_validator("nome", "patrimonio")
    @classmethod
    def strip_texto(cls, v: str | None) -> str | None:
        return v.strip() if v else v


class QRScanResponse(BaseModel):
    sucesso: bool
    mensagem: str
    raw: str | None = None
    patrimonio: str | None = None
    codigo_qr: str | None = None
    nome: str | None = None
    area: str | None = None
    setor_id: int | None = None
    setor_nome: str | None = None
    item: ItemResponse | None = None
    acao: str | None = None
    roi: dict[str, int | str] | None = None
    metodo: str | None = None


# --- Usuário (visão do admin) ---

class UsuarioAdminResponse(BaseModel):
    """Visão enriquecida de um usuário para o painel admin — inclui nome
    do setor já resolvido e o campo `ativo`, que não é exposto em
    UsuarioResponse (irrelevante pra o próprio usuário, que só está
    autenticado se `ativo=True`)."""
    id: int
    username: str
    nome_completo: str | None = None
    email: str | None = None
    setor_id: int | None = None
    setor_nome: str | None = None
    is_admin: bool
    ativo: bool

    model_config = ConfigDict(from_attributes=True)


class UsuarioUpdate(BaseModel):
    """
    Edição de um usuário (membro ou admin) feita por um administrador.
    Todos os campos são opcionais — PATCH parcial, o admin só envia o que
    quer mudar. `nova_senha`, quando enviada, reseta a senha do usuário
    (útil pra quando alguém esquece a senha e não tem como recuperar
    sozinho). `setor_id` só faz sentido pra membros (admins não têm setor),
    mas o schema não impõe essa regra — o admin decide.
    """
    username: str | None = Field(None, min_length=3, max_length=100)
    nome_completo: str | None = Field(None, min_length=3, max_length=150)
    email: EmailStr | None = None
    setor_id: int | None = Field(None, gt=0)
    nova_senha: str | None = None

    @field_validator("username")
    @classmethod
    def validar_username(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _validar_username_formato(v)

    @field_validator("nome_completo")
    @classmethod
    def validar_nome_completo(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _validar_nome_completo(v)

    @field_validator("nova_senha")
    @classmethod
    def validar_nova_senha(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _validar_senha_forte(v)


class MeuPerfilUpdate(BaseModel):
    """
    Atualização do próprio perfil de usuário. Um usuário pode mudar:
    - nome_completo
    - email
    - setor_id
    - senha

    Continua sem poder mudar o próprio `username` (é a identidade da conta,
    trocá-la à revelia confunde o histórico visto pelo admin) nem o próprio
    `is_admin` — escalada de privilégio nunca parte do autoatendimento.
    Todos os campos são opcionais — PATCH parcial.
    """
    nome_completo: str | None = Field(None, min_length=3, max_length=150)
    email: EmailStr | None = None
    setor_id: int | None = Field(None, gt=0)
    senha_atual: str | None = Field(None, description="Obrigatória ao mudar senha")
    nova_senha: str | None = None

    @field_validator("nome_completo")
    @classmethod
    def validar_nome_completo(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _validar_nome_completo(v)

    @field_validator("nova_senha")
    @classmethod
    def validar_nova_senha(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _validar_senha_forte(v)


class ConfirmacaoSenha(BaseModel):
    """
    Corpo de confirmação para ações sensíveis sobre a própria conta
    (ex: autodesativação). Schema explícito em vez de `dict` cru, para que
    a validação e a documentação automática do FastAPI funcionem.
    """
    senha: str = Field(..., min_length=1)


# (paginação da lista de empréstimos: ver PaginaEmprestimosAdmin no final
# deste arquivo, definida após EmprestimoAdminResponse existir)


# --- Empréstimo ---

class EmprestimoCreate(BaseModel):
    """
    O membro informa o item, quantidade e os dias — quem está pegando o
    item é sempre o usuário autenticado da sessão, nunca um campo enviado
    pelo cliente (evita registrar empréstimo em nome de outra pessoa).
    """
    item_id: int = Field(..., gt=0)
    quantidade: int = Field(
        default=1,
        ge=1,
        le=100,
        description="Quantidade do item a emprestar (máximo 100).",
    )
    dias_solicitados: int = Field(
        ...,
        ge=1,
        le=30,
        description="Mínimo 1 dia, máximo 30 dias.",
    )


class EmprestimoResponse(BaseModel):
    """
    Visão do próprio membro sobre um empréstimo seu. `status` aqui é sempre
    o status de EXIBIÇÃO calculado no momento da resposta (ver
    main.py:_status_exibicao) — "ATRASADO" nunca fica gravado no banco (não
    há job periódico), é sempre recalculado comparando a data atual com
    `data_limite_tolerancia` toda vez que a rota é chamada.
    """
    id: int
    item_id: int
    item_nome: str
    quantidade: int
    dias_solicitados: int
    data_retirada: datetime
    data_devolucao_prevista: datetime
    data_limite_tolerancia: datetime
    data_devolucao_real: datetime | None = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class EmprestimoAdminResponse(BaseModel):
    """Visão enriquecida usada no painel do administrador — mostra quem
    pegou o quê, sem o admin precisar cruzar IDs manualmente. `status`
    segue a mesma regra de cálculo do EmprestimoResponse (ver acima)."""
    id: int
    item_id: int
    item_nome: str
    usuario_id: int | None = None
    usuario_nome: str
    setor_nome: str | None = None
    quantidade: int
    dias_solicitados: int
    data_retirada: datetime
    data_devolucao_prevista: datetime
    data_limite_tolerancia: datetime
    data_devolucao_real: datetime | None = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class PaginaEmprestimosAdmin(BaseModel):
    """Envelope de paginação para a lista de empréstimos do painel admin."""
    itens: list[EmprestimoAdminResponse]
    total: int
    pagina: int
    tamanho_pagina: int
    total_paginas: int


class ResumoAtrasados(BaseModel):
    """Resumo de empréstimos atrasados no momento — usado para o banner de
    notificação proativa no painel do administrador. Sempre calculado a
    partir do estado real do banco (mesma regra de EmprestimoAdminResponse),
    nunca de um campo armazenado."""
    total_atrasados: int
    itens: list[EmprestimoAdminResponse]
