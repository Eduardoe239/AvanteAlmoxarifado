from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from database import Base


class Setor(Base):
    """
    Setores fixos da organização. A lista de valores válidos é seedada via
    migração Alembic (não editável pela aplicação) — ver
    alembic/versions/*_seed_setores.py.
    """
    __tablename__ = "setores"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False)


class Usuario(Base):
    """
    Representa tanto administradores quanto membros comuns (quem pega
    itens emprestados). `nome_completo` e `setor_id` são obrigatórios para
    membros (preenchidos no autocadastro) e opcionais para administradores
    criados via CLI (scripts/create_admin.py). `email` é obrigatório no
    autocadastro a partir desta versão (preparação para notificação por
    e-mail, a ser implementada futuramente) mas nullable no banco, porque
    contas criadas antes dessa mudança (ou via CLI) podem não ter — nesse
    caso, um admin pode completá-lo depois pelo painel.
    """
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    nome_completo = Column(String(150), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    setor_id = Column(Integer, ForeignKey("setores.id"), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    foto_perfil = Column(Text, nullable=True)

    setor = relationship("Setor")


class Item(Base):
    __tablename__ = "itens"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    patrimonio = Column(String(50), unique=True, nullable=True)
    codigo_qr = Column(String(120), unique=True, nullable=True, index=True)
    area = Column(String(120), nullable=True)
    setor_atual_id = Column(Integer, ForeignKey("setores.id"), nullable=True)
    quantidade_total = Column(Integer, nullable=False)
    quantidade_disponivel = Column(Integer, nullable=False)
    status = Column(String(20), default="ATIVO", nullable=False)

    setor_atual = relationship("Setor")


class Emprestimo(Base):
    __tablename__ = "emprestimos"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("itens.id"), nullable=False)
    # nullable + ON DELETE SET NULL de propósito: quando um admin exclui um
    # usuário (não apenas desativa), o histórico de empréstimos precisa
    # continuar existindo para auditoria — só a referência à pessoa vira
    # NULL. O painel admin mostra "(usuário removido)" nesse caso (ver
    # main.py:_construir_resposta_emprestimo_admin).
    usuario_id = Column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    quantidade = Column(Integer, default=1, nullable=False)  # Quantidade emprestada
    data_retirada = Column(DateTime, default=lambda: datetime.now(UTC))
    dias_solicitados = Column(Integer, nullable=False)
    data_devolucao_prevista = Column(DateTime, nullable=False)
    data_limite_tolerancia = Column(DateTime, nullable=False)
    data_devolucao_real = Column(DateTime, nullable=True)
    status = Column(String(20), default="EM_ANDAMENTO", nullable=False)
    # Controle do lembrete de "falta 1 dia" (enviado uma única vez).
    emails_enviados = Column(Boolean, default=False, nullable=False)
    # Data do último alerta de ATRASO enviado. Diferente do lembrete acima,
    # o alerta de atraso se repete enquanto o item não volta — mas no
    # máximo uma vez por dia. Sem este campo, o scheduler (que roda de hora
    # em hora) mandaria 24 e-mails por dia para a mesma pessoa.
    ultimo_alerta_atraso = Column(DateTime, nullable=True)
    devolucao_solicitada_em = Column(DateTime, nullable=True)

    item = relationship("Item")
    usuario = relationship("Usuario")


class NotaFiscal(Base):
    __tablename__ = "notas_fiscais"
    id = Column(Integer, primary_key=True, index=True)
    nome_arquivo = Column(String(255), nullable=False)
    tipo_arquivo = Column(String(30), nullable=False)
    status = Column(String(30), nullable=False, default="IMPORTADA")
    total_produtos = Column(Integer, nullable=False, default=0)
    total_cadastrados = Column(Integer, nullable=False, default=0)
    produtos_json = Column(Text, nullable=False, default="[]")
    observacoes = Column(Text, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    criada_em = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    usuario = relationship("Usuario")


class MensagemContato(Base):
    __tablename__ = "mensagens_contato"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    assunto = Column(String(160), nullable=False)
    mensagem = Column(Text, nullable=False)
    status = Column(String(30), nullable=False, default="ABERTA")
    resposta = Column(Text, nullable=True)
    historico_json = Column(Text, nullable=False, default="[]")
    anexos_json = Column(Text, nullable=False, default="[]")
    respondida_por_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    criada_em = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    atualizada_em = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    respondida_por = relationship("Usuario", foreign_keys=[respondida_por_id])
