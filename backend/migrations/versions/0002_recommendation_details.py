from alembic import op
import sqlalchemy as sa

revision = "0002_recommendation_details"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("recommendations", sa.Column("expected_impact", sa.Text(), nullable=False, server_default=""))
    op.add_column("recommendations", sa.Column("dataset_name", sa.String(255), nullable=False, server_default=""))
    op.add_column("recommendations", sa.Column("analysis_summary", sa.Text(), nullable=False, server_default="{}"))
    op.add_column("recommendations", sa.Column("created_by", sa.String(36), nullable=True))


def downgrade():
    op.drop_column("recommendations", "created_by")
    op.drop_column("recommendations", "analysis_summary")
    op.drop_column("recommendations", "dataset_name")
    op.drop_column("recommendations", "expected_impact")
