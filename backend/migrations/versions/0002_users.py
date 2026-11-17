"""Create user authentication table."""

from alembic import op
from app.db import Base
from app import models  # noqa: F401

revision = "0002_users"
down_revision = "0001_master_data"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    op.drop_table("users")
