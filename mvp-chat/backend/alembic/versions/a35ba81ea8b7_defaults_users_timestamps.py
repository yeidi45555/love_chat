"""defaults users timestamps

Revision ID: a35ba81ea8b7
Revises: 8554b278d296
Create Date: 2026-02-02 19:42:56.729484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a35ba81ea8b7'
down_revision: Union[str, Sequence[str], None] = '8554b278d296'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op

def upgrade():
    op.execute("ALTER TABLE users ALTER COLUMN created_at SET DEFAULT now()")
    op.execute("ALTER TABLE user_profiles ALTER COLUMN created_at SET DEFAULT now()")
    op.execute("ALTER TABLE user_profiles ALTER COLUMN updated_at SET DEFAULT now()")

def downgrade():
    op.execute("ALTER TABLE users ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE user_profiles ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE user_profiles ALTER COLUMN updated_at DROP DEFAULT")
