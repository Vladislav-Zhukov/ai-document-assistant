"""fix messages cascade delete

Revision ID: 9b66286f8b26
Revises: 53b4551e3bcd
Create Date: 2026-06-21 22:52:04.916965

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b66286f8b26'
down_revision: Union[str, Sequence[str], None] = '53b4551e3bcd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "messages_chat_id_fkey",
        "messages",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "messages_chat_id_fkey",
        "messages",
        "chats",
        ["chat_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "messages_chat_id_fkey",
        "messages",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "messages_chat_id_fkey",
        "messages",
        "chats",
        ["chat_id"],
        ["id"],
    )