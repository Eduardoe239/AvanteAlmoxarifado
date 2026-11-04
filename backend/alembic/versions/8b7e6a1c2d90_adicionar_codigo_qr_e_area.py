"""Restaurar migração de codigo_qr e area.

Revision ID: 8b7e6a1c2d90
Revises: 7a1c3f9d2b04
"""
from alembic import op
import sqlalchemy as sa

revision = "8b7e6a1c2d90"
down_revision = "7a1c3f9d2b04"
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    colunas = {coluna["name"] for coluna in inspector.get_columns("itens")}
    if "codigo_qr" not in colunas:
        op.add_column("itens", sa.Column("codigo_qr", sa.String(120), nullable=True))
    if "area" not in colunas:
        op.add_column("itens", sa.Column("area", sa.String(120), nullable=True))
    inspector = sa.inspect(bind)
    indices = {indice["name"] for indice in inspector.get_indexes("itens")}
    if "ix_itens_codigo_qr" not in indices:
        op.create_index("ix_itens_codigo_qr", "itens", ["codigo_qr"], unique=True)

def downgrade() -> None:
    # Preserva os dados de QR Code e área ao reverter a revisão.
    pass
