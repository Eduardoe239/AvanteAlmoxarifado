import math
import os
import json
import re
import base64
import io
from html import escape
import fitz
from datetime import datetime, timedelta, UTC

from fastapi import FastAPI, Depends, HTTPException, Query, Response, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi.responses import Response as RawResponse
from email_service import enviar_email_novo_item

from database import get_db, SessionLocal
from errors import registrar_tratamento_de_erros
from models import Item, Emprestimo, Setor, Usuario, NotaFiscal, MensagemContato
from schemas import (
    EmprestimoCreate,
    EmprestimoResponse,
    EmprestimoAdminResponse,
    PaginaEmprestimosAdmin,
    ResumoAtrasados,
    UsuarioResponse,
    UsuarioCadastro,
    UsuarioAdminResponse,
    UsuarioUpdate,
    MeuPerfilUpdate,
    ConfirmacaoSenha,
    AdminCadastro,
    ItemResponse,
    ItemCreate,
    ItemUpdate,
    SetorResponse,
    QRScanResponse,
)
from qr_service import decode_qr_from_bytes

from auth import (
    autenticar_usuario,
    criar_access_token,
    criar_usuario,
    gerar_hash_senha,
    obter_usuario_atual,
    exigir_admin,
    COOKIE_NAME,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

# O schema do banco agora é gerido por migrações Alembic (pasta alembic/),
# não mais por create_all() automático no startup. Rode `alembic upgrade head`
# antes de subir a aplicação (o Dockerfile e start.sh já fazem isso).

app = FastAPI(title="Sistema Almoxarifado API")

# --- CORS ---
# Em produção, defina ALLOWED_ORIGINS no ambiente como uma lista separada por vírgula
# de domínios do frontend (ex: "https://lab.suaorg.com"). Nunca use "*" com credenciais
# habilitadas em produção.
origens_permitidas = [
    origem.strip()
    for origem in os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if origem.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origens_permitidas,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)
# Padrão de erro (seção 27 do Plano Mestre) + X-Request-ID; ver errors.py.
# Fica depois do CORS para ser o middleware mais externo (o último
# adicionado é o primeiro a ver a requisição).
registrar_tratamento_de_erros(app)

# Em produção (HTTPS) o cookie deve ter Secure=True, o que faz o navegador só
# enviá-lo por conexões HTTPS. Em desenvolvimento local (HTTP puro) isso
# impediria o cookie de ser aceito, então permitimos desligar via ambiente.
# Nunca defina COOKIE_SECURE=false em produção.
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "true").lower() == "true"


def _definir_cookie_sessao(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


def _validar_setor(db: Session, setor_id: int) -> None:
    if not db.query(Setor).filter(Setor.id == setor_id).first():
        raise HTTPException(status_code=400, detail="Setor inválido.")


def _agora_naive_utc() -> datetime:
    """
    Datetime atual em UTC, sem tzinfo. Mantém tudo consistente em UTC naive,
    tanto na escrita quanto na leitura do banco de dados.
    """
    return datetime.now(UTC).replace(tzinfo=None)


def _status_exibicao(emprestimo: Emprestimo) -> str:
    """
    Calcula o status para EXIBIÇÃO no momento da resposta. "ATRASADO" nunca
    é gravado no banco — não há job periódico rodando para isso — é sempre
    recalculado comparando a data atual com `data_limite_tolerancia`. O
    banco guarda EM_ANDAMENTO, PENDENTE_DEVOLUCAO e DEVOLVIDO.
    """
    if emprestimo.status == "DEVOLVIDO":
        return "DEVOLVIDO"
    if emprestimo.status == "PENDENTE_DEVOLUCAO":
        return "PENDENTE_DEVOLUCAO"
    if _agora_naive_utc() > emprestimo.data_limite_tolerancia:
        return "ATRASADO"
    return "EM_ANDAMENTO"


def _construir_resposta_emprestimo(emprestimo: Emprestimo) -> EmprestimoResponse:
    return EmprestimoResponse(
        id=emprestimo.id,
        item_id=emprestimo.item_id,
        item_nome=emprestimo.item.nome if emprestimo.item else "(item removido)",
        quantidade=emprestimo.quantidade,
        dias_solicitados=emprestimo.dias_solicitados,
        data_retirada=emprestimo.data_retirada,
        data_devolucao_prevista=emprestimo.data_devolucao_prevista,
        data_limite_tolerancia=emprestimo.data_limite_tolerancia,
        data_devolucao_real=emprestimo.data_devolucao_real,
        status=_status_exibicao(emprestimo),
    )


def _construir_resposta_emprestimo_admin(emprestimo: Emprestimo) -> EmprestimoAdminResponse:
    return EmprestimoAdminResponse(
        id=emprestimo.id,
        item_id=emprestimo.item_id,
        item_nome=emprestimo.item.nome if emprestimo.item else "(item removido)",
        usuario_id=emprestimo.usuario_id,
        usuario_nome=(
            (emprestimo.usuario.nome_completo or emprestimo.usuario.username)
            if emprestimo.usuario
            else "(usuário removido)"
        ),
        setor_nome=(
            emprestimo.usuario.setor.nome if emprestimo.usuario and emprestimo.usuario.setor else None
        ),
        quantidade=emprestimo.quantidade,
        dias_solicitados=emprestimo.dias_solicitados,
        data_retirada=emprestimo.data_retirada,
        data_devolucao_prevista=emprestimo.data_devolucao_prevista,
        data_limite_tolerancia=emprestimo.data_limite_tolerancia,
        data_devolucao_real=emprestimo.data_devolucao_real,
        status=_status_exibicao(emprestimo),
    )


def _construir_resposta_usuario_admin(usuario: Usuario) -> UsuarioAdminResponse:
    return UsuarioAdminResponse(
        id=usuario.id,
        username=usuario.username,
        nome_completo=usuario.nome_completo,
        email=usuario.email,
        setor_id=usuario.setor_id,
        setor_nome=usuario.setor.nome if usuario.setor else None,
        is_admin=usuario.is_admin,
        ativo=usuario.ativo,
    )


def _processar_devolucao(db: Session, emprestimo: Emprestimo) -> Emprestimo:
    """Lógica compartilhada entre a devolução feita pelo próprio membro e a
    devolução forçada pelo admin: marca como devolvido e devolve as unidades
    ao estoque disponível."""
    if emprestimo.status == "DEVOLVIDO":
        raise HTTPException(status_code=400, detail="Este empréstimo já foi devolvido.")

    item = db.query(Item).with_for_update().filter(Item.id == emprestimo.item_id).first()
    if item:
        # Devolver a quantidade emprestada
        # min() é uma defesa contra o estoque "disponível" ultrapassar o
        # "total" por alguma inconsistência anterior de dados.
        item.quantidade_disponivel = min(
            item.quantidade_disponivel + emprestimo.quantidade,
            item.quantidade_total,
        )

    emprestimo.status = "DEVOLVIDO"
    emprestimo.data_devolucao_real = _agora_naive_utc()

    db.commit()
    db.refresh(emprestimo)
    return emprestimo


# --- Autenticação ---

@app.post("/login", response_model=UsuarioResponse)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    usuario = autenticar_usuario(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos.")
    access_token = criar_access_token(dados={"sub": usuario.username})
    _definir_cookie_sessao(response, access_token)
    return usuario


@app.post("/logout")
def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"detail": "Sessão encerrada."}


@app.get("/me", response_model=UsuarioResponse)
def me(usuario=Depends(obter_usuario_atual)):
    """Usado pelo frontend para checar se a sessão (cookie) ainda é válida,
    já que o JavaScript não tem acesso direto ao cookie httpOnly."""
    return usuario


@app.patch("/me", response_model=UsuarioResponse)
def atualizar_meu_perfil(
    dados: MeuPerfilUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    """
    Permite que o usuário atualize seu próprio perfil (nome completo, email, senha).
    Se mudar a senha, precisa confirmar com a senha atual.
    """
    # Se quer mudar senha, validar a senha atual
    if dados.nova_senha:
        if not dados.senha_atual:
            raise HTTPException(
                status_code=400,
                detail="Senha atual é obrigatória ao mudar a senha.",
            )
        
        # Validar que a senha atual está correta
        if not autenticar_usuario(db, usuario.username, dados.senha_atual):
            raise HTTPException(
                status_code=401,
                detail="Senha atual incorreta.",
            )
    
    # Atualizar nome completo
    if dados.nome_completo is not None:
        usuario.nome_completo = dados.nome_completo
    
    # Atualizar email (se não estiver em uso por outro usuário)
    if dados.email is not None:
        if dados.email != usuario.email:
            existente = (
                db.query(Usuario)
                .filter(Usuario.email == dados.email, Usuario.id != usuario.id)
                .first()
            )
            if existente:
                raise HTTPException(
                    status_code=409,
                    detail="Este e-mail já está em uso.",
                )
        usuario.email = dados.email

    # Atualizar setor
    if dados.setor_id is not None:
        _validar_setor(db, dados.setor_id)
        usuario.setor_id = dados.setor_id

    # Atualizar senha
    if dados.nova_senha:
        usuario.hashed_password = gerar_hash_senha(dados.nova_senha)
    
    db.commit()
    db.refresh(usuario)
    return usuario


@app.post("/me/desativar-conta", status_code=204)
def desativar_minha_conta(
    confirmacao: ConfirmacaoSenha,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    """
    Permite que o usuário desative a própria conta, confirmando com a senha.

    Diferente das rotas administrativas (onde um admin nunca pode desativar
    a si mesmo), aqui a autodesativação é o propósito da rota. Por isso a
    proteção contra lockout precisa ser explícita: se quem está saindo é o
    último administrador ativo do sistema, a ação é bloqueada — sem isso,
    o sistema ficaria permanentemente sem ninguém capaz de administrá-lo,
    e não há rota pública para promover um novo admin.
    """
    if not autenticar_usuario(db, usuario.username, confirmacao.senha):
        raise HTTPException(status_code=401, detail="Senha incorreta.")

    if usuario.is_admin:
        outros_admins_ativos = (
            db.query(Usuario)
            .filter(
                Usuario.is_admin.is_(True),
                Usuario.ativo.is_(True),
                Usuario.id != usuario.id,
            )
            .count()
        )
        if outros_admins_ativos == 0:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Você é o único administrador ativo. Cadastre ou reative outro "
                    "administrador antes de desativar sua conta."
                ),
            )

    usuario.ativo = False
    db.commit()

    return None


@app.post("/cadastro", response_model=UsuarioResponse, status_code=201)
def cadastrar_membro(dados: UsuarioCadastro, db: Session = Depends(get_db)):
    """Autocadastro de um membro comum (não-admin). Público — qualquer
    pessoa pode se cadastrar, mas nunca como administrador por aqui
    (is_admin é sempre False nesta rota; admins só nascem via painel admin
    ou via scripts/create_admin.py)."""
    _validar_setor(db, dados.setor_id)
    return criar_usuario(
        db,
        username=dados.username,
        senha=dados.senha,
        email=dados.email,
        nome_completo=dados.nome_completo,
        setor_id=dados.setor_id,
        is_admin=False,
    )


# --- Setores (referência fixa, pública — usada nos formulários de cadastro) ---

@app.get("/setores/", response_model=list[SetorResponse])
def listar_setores(db: Session = Depends(get_db)):
    return db.query(Setor).order_by(Setor.nome).all()


# --- Leitura de QR Code / OCR ---

@app.post("/qr/scan", response_model=QRScanResponse)
def escanear_qr(
    imagem: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_admin),
):
    """Lê o QR e altera o estoque automaticamente, sem formulário.

    Uma leitura de item existente adiciona exatamente 1 unidade.
    Um QR novo cria automaticamente 1 unidade usando os dados presentes no QR.
    """
    content_type = imagem.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Envie uma imagem capturada pela câmera.")
    try:
        content = imagem.file.read()
        result, roi = decode_qr_from_bytes(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail="Não foi possível processar a imagem.") from exc

    if not result:
        return QRScanResponse(
            sucesso=False,
            mensagem="Nenhum QR Code reconhecido dentro da região de leitura.",
            roi=roi,
            metodo=roi.get("method"),
        )

    filtros = []
    if result.codigo_qr:
        filtros.append(Item.codigo_qr == result.codigo_qr)
    if result.patrimonio:
        filtros.append(Item.patrimonio == result.patrimonio)

    item = db.query(Item).filter(or_(*filtros)).with_for_update().first() if filtros else None

    if item:
        item.quantidade_total += 1
        item.quantidade_disponivel += 1
        item.status = "ATIVO"
        db.commit()
        db.refresh(item)
        return QRScanResponse(
            sucesso=True,
            mensagem=f"Item identificado: +1 unidade adicionada ao estoque de {item.nome}.",
            raw=result.raw,
            patrimonio=result.patrimonio,
            codigo_qr=result.codigo_qr,
            nome=result.nome or item.nome,
            area=result.area or item.area,
            setor_id=item.setor_atual_id,
            setor_nome=item.setor_atual.nome if item.setor_atual else None,
            item=item,
            acao="adicionado",
            roi=roi,
            metodo=roi.get("method"),
        )

    if not result.nome:
        raise HTTPException(
            status_code=422,
            detail="QR reconhecido, mas não contém o campo 'nome'.",
        )

    setor = None
    if result.setor_id:
        setor = db.query(Setor).filter(Setor.id == result.setor_id).first()
    elif result.setor_nome:
        setor = db.query(Setor).filter(Setor.nome.ilike(result.setor_nome.strip())).first()

    if not setor:
        raise HTTPException(
            status_code=422,
            detail="QR reconhecido, mas não contém um setor válido. Use 'setor_id' ou 'setor_nome'.",
        )

    if not result.codigo_qr and not result.patrimonio:
        raise HTTPException(
            status_code=422,
            detail="QR reconhecido, mas não contém 'codigo_qr' ou 'patrimonio'.",
        )

    novo_item = Item(
        nome=result.nome,
        patrimonio=result.patrimonio,
        codigo_qr=result.codigo_qr or result.patrimonio,
        area=result.area,
        setor_atual_id=setor.id,
        quantidade_total=1,
        quantidade_disponivel=1,
        status="ATIVO",
    )
    db.add(novo_item)
    try:
        db.commit()
    except Exception:
        db.rollback()
        # Evita duplicidade se duas leituras chegarem simultaneamente.
        existente = None
        if result.codigo_qr:
            existente = db.query(Item).filter(Item.codigo_qr == result.codigo_qr).first()
        if not existente and result.patrimonio:
            existente = db.query(Item).filter(Item.patrimonio == result.patrimonio).first()
        if existente:
            existente.quantidade_total += 1
            existente.quantidade_disponivel += 1
            existente.status = "ATIVO"
            db.commit()
            db.refresh(existente)
            return QRScanResponse(
                sucesso=True,
                mensagem=f"Item identificado: +1 unidade adicionada ao estoque de {existente.nome}.",
                raw=result.raw,
                patrimonio=result.patrimonio,
                codigo_qr=result.codigo_qr,
                nome=existente.nome,
                area=existente.area,
                setor_id=existente.setor_atual_id,
                setor_nome=existente.setor_atual.nome if existente.setor_atual else None,
                item=existente,
                acao="adicionado",
                roi=roi,
                metodo=roi.get("method"),
            )
        raise HTTPException(status_code=409, detail="Não foi possível cadastrar o item automaticamente.")

    db.refresh(novo_item)
    try:
        enviar_email_novo_item(db, novo_item)
    except Exception as exc:
        print(f"Falha ao notificar novo item via QR: {exc}")
    return QRScanResponse(
        sucesso=True,
        mensagem=f"Novo item cadastrado automaticamente: {novo_item.nome}.",
        raw=result.raw,
        patrimonio=novo_item.patrimonio,
        codigo_qr=novo_item.codigo_qr,
        nome=novo_item.nome,
        area=novo_item.area,
        setor_id=novo_item.setor_atual_id,
        setor_nome=setor.nome,
        item=novo_item,
        acao="cadastrado",
        roi=roi,
        metodo=roi.get("method"),
    )


# --- Catálogo de itens (leitura: qualquer usuário autenticado) ---

@app.get("/itens/", response_model=list[ItemResponse])
def listar_itens(db: Session = Depends(get_db), usuario=Depends(obter_usuario_atual)):
    return db.query(Item).filter(Item.status == "ATIVO").order_by(Item.nome).all()


# --- Empréstimos (membro comum pega o item para si mesmo) ---

@app.post("/emprestimos/", response_model=EmprestimoResponse)
def registrar_emprestimo(
    dados: EmprestimoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    # Trava a linha no banco para evitar problemas de concorrência
    item = db.query(Item).with_for_update().filter(Item.id == dados.item_id).first()

    if not item or item.status != "ATIVO":
        raise HTTPException(status_code=404, detail="Item não encontrado.")

    # Validar quantidade disponível
    quantidade_solicitada = dados.quantidade
    if quantidade_solicitada > item.quantidade_disponivel:
        raise HTTPException(
            status_code=400,
            detail=f"Quantidade insuficiente. Disponível: {item.quantidade_disponivel}, Solicitado: {quantidade_solicitada}",
        )

    agora = datetime.now(UTC)
    devolucao_prevista = agora + timedelta(days=dados.dias_solicitados)
    limite_tolerancia = devolucao_prevista + timedelta(days=1)

    # Decrementar a quantidade disponível
    item.quantidade_disponivel -= quantidade_solicitada

    novo_emprestimo = Emprestimo(
        item_id=item.id,
        usuario_id=usuario.id,
        quantidade=quantidade_solicitada,
        data_retirada=agora,
        dias_solicitados=dados.dias_solicitados,
        data_devolucao_prevista=devolucao_prevista,
        data_limite_tolerancia=limite_tolerancia,
        status="EM_ANDAMENTO",
    )

    db.add(novo_emprestimo)
    db.commit()
    db.refresh(novo_emprestimo)

    return _construir_resposta_emprestimo(novo_emprestimo)


@app.get("/emprestimos/meus/", response_model=list[EmprestimoResponse])
def listar_meus_emprestimos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    """Lista os empréstimos do próprio usuário autenticado (nunca de outra
    pessoa) — usado pelo frontend para o membro ver o que está com ele e
    poder devolver."""
    emprestimos = (
        db.query(Emprestimo)
        .filter(Emprestimo.usuario_id == usuario.id)
        .order_by(Emprestimo.data_retirada.desc())
        .all()
    )
    return [_construir_resposta_emprestimo(e) for e in emprestimos]


@app.post("/emprestimos/{emprestimo_id}/devolver", response_model=EmprestimoResponse)
def devolver_meu_emprestimo(
    emprestimo_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    """O membro marca como devolvido um empréstimo que é seu. Não permite
    devolver empréstimo de outra pessoa (404 em vez de 403, pra não revelar
    se o ID pertence a alguém)."""
    emprestimo = (
        db.query(Emprestimo)
        .filter(Emprestimo.id == emprestimo_id, Emprestimo.usuario_id == usuario.id)
        .first()
    )
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")

    if emprestimo.status == "DEVOLVIDO":
        raise HTTPException(status_code=400, detail="Este empréstimo já foi devolvido.")
    if emprestimo.status == "PENDENTE_DEVOLUCAO":
        raise HTTPException(status_code=409, detail="A devolução já está aguardando conferência do administrador.")
    emprestimo.status = "PENDENTE_DEVOLUCAO"
    emprestimo.devolucao_solicitada_em = _agora_naive_utc()
    db.commit()
    db.refresh(emprestimo)
    return _construir_resposta_emprestimo(emprestimo)


# --- Painel do administrador ---
# Todas as rotas abaixo exigem usuário com is_admin=True (dependência
# exigir_admin), retornando 403 para qualquer membro comum que tentar
# acessá-las diretamente pela API.

@app.get("/admin/itens/", response_model=list[ItemResponse])
def listar_itens_admin(
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_admin),
):
    """
    Lista TODOS os itens, independente do status — diferente de GET /itens/
    (que só mostra ATIVO, pra quem vai pegar emprestado). O admin precisa
    ver os itens INATIVOS também, senão não teria como encontrá-los de
    novo pra reativar.
    """
    return db.query(Item).order_by(Item.nome).all()


@app.post("/admin/itens/", response_model=ItemResponse, status_code=201)
def cadastrar_item(
    dados: ItemCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_admin),
):
    _validar_setor(db, dados.setor_id)

    if dados.patrimonio:
        existente = db.query(Item).filter(Item.patrimonio == dados.patrimonio).first()
        if existente:
            raise HTTPException(
                status_code=409, detail="Já existe um item com esse número de patrimônio."
            )
    if dados.codigo_qr:
        existente = db.query(Item).filter(Item.codigo_qr == dados.codigo_qr).first()
        if existente:
            raise HTTPException(status_code=409, detail="Já existe um item com esse QR Code.")

    novo_item = Item(
        nome=dados.nome,
        patrimonio=dados.patrimonio,
        codigo_qr=dados.codigo_qr,
        area=dados.area,
        setor_atual_id=dados.setor_id,
        quantidade_total=dados.quantidade_total,
        quantidade_disponivel=dados.quantidade_total,
        status="ATIVO",
    )
    db.add(novo_item)
    db.commit()
    db.refresh(novo_item)
    try:
        enviar_email_novo_item(db, novo_item)
    except Exception as exc:
        # A falha de notificação nunca deve desfazer um cadastro já confirmado.
        print(f"Falha ao notificar cadastro de item: {exc}")
    return novo_item


@app.patch("/admin/itens/{item_id}", response_model=ItemResponse)
def editar_item(
    item_id: int,
    dados: ItemUpdate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_admin),
):
    """
    Edição parcial — o admin só envia os campos que quer mudar.
    `quantidade_total` não pode ser reduzida abaixo da quantidade já
    emprestada agora (calculada como total atual - disponível atual);
    quando reduzida validamente, `quantidade_disponivel` é recalculada na
    mesma proporção, preservando o número de unidades já emprestadas.
    """
    item = db.query(Item).with_for_update().filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado.")

    # exclude_unset: só considera campos que o cliente de fato enviou no
    # corpo da requisição — distingue "não mandei esse campo" de "mandei
    # esse campo como null", o que importa pra permitir limpar o
    # patrimônio (enviando null) sem afetar os outros campos.
    alteracoes = dados.model_dump(exclude_unset=True)

    if "setor_id" in alteracoes:
        _validar_setor(db, alteracoes["setor_id"])
        item.setor_atual_id = alteracoes["setor_id"]

    if "patrimonio" in alteracoes and alteracoes["patrimonio"] != item.patrimonio:
        novo_patrimonio = alteracoes["patrimonio"]
        if novo_patrimonio:
            existente = (
                db.query(Item)
                .filter(Item.patrimonio == novo_patrimonio, Item.id != item_id)
                .first()
            )
            if existente:
                raise HTTPException(
                    status_code=409,
                    detail="Já existe um item com esse número de patrimônio.",
                )
        item.patrimonio = novo_patrimonio

    if "codigo_qr" in alteracoes and alteracoes["codigo_qr"] != item.codigo_qr:
        novo_qr = alteracoes["codigo_qr"]
        if novo_qr:
            existente = db.query(Item).filter(Item.codigo_qr == novo_qr, Item.id != item_id).first()
            if existente:
                raise HTTPException(status_code=409, detail="Já existe um item com esse QR Code.")
        item.codigo_qr = novo_qr

    if "area" in alteracoes:
        item.area = alteracoes["area"]

    if "nome" in alteracoes:
        item.nome = alteracoes["nome"]

    if "quantidade_total" in alteracoes:
        novo_total = alteracoes["quantidade_total"]
        quantidade_emprestada = item.quantidade_total - item.quantidade_disponivel
        if novo_total < quantidade_emprestada:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Não é possível reduzir a quantidade total para {novo_total}: "
                    f"{quantidade_emprestada} unidade(s) já está(ão) emprestada(s) "
                    "no momento."
                ),
            )
        item.quantidade_disponivel = novo_total - quantidade_emprestada
        item.quantidade_total = novo_total

    db.commit()
    db.refresh(item)
    return item


@app.post("/admin/itens/{item_id}/desativar", response_model=ItemResponse)
def desativar_item(
    item_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_admin),
):
    """
    Marca o item como INATIVO — some do catálogo (GET /itens/ só mostra
    ATIVO), impedindo novos empréstimos. Não afeta empréstimos já em
    andamento desse item: quem já pegou continua podendo devolver
    normalmente, a devolução (POST /emprestimos/{id}/devolver) não checa o
    status do item, só o do empréstimo.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    item.status = "INATIVO"
    db.commit()
    db.refresh(item)
    return item


@app.post("/admin/itens/{item_id}/reativar", response_model=ItemResponse)
def reativar_item(
    item_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_admin),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    item.status = "ATIVO"
    db.commit()
    db.refresh(item)
    return item


@app.delete("/admin/itens/{item_id}", status_code=204)
def remover_item(
    item_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_admin),
):
    """Remove fisicamente um item somente quando não há histórico de empréstimos."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    if db.query(Emprestimo).filter(Emprestimo.item_id == item_id).first():
        raise HTTPException(status_code=409, detail="Não é possível remover um item com histórico de empréstimos. Desative-o para preservar o histórico.")
    db.delete(item)
    db.commit()
    return Response(status_code=204)


@app.get("/admin/emprestimos/", response_model=PaginaEmprestimosAdmin)
def listar_emprestimos_admin(
    pagina: int = Query(1, ge=1, description="Página atual, começando em 1."),
    tamanho_pagina: int = Query(20, ge=1, le=100, description="Itens por página (máx. 100)."),
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_admin),
):
    """Lista todos os empréstimos (de todos os membros), paginados, com nome
    do item, nome de quem pegou e setor — para o admin não precisar cruzar
    IDs. Mais recentes primeiro."""
    query = db.query(Emprestimo).order_by(Emprestimo.data_retirada.desc())
    total = query.count()
    total_paginas = math.ceil(total / tamanho_pagina) if total > 0 else 1
    offset = (pagina - 1) * tamanho_pagina
    emprestimos = query.offset(offset).limit(tamanho_pagina).all()
    return PaginaEmprestimosAdmin(
        itens=[_construir_resposta_emprestimo_admin(e) for e in emprestimos],
        total=total,
        pagina=pagina,
        tamanho_pagina=tamanho_pagina,
        total_paginas=total_paginas,
    )


@app.get("/admin/emprestimos/atrasados/resumo", response_model=ResumoAtrasados)
def resumo_emprestimos_atrasados(
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_admin),
):
    """
    Notificação proativa de atraso para o admin: em vez do admin precisar
    vasculhar a lista paginada procurando por linhas vermelhas, esta rota
    devolve só o que está atrasado agora — pensada para um banner exibido
    assim que o painel é aberto. Não há envio de e-mail/push aqui (exigiria
    credenciais de um serviço de SMTP/push que este projeto não tem
    configurado) — é uma notificação dentro da própria aplicação.
    """
    agora = _agora_naive_utc()
    emprestimos_atrasados = (
        db.query(Emprestimo)
        .filter(
            Emprestimo.status == "EM_ANDAMENTO",
            Emprestimo.data_limite_tolerancia < agora,
        )
        .order_by(Emprestimo.data_limite_tolerancia.asc())
        .all()
    )
    return ResumoAtrasados(
        total_atrasados=len(emprestimos_atrasados),
        itens=[_construir_resposta_emprestimo_admin(e) for e in emprestimos_atrasados],
    )


@app.post("/admin/emprestimos/{emprestimo_id}/devolver", response_model=EmprestimoAdminResponse)
def devolver_emprestimo_admin(
    emprestimo_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_admin),
):
    """Confirmação de devolução física feita pelo administrador — cobre o
    caso do membro não ter (ou não conseguir) marcar a devolução ele mesmo."""
    emprestimo = db.query(Emprestimo).filter(Emprestimo.id == emprestimo_id).first()
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")

    emprestimo = _processar_devolucao(db, emprestimo)
    return _construir_resposta_emprestimo_admin(emprestimo)


@app.post("/admin/administradores/", response_model=UsuarioResponse, status_code=201)
def cadastrar_administrador(
    dados: AdminCadastro,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_admin),
):
    """Cria um novo administrador. Só acessível por quem já é admin —
    nunca existiu (e não deve existir) uma rota pública equivalente."""
    _validar_setor(db, dados.setor_id)
    return criar_usuario(
        db,
        username=dados.username,
        senha=dados.senha,
        email=dados.email,
        nome_completo=dados.nome_completo,
        setor_id=dados.setor_id,
        is_admin=True,
    )


@app.get("/admin/usuarios/", response_model=list[UsuarioAdminResponse])
def listar_usuarios_admin(
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_admin),
):
    """Lista todos os usuários (membros e admins), com setor já resolvido —
    usado pelo admin para escolher quem desativar."""
    usuarios = db.query(Usuario).order_by(Usuario.username).all()
    return [_construir_resposta_usuario_admin(u) for u in usuarios]


@app.post("/admin/usuarios/{usuario_id}/desativar", response_model=UsuarioAdminResponse)
def desativar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_admin),
):
    """
    Desativa um usuário (membro ou admin) — impede login (autenticar_usuario
    e obter_usuario_atual já checam `ativo`, então uma sessão em andamento
    também para de funcionar na próxima requisição, mesmo com o cookie
    ainda válido).

    Proteção contra lockout: um admin não pode desativar a própria conta.
    Isso sozinho já garante que nunca fica zero admin ativo no sistema —
    quem chama esta rota precisa ser um admin ativo (via `exigir_admin`), e
    como ele não pode se autodesativar, sempre sobra pelo menos ele mesmo
    ativo. Uma checagem adicional de "não desativar o último admin" seria
    código morto: qualquer OUTRO admin que chamasse esta rota já conta como
    um admin ativo além do alvo, então a contagem de "admins ativos restantes"
    nunca chegaria a zero por esse caminho.
    """
    if usuario_id == admin.id:
        raise HTTPException(status_code=400, detail="Você não pode desativar sua própria conta.")

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    usuario.ativo = False
    db.commit()
    db.refresh(usuario)
    return _construir_resposta_usuario_admin(usuario)


@app.post("/admin/usuarios/{usuario_id}/reativar", response_model=UsuarioAdminResponse)
def reativar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_admin),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    usuario.ativo = True
    db.commit()
    db.refresh(usuario)
    return _construir_resposta_usuario_admin(usuario)


@app.patch("/admin/usuarios/{usuario_id}", response_model=UsuarioAdminResponse)
def editar_usuario(
    usuario_id: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_admin),
):
    """
    Edição parcial de um usuário (membro ou admin), incluindo o próprio
    admin logado editando a si mesmo — só a desativação/exclusão da
    própria conta é bloqueada, editar a própria conta é permitido.
    `exclude_unset` distingue "não mandei esse campo" de "mandei null",
    permitindo inclusive limpar um e-mail incorreto, se for o caso.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    alteracoes = dados.model_dump(exclude_unset=True)

    if "username" in alteracoes and alteracoes["username"] != usuario.username:
        existente = (
            db.query(Usuario)
            .filter(Usuario.username == alteracoes["username"], Usuario.id != usuario_id)
            .first()
        )
        if existente:
            raise HTTPException(status_code=409, detail="Este nome de usuário já está em uso.")
        usuario.username = alteracoes["username"]

    if "email" in alteracoes:
        novo_email = alteracoes["email"]
        if novo_email and novo_email != usuario.email:
            existente_email = (
                db.query(Usuario)
                .filter(Usuario.email == novo_email, Usuario.id != usuario_id)
                .first()
            )
            if existente_email:
                raise HTTPException(
                    status_code=409, detail="Este e-mail já está cadastrado para outro usuário."
                )
        usuario.email = novo_email

    if "nome_completo" in alteracoes:
        usuario.nome_completo = alteracoes["nome_completo"]

    if "setor_id" in alteracoes:
        if alteracoes["setor_id"] is not None:
            _validar_setor(db, alteracoes["setor_id"])
        usuario.setor_id = alteracoes["setor_id"]

    if alteracoes.get("nova_senha"):
        usuario.hashed_password = gerar_hash_senha(alteracoes["nova_senha"])

    db.commit()
    db.refresh(usuario)
    return _construir_resposta_usuario_admin(usuario)


@app.delete("/admin/usuarios/{usuario_id}", status_code=204)
def excluir_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_admin),
):
    """
    Exclui permanentemente um usuário (membro ou admin) — diferente de
    desativar, aqui a conta deixa de existir de vez. O histórico de
    empréstimos dessa pessoa NÃO é apagado (auditoria é importante demais
    pra um sistema de controle de patrimônio); a referência ao usuário nos
    empréstimos antigos vira NULL (ON DELETE SET NULL — ver models.py) e o
    painel admin passa a mostrar "(usuário removido)" no lugar do nome.

    Mesma proteção contra lockout da desativação: um admin não pode
    excluir a própria conta.
    """
    if usuario_id == admin.id:
        raise HTTPException(status_code=400, detail="Você não pode excluir sua própria conta.")

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    db.delete(usuario)
    db.commit()


# --- Agendador de tarefas de background ---

@app.on_event("startup")
def startup_event():
    """Inicia o agendador de tarefas de notificação de email."""
    from tasks import iniciar_scheduler
    
    # Iniciar o scheduler apenas se email estiver habilitado
    email_habilitado = os.getenv("EMAIL_HABILITADO", "false").lower() == "true"
    if email_habilitado:
        iniciar_scheduler(SessionLocal)
        print("✅ Sistema de notificações por email iniciado")
    else:
        print("⚠️  Notificações por email desabilitadas (configure EMAIL_HABILITADO=true)")


@app.on_event("shutdown")
def shutdown_event():
    """Para o agendador de tarefas."""
    from tasks import parar_scheduler
    
    parar_scheduler()


# --- Recursos operacionais adicionais ---

@app.post("/admin/notas-fiscais/extrair-pdf")
async def extrair_produtos_pdf(
    arquivo: UploadFile = File(...),
    admin: Usuario = Depends(exigir_admin),
):
    """Extrai linhas de produto de um PDF/DANFE, com OCR para PDFs digitalizados."""
    nome = (arquivo.filename or "nota.pdf").lower()
    if not nome.endswith(".pdf") or arquivo.content_type not in ("application/pdf", "application/octet-stream", None):
        raise HTTPException(status_code=415, detail="Envie um arquivo PDF válido.")
    conteudo = await arquivo.read()
    if not conteudo or len(conteudo) > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="O PDF deve ter até 15 MB.")
    if not conteudo.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="O arquivo enviado não parece ser um PDF válido.")
    try:
        documento = fitz.open(stream=conteudo, filetype="pdf")
        if len(documento) > 40:
            raise HTTPException(status_code=413, detail="O PDF deve ter no máximo 40 páginas.")
        texto = "\n".join(p.get_text("text") for p in documento)
        if len(texto.strip()) < 30:
            # OCR por página; Tesseract está instalado na imagem Docker.
            try:
                import pytesseract
                from PIL import Image
                for pagina in documento:
                    pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    texto += "\n" + pytesseract.image_to_string(img, lang=os.environ.get("OCR_LANG", "por+eng"))
            except Exception as exc:
                raise HTTPException(status_code=422, detail=f"PDF digitalizado detectado, mas não foi possível executar OCR: {exc}")
        documento.close()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Não foi possível ler o PDF: {exc}")

    produtos = []
    # Extrai linhas com estrutura típica de DANFE: código, descrição, unidade,
    # quantidade, valor unitário e total. O resultado sempre exige revisão humana.
    linhas = [re.sub(r"\s+", " ", l).strip() for l in texto.splitlines() if l.strip()]
    for linha in linhas:
        if len(produtos) >= 500:
            break
        if not re.search(r"\d+[,.]\d{2}", linha):
            continue
        valores = re.findall(r"(?<!\w)\d+[,.]\d{2,4}(?!\w)", linha)
        if len(valores) < 2:
            continue
        # Descarta cabeçalhos/rodapés e tenta identificar quantidade decimal.
        if any(p in linha.lower() for p in ("valor total da nota", "base de cálculo", "imposto", "frete", "desconto")):
            continue
        partes = re.split(r"\s+", linha)
        if len(partes) < 4:
            continue
        # Nome é a parte textual antes da sequência de valores; códigos/unidades são opcionais.
        primeiro_valor = min((linha.find(v) for v in valores if linha.find(v) >= 0), default=len(linha))
        prefixo = linha[:primeiro_valor].strip(" -|\t")
        nome_produto = re.sub(r"^\d{1,4}\s+", "", prefixo).strip()
        if len(nome_produto) < 3 or nome_produto.lower() in {"produto", "descrição", "descrição do produto"}:
            continue
        # Quantidade é aproximada a partir da coluna imediatamente anterior ao preço unitário.
        trecho = linha[primeiro_valor:]
        nums = re.findall(r"\d+(?:[,.]\d+)?", trecho)
        quantidade = 1
        if nums:
            try:
                candidato = float(nums[0].replace(",", "."))
                if 0 < candidato <= 100000:
                    quantidade = max(1, round(candidato))
            except ValueError:
                pass
        def moeda(v):
            try: return float(v.replace(".", "").replace(",", ".")) if "," in v else float(v)
            except ValueError: return 0.0
        codigo = partes[0] if partes and re.fullmatch(r"[A-Za-z0-9._/-]{2,30}", partes[0]) else ""
        produtos.append({"codigo": codigo[:50], "nome": nome_produto[:150], "quantidade": quantidade,
                         "unidade": "", "valorUnitario": moeda(valores[-2]), "valorTotal": moeda(valores[-1])})
    # Elimina duplicações idênticas ocasionadas por cabeçalhos repetidos em PDFs multipágina.
    unicos = []
    vistos = set()
    for produto in produtos:
        chave = (produto["codigo"], produto["nome"].casefold(), produto["quantidade"], produto["valorTotal"])
        if chave not in vistos:
            vistos.add(chave); unicos.append(produto)
    if not unicos:
        raise HTTPException(status_code=422, detail="Não identifiquei linhas de produtos com confiança neste PDF. Se for uma digitalização, verifique a qualidade ou utilize o XML original da NF-e.")
    return {"nome_arquivo": arquivo.filename or "nota.pdf", "produtos": unicos,
            "aviso": "Extração automática aproximada. Confira descrição, quantidade e valores antes de cadastrar no estoque."}


@app.post("/admin/notas-fiscais/", status_code=201)
def registrar_nota_fiscal(dados: dict, db: Session = Depends(get_db), admin: Usuario = Depends(exigir_admin)):
    produtos = dados.get("produtos") or []
    cadastrados = int(dados.get("total_cadastrados") or 0)
    nota = NotaFiscal(nome_arquivo=str(dados.get("nome_arquivo") or "nota fiscal")[:255],
        tipo_arquivo=str(dados.get("tipo_arquivo") or "XML")[:30], status="IMPORTADA" if cadastrados else "PROCESSADA",
        total_produtos=len(produtos), total_cadastrados=max(0, cadastrados),
        produtos_json=json.dumps(produtos, ensure_ascii=False), observacoes=str(dados.get("observacoes") or "")[:2000], usuario_id=admin.id)
    db.add(nota); db.commit(); db.refresh(nota)
    return {"id": nota.id, "nome_arquivo": nota.nome_arquivo, "tipo_arquivo": nota.tipo_arquivo,
        "status": nota.status, "total_produtos": nota.total_produtos, "total_cadastrados": nota.total_cadastrados, "criada_em": nota.criada_em}


@app.get("/admin/notas-fiscais/")
def listar_notas_fiscais(db: Session = Depends(get_db), admin: Usuario = Depends(exigir_admin)):
    notas = db.query(NotaFiscal).order_by(NotaFiscal.criada_em.desc()).limit(500).all()
    return [{"id": n.id, "nome_arquivo": n.nome_arquivo, "tipo_arquivo": n.tipo_arquivo, "status": n.status,
             "total_produtos": n.total_produtos, "total_cadastrados": n.total_cadastrados,
             "produtos": json.loads(n.produtos_json or "[]"), "observacoes": n.observacoes, "criada_em": n.criada_em,
             "responsavel": n.usuario.nome_completo or n.usuario.username if n.usuario else "Usuário removido"} for n in notas]


@app.post("/contato/", status_code=201)
def enviar_mensagem_contato(dados: dict, db: Session = Depends(get_db), usuario: Usuario = Depends(obter_usuario_atual)):
    assunto = str(dados.get("assunto") or "").strip()
    mensagem = str(dados.get("mensagem") or "").strip()
    if len(assunto) < 3 or len(assunto) > 160 or len(mensagem) < 10 or len(mensagem) > 5000:
        raise HTTPException(status_code=422, detail="Informe um assunto de 3 a 160 caracteres e uma mensagem de 10 a 5000 caracteres.")
    anexos = dados.get("anexos") or []
    if not isinstance(anexos, list) or len(anexos) > 4:
        raise HTTPException(status_code=422, detail="Anexe no máximo 4 imagens por chamado.")
    for anexo in anexos:
        if not isinstance(anexo, dict) or not str(anexo.get("data") or "").startswith(("data:image/png;base64,", "data:image/jpeg;base64,", "data:image/webp;base64,")) or len(str(anexo.get("data"))) > 1_500_000:
            raise HTTPException(status_code=422, detail="Anexo inválido. Use imagens PNG, JPEG ou WebP de até 1 MB.")
    historico = [{"autor_id": usuario.id, "autor_nome": usuario.nome_completo or usuario.username, "autor_foto": usuario.foto_perfil, "tipo": "MENSAGEM", "mensagem": mensagem, "criada_em": _agora_naive_utc().isoformat()}]
    registro = MensagemContato(usuario_id=usuario.id, assunto=assunto, mensagem=mensagem, historico_json=json.dumps(historico, ensure_ascii=False), anexos_json=json.dumps(anexos, ensure_ascii=False))
    db.add(registro); db.commit(); db.refresh(registro)
    return {"id": registro.id, "assunto": registro.assunto, "mensagem": registro.mensagem, "status": registro.status, "resposta": registro.resposta, "anexos": json.loads(registro.anexos_json or "[]"), "historico": json.loads(registro.historico_json or "[]"), "criada_em": registro.criada_em}


@app.get("/contato/minhas/")
def listar_minhas_mensagens(db: Session = Depends(get_db), usuario: Usuario = Depends(obter_usuario_atual)):
    registros = db.query(MensagemContato).filter(MensagemContato.usuario_id == usuario.id).order_by(MensagemContato.criada_em.desc()).all()
    return [{"id": m.id, "assunto": m.assunto, "mensagem": m.mensagem, "status": m.status, "resposta": m.resposta, "criada_em": m.criada_em, "atualizada_em": m.atualizada_em, "anexos": json.loads(m.anexos_json or "[]"), "historico": json.loads(m.historico_json or "[]")} for m in registros]


@app.get("/admin/contato/")
def listar_mensagens_contato(db: Session = Depends(get_db), admin: Usuario = Depends(exigir_admin)):
    registros = db.query(MensagemContato).order_by(MensagemContato.criada_em.desc()).limit(500).all()
    return [{"id": m.id, "assunto": m.assunto, "mensagem": m.mensagem, "status": m.status, "resposta": m.resposta,
             "criada_em": m.criada_em, "usuario_nome": m.usuario.nome_completo or m.usuario.username if m.usuario else "Usuário removido",
             "usuario_email": m.usuario.email if m.usuario else None, "usuario_foto": m.usuario.foto_perfil if m.usuario else None, "anexos": json.loads(m.anexos_json or "[]"), "historico": json.loads(m.historico_json or "[]")} for m in registros]


@app.patch("/admin/contato/{mensagem_id}")
def responder_mensagem_contato(mensagem_id: int, dados: dict, db: Session = Depends(get_db), admin: Usuario = Depends(exigir_admin)):
    registro = db.query(MensagemContato).filter(MensagemContato.id == mensagem_id).first()
    if not registro: raise HTTPException(status_code=404, detail="Mensagem não encontrada.")
    resposta = str(dados.get("resposta") or "").strip()
    if len(resposta) < 2 or len(resposta) > 5000: raise HTTPException(status_code=422, detail="A resposta deve ter entre 2 e 5000 caracteres.")
    historico = json.loads(registro.historico_json or "[]")
    historico.append({"autor_id": admin.id, "autor_nome": admin.nome_completo or admin.username, "autor_foto": admin.foto_perfil, "tipo": "RESPOSTA", "mensagem": resposta, "criada_em": _agora_naive_utc().isoformat()})
    registro.historico_json = json.dumps(historico, ensure_ascii=False)
    registro.resposta = resposta; registro.status = "RESPONDIDA"; registro.respondida_por_id = admin.id; registro.atualizada_em = _agora_naive_utc()
    db.commit(); db.refresh(registro)
    return {"id": registro.id, "status": registro.status, "resposta": registro.resposta}


@app.patch("/contato/{mensagem_id}/status")
def atualizar_status_chamado(mensagem_id: int, dados: dict, db: Session = Depends(get_db), usuario: Usuario = Depends(obter_usuario_atual)):
    registro = db.query(MensagemContato).filter(MensagemContato.id == mensagem_id, MensagemContato.usuario_id == usuario.id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Chamado não encontrado.")
    acao = str(dados.get("acao") or "").upper()
    if acao not in {"CONCLUIR", "REABRIR", "NAO_RESOLVIDO"}:
        raise HTTPException(status_code=422, detail="Ação de chamado inválida.")
    if acao == "CONCLUIR":
        registro.status = "CONCLUIDA"
    elif acao in {"REABRIR", "NAO_RESOLVIDO"}:
        registro.status = "ABERTA"
    registro.atualizada_em = _agora_naive_utc()
    hist = json.loads(registro.historico_json or "[]")
    texto = {"CONCLUIR": "Usuário confirmou a resolução e concluiu o chamado.", "REABRIR": "Usuário reabriu o chamado.", "NAO_RESOLVIDO": "Usuário informou que o problema ainda não foi resolvido."}[acao]
    hist.append({"autor_id": usuario.id, "autor_nome": usuario.nome_completo or usuario.username, "autor_foto": usuario.foto_perfil, "tipo": acao, "mensagem": texto, "criada_em": _agora_naive_utc().isoformat()})
    registro.historico_json = json.dumps(hist, ensure_ascii=False)
    db.commit()
    return {"id": registro.id, "status": registro.status}


@app.post("/me/foto")
async def atualizar_foto_perfil(arquivo: UploadFile = File(...), db: Session = Depends(get_db), usuario: Usuario = Depends(obter_usuario_atual)):
    tipo = arquivo.content_type or ""
    if tipo not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=415, detail="Envie uma imagem PNG, JPEG ou WebP.")
    conteudo = await arquivo.read()
    if not conteudo or len(conteudo) > 2 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="A foto deve ter até 2 MB.")
    try:
        from PIL import Image
        imagem = Image.open(io.BytesIO(conteudo)); imagem.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="O arquivo enviado não é uma imagem válida.")
    usuario.foto_perfil = f"data:{tipo};base64," + base64.b64encode(conteudo).decode("ascii")
    db.commit(); db.refresh(usuario)
    return {"foto_perfil": usuario.foto_perfil}


@app.get("/admin/itens/{item_id}/qrcode")
def gerar_qrcode_item(item_id: int, db: Session = Depends(get_db), admin: Usuario = Depends(exigir_admin)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item: raise HTTPException(status_code=404, detail="Item não encontrado.")
    payload = item.codigo_qr or item.patrimonio or f"AVT-{item.id:06d}"
    try:
        import qrcode
        from PIL import Image
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
        qr.add_data(payload); qr.make(fit=True)
        imagem = qr.make_image(fill_color="#10243e", back_color="white").convert("RGB")
        buffer = io.BytesIO(); imagem.save(buffer, format="PNG")
        return {"item_id": item.id, "nome": item.nome, "codigo": payload, "imagem": "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Não foi possível gerar o QR Code: {exc}")
