"""Додати boolean та обчислити його для наявних записів."""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"


def upgrade():
    # Додати nullable -> обчислити старі рядки -> заборонити NULL.
    op.add_column("air_quality", sa.Column("go_outside", sa.Boolean, nullable=True))
    op.execute(sa.text("UPDATE air_quality SET go_outside = (us_epa_index <= 2 AND gb_defra_index <= 3)"))
    op.alter_column("air_quality", "go_outside", existing_type=sa.Boolean(), nullable=False)
    op.add_column("wind", sa.Column("go_outside", sa.Boolean, nullable=True))
    op.execute(sa.text("UPDATE wind SET go_outside = (wind_kph <= 36 AND gust_kph <= 50)"))
    op.alter_column("wind", "go_outside", existing_type=sa.Boolean(), nullable=False)


def downgrade():
    op.drop_column("air_quality", "go_outside")
    op.drop_column("wind", "go_outside")
