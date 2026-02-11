"""conversations user_id not null

Revision ID: 8f88f071d6a6
Revises: 1c39da6ad210
Create Date: 2026-02-02 21:04:41.215271

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f88f071d6a6'
down_revision: Union[str, Sequence[str], None] = '1c39da6ad210'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # limpiar datos legacy (huérfanos)
    op.execute("""
        DELETE FROM messages
        WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id IS NULL);
    """)
    op.execute("DELETE FROM conversations WHERE user_id IS NULL;")

    # enforce schema
    op.execute("ALTER TABLE conversations ALTER COLUMN user_id SET NOT NULL;")


def downgrade():
    op.execute("ALTER TABLE conversations ALTER COLUMN user_id DROP NOT NULL;")
