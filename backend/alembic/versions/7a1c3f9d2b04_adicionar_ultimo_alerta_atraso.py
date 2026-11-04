"""adicionar ultimo_alerta_atraso

Controla a frequência do e-mail de atraso: sem esta coluna, o scheduler
(que roda de hora em hora) reenviaria o alerta a cada execução, gerando
24 e-mails por dia para a mesma pessoa enquanto o item não fosse devolvido.

Revision ID: 7a1c3f9d2b04
Revises: 5e66d94ccf2e
Create Date: 2026-09-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a1c3f9d2b04'
down_revision: Union[str, Sequence[str], None] = '5e66d94ccf2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'emprestimos',
        sa.Column('ultimo_alerta_atraso', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('emprestimos', 'ultimo_alerta_atraso')
