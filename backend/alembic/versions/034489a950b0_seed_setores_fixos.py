"""seed setores fixos

Revision ID: 034489a950b0
Revises: bcc0d229b7e7
Create Date: 2026-09-03 18:18:11.225083

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '034489a950b0'
down_revision: Union[str, Sequence[str], None] = 'bcc0d229b7e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Lista fixa de setores da organização. Alterar setores existentes deve ser
# feito por uma nova migração (não editando esta), para manter o histórico
# do schema rastreável e reproduzível em qualquer ambiente.
SETORES = [
    "Embarcados",
    "Projetos",
    "Gestão de Pessoas",
    "Comercial",
    "Financeiro",
    "Diretoria Executiva",
]

setores_table = sa.table(
    "setores",
    sa.column("id", sa.Integer),
    sa.column("nome", sa.String),
)


def upgrade() -> None:
    """Upgrade schema."""
    op.bulk_insert(
        setores_table,
        [{"nome": nome} for nome in SETORES],
    )


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    conn.execute(
        setores_table.delete().where(setores_table.c.nome.in_(SETORES))
    )
