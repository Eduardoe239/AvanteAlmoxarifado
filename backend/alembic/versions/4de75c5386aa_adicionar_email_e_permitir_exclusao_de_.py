"""adicionar email e permitir exclusao de usuario preservando historico

Revision ID: 4de75c5386aa
Revises: 5dc55278ec99
Create Date: 2026-09-12 00:48:44.998361

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4de75c5386aa"
down_revision: Union[str, Sequence[str], None] = "5dc55278ec99"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NAMING_CONVENTION = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}


def _find_usuario_fk_name():
    """Localiza a FK de emprestimos.usuario_id -> usuarios.id."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    for fk in inspector.get_foreign_keys("emprestimos"):
        columns = fk.get("constrained_columns") or []
        referred_table = fk.get("referred_table")

        if (
            "usuario_id" in columns
            and referred_table == "usuarios"
        ):
            return fk.get("name")

    return None


def upgrade() -> None:
    """Upgrade schema."""

    # Primeiro localiza a FK realmente existente no banco.
    existing_fk_name = _find_usuario_fk_name()

    with op.batch_alter_table(
        "emprestimos",
        schema=None,
        naming_convention=NAMING_CONVENTION,
    ) as batch_op:

        # Permite preservar empréstimos quando um usuário for excluído.
        batch_op.alter_column(
            "usuario_id",
            existing_type=sa.INTEGER(),
            nullable=True,
        )

        # Remove a FK antiga somente se ela realmente existir.
        if existing_fk_name:
            batch_op.drop_constraint(
                existing_fk_name,
                type_="foreignkey",
            )

        # Cria a nova FK com ON DELETE SET NULL.
        batch_op.create_foreign_key(
            "fk_emprestimos_usuario_id_usuarios",
            "usuarios",
            ["usuario_id"],
            ["id"],
            ondelete="SET NULL",
        )

    with op.batch_alter_table("usuarios", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "email",
                sa.String(length=255),
                nullable=True,
            )
        )

        batch_op.create_unique_constraint(
            "uq_usuarios_email",
            ["email"],
        )


def downgrade() -> None:
    """Downgrade schema."""

    with op.batch_alter_table("usuarios", schema=None) as batch_op:
        batch_op.drop_constraint(
            "uq_usuarios_email",
            type_="unique",
        )

        batch_op.drop_column("email")

    with op.batch_alter_table(
        "emprestimos",
        schema=None,
        naming_convention=NAMING_CONVENTION,
    ) as batch_op:

        existing_fk_name = _find_usuario_fk_name()

        if existing_fk_name:
            batch_op.drop_constraint(
                existing_fk_name,
                type_="foreignkey",
            )

        batch_op.create_foreign_key(
            "fk_emprestimos_usuario_id_usuarios",
            "usuarios",
            ["usuario_id"],
            ["id"],
        )

        batch_op.alter_column(
            "usuario_id",
            existing_type=sa.INTEGER(),
            nullable=False,
        )