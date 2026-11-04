"""Adicionar quantidade e email tracking a empréstimos

Revision ID: 5e66d94ccf2e
Revises: 4de75c5386aa
Create Date: 2024-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e66d94ccf2e'
down_revision = '4de75c5386aa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adicionar coluna quantidade
    op.add_column('emprestimos', sa.Column('quantidade', sa.Integer(), nullable=False, server_default='1'))
    
    # Adicionar coluna emails_enviados.
    # server_default precisa ser uma expressão SQL (string ou sa.text), nunca
    # um bool do Python — passar False cru faz o Alembic estourar
    # ArgumentError e aborta o `alembic upgrade head` num deploy limpo.
    op.add_column(
        'emprestimos',
        sa.Column('emails_enviados', sa.Boolean(), nullable=False, server_default=sa.text('false')),
    )


def downgrade() -> None:
    # Remover colunas
    op.drop_column('emprestimos', 'emails_enviados')
    op.drop_column('emprestimos', 'quantidade')
