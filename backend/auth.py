"""
Módulo central de autenticação.

Responsável por:
- Hash e verificação de senha (bcrypt via passlib)
- Criação e validação de JWT (python-jose)
- Dependência FastAPI que extrai e valida o usuário autenticado

O token é transportado em um cookie httpOnly (não em localStorage/header
Authorization), para que o JavaScript do frontend nunca tenha acesso direto
ao JWT — reduz a superfície de roubo de sessão via XSS.
"""
import os
from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import Usuario

# --- Configuração (lida do ambiente, nunca hardcoded) ---
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Nome do cookie que carrega o JWT.
COOKIE_NAME = "access_token"

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY não definida no ambiente. "
        "Defina uma chave forte na variável de ambiente SECRET_KEY antes de subir a aplicação "
        "(veja .env.example). NUNCA use uma chave padrão em produção."
    )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_plana, senha_hash)


def gerar_hash_senha(senha_plana: str) -> str:
    return pwd_context.hash(senha_plana)


def criar_access_token(dados: dict, expira_em: Optional[timedelta] = None) -> str:
    to_encode = dados.copy()
    expira = datetime.now(UTC) + (expira_em or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expira})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def autenticar_usuario(db: Session, username: str, senha: str) -> Optional[Usuario]:
    usuario = db.query(Usuario).filter(Usuario.username == username).first()
    if not usuario or not usuario.ativo:
        return None
    if not verificar_senha(senha, usuario.hashed_password):
        return None
    return usuario


def criar_usuario(
    db: Session,
    username: str,
    senha: str,
    email: Optional[str] = None,
    nome_completo: Optional[str] = None,
    setor_id: Optional[int] = None,
    is_admin: bool = False,
) -> Usuario:
    """Cria um usuário novo (membro ou admin). Levanta HTTPException 409 se
    o username ou o e-mail já existirem — checagem feita no banco
    (constraint unique em ambos), não só na aplicação, para ser segura
    mesmo sob concorrência."""
    usuario = Usuario(
        username=username,
        hashed_password=gerar_hash_senha(senha),
        email=email,
        nome_completo=nome_completo,
        setor_id=setor_id,
        is_admin=is_admin,
        ativo=True,
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Nome de usuário ou e-mail já em uso."
        )
    db.refresh(usuario)
    return usuario


def _extrair_token_do_cookie(request: Request) -> str:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado.",
        )
    return token


def obter_usuario_atual(
    token: str = Depends(_extrair_token_do_cookie),
    db: Session = Depends(get_db),
) -> Usuario:
    """Decodifica e valida o JWT vindo do cookie. Levanta 401 se o token for
    inválido, expirado ou o usuário não existir mais."""
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais.",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credenciais_invalidas
    except JWTError:
        raise credenciais_invalidas

    usuario = db.query(Usuario).filter(Usuario.username == username).first()
    if usuario is None or not usuario.ativo:
        raise credenciais_invalidas
    return usuario


def exigir_admin(usuario: Usuario = Depends(obter_usuario_atual)) -> Usuario:
    """Dependência para rotas que exigem privilégio de admin."""
    if not usuario.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ação restrita a administradores.",
        )
    return usuario
