"""align collection and view FKs to UUID

Revision ID: 0008
Revises: 0007
Create Date: 2026-01-13 18:30:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())

    if inspector.has_table("collections"):
        op.drop_constraint(
            op.f("fk_collections_user_id_users"), "collections", type_="foreignkey"
        )
        op.alter_column(
            "collections",
            "user_id",
            existing_type=sa.Integer(),
            type_=postgresql.UUID(as_uuid=True),
            nullable=False,
            postgresql_using="user_id::uuid",
        )
        op.create_foreign_key(
            op.f("fk_collections_user_id_users"),
            "collections",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )

    if inspector.has_table("views"):
        op.drop_constraint(op.f("fk_views_user_id_users"), "views", type_="foreignkey")
        op.drop_constraint(
            op.f("fk_views_episode_id_episodes"), "views", type_="foreignkey"
        )
        op.alter_column(
            "views",
            "user_id",
            existing_type=sa.Integer(),
            type_=postgresql.UUID(as_uuid=True),
            nullable=False,
            postgresql_using="user_id::uuid",
        )
        op.alter_column(
            "views",
            "episode_id",
            existing_type=sa.Integer(),
            type_=postgresql.UUID(as_uuid=True),
            nullable=False,
            postgresql_using="episode_id::uuid",
        )
        op.create_foreign_key(
            op.f("fk_views_user_id_users"),
            "views",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )
        op.create_foreign_key(
            op.f("fk_views_episode_id_episodes"),
            "views",
            "episodes",
            ["episode_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())

    if inspector.has_table("collections"):
        op.drop_constraint(
            op.f("fk_collections_user_id_users"), "collections", type_="foreignkey"
        )
        op.alter_column(
            "collections",
            "user_id",
            existing_type=postgresql.UUID(as_uuid=True),
            type_=sa.Integer(),
            nullable=False,
            postgresql_using="user_id::integer",
        )
        op.create_foreign_key(
            op.f("fk_collections_user_id_users"),
            "collections",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )

    if inspector.has_table("views"):
        op.drop_constraint(
            op.f("fk_views_episode_id_episodes"), "views", type_="foreignkey"
        )
        op.drop_constraint(op.f("fk_views_user_id_users"), "views", type_="foreignkey")
        op.alter_column(
            "views",
            "episode_id",
            existing_type=postgresql.UUID(as_uuid=True),
            type_=sa.Integer(),
            nullable=False,
            postgresql_using="episode_id::integer",
        )
        op.alter_column(
            "views",
            "user_id",
            existing_type=postgresql.UUID(as_uuid=True),
            type_=sa.Integer(),
            nullable=False,
            postgresql_using="user_id::integer",
        )
        op.create_foreign_key(
            op.f("fk_views_episode_id_episodes"),
            "views",
            "episodes",
            ["episode_id"],
            ["id"],
            ondelete="CASCADE",
        )
        op.create_foreign_key(
            op.f("fk_views_user_id_users"),
            "views",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )
