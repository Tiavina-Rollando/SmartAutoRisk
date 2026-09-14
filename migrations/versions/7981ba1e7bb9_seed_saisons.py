"""seed saisons

Revision ID: 7981ba1e7bb9
Revises: 49fe6cb96ec3
Create Date: 2026-04-15 20:09:36.670987

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7981ba1e7bb9'
down_revision: Union[str, Sequence[str], None] = '49fe6cb96ec3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    saisons_table = sa.table(
        "saisons",
        sa.column("id", sa.BigInteger),
        sa.column("mois", sa.SmallInteger),
        sa.column("periode", sa.String),
        sa.column("type", sa.String),
    )

    op.bulk_insert(saisons_table, [
        {"id": 1, "mois": 1, "periode": "Calme", "type": "Pluvieux"},
        {"id": 2, "mois": 2, "periode": "Calme", "type": "Pluvieux"},
        {"id": 3, "mois": 3, "periode": "Fête", "type": "Pluvieux"},
        {"id": 4, "mois": 4, "periode": "Calme", "type": "Sec"},
        {"id": 5, "mois": 5, "periode": "Calme", "type": "Sec"},
        {"id": 6, "mois": 6, "periode": "Fête", "type": "Sec"},
        {"id": 7, "mois": 7, "periode": "Vacance", "type": "Sec"},
        {"id": 8, "mois": 8, "periode": "Vacance", "type": "Sec"},
        {"id": 9, "mois": 9, "periode": "Vacance", "type": "Sec"},
        {"id": 10, "mois": 10, "periode": "Calme", "type": "Sec"},
        {"id": 11, "mois": 11, "periode": "Calme", "type": "Pluvieux"},
        {"id": 12, "mois": 12, "periode": "Fête", "type": "Pluvieux"},
    ])


def downgrade():
    op.execute("DELETE FROM saisons")