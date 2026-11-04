"""Adiciona foto de perfil, fluxo de devolução, histórico de notas e contato."""
from alembic import op
import sqlalchemy as sa

revision = "c1f8a2d4e6b0"
down_revision = "8b7e6a1c2d90"
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    usuarios = {c["name"] for c in inspector.get_columns("usuarios")}
    emprestimos = {c["name"] for c in inspector.get_columns("emprestimos")}
    if "foto_perfil" not in usuarios:
        op.add_column("usuarios", sa.Column("foto_perfil", sa.Text(), nullable=True))
    if "devolucao_solicitada_em" not in emprestimos:
        op.add_column("emprestimos", sa.Column("devolucao_solicitada_em", sa.DateTime(), nullable=True))
    op.create_table(
        "notas_fiscais",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome_arquivo", sa.String(255), nullable=False),
        sa.Column("tipo_arquivo", sa.String(30), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="IMPORTADA"),
        sa.Column("total_produtos", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_cadastrados", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("produtos_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("criada_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "mensagens_contato",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assunto", sa.String(160), nullable=False),
        sa.Column("mensagem", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="ABERTA"),
        sa.Column("resposta", sa.Text(), nullable=True),
        sa.Column("respondida_por_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("criada_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("atualizada_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_notas_fiscais_criada_em", "notas_fiscais", ["criada_em"])
    op.create_index("ix_mensagens_contato_status", "mensagens_contato", ["status"])

def downgrade():
    op.drop_index("ix_mensagens_contato_status", table_name="mensagens_contato")
    op.drop_index("ix_notas_fiscais_criada_em", table_name="notas_fiscais")
    op.drop_table("mensagens_contato")
    op.drop_table("notas_fiscais")
    op.drop_column("emprestimos", "devolucao_solicitada_em")
    op.drop_column("usuarios", "foto_perfil")
