"""add core user fields

Revision ID: 0017
Revises: 0016
Create Date: 2026-02-14 06:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=50), nullable=True))
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.execute("UPDATE users SET username = split_part(email, '@', 1) WHERE username IS NULL")

    op.alter_column("users", "username", nullable=False)
    op.create_unique_constraint(op.f("uq_users_username"), "users", ["username"])
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_constraint(op.f("uq_users_username"), "users", type_="unique")
    op.drop_column("users", "updated_at")
    op.drop_column("users", "is_admin")
    op.drop_column("users", "username")
