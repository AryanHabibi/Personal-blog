from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5c32e1c2adb9"
down_revision: Union[str, Sequence[str], None] = "1ce061737a47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("blog_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["blog_id"],
            ["blogs.id"],
            name="fk_comments_blog_id_blogs",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_comments_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("comments", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_comments_blog_id"),
            ["blog_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_comments_id"),
            ["id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_comments_user_id"),
            ["user_id"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("comments", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_comments_user_id"))
        batch_op.drop_index(batch_op.f("ix_comments_id"))
        batch_op.drop_index(batch_op.f("ix_comments_blog_id"))

    op.drop_table("comments")