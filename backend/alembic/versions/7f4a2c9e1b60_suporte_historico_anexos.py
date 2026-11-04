"""Add persistent support history and attachments."""
from alembic import op
import sqlalchemy as sa

revision = "7f4a2c9e1b60"
down_revision = "5e66d94ccf2e"
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("mensagens_contato")}
    if "historico_json" not in cols:
        op.add_column("mensagens_contato", sa.Column("historico_json", sa.Text(), nullable=False, server_default="[]"))
    if "anexos_json" not in cols:
        op.add_column("mensagens_contato", sa.Column("anexos_json", sa.Text(), nullable=False, server_default="[]"))

def downgrade():
    op.drop_column("mensagens_contato", "anexos_json")
    op.drop_column("mensagens_contato", "historico_json")
