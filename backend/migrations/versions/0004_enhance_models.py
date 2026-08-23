from alembic import op
import sqlalchemy as sa

revision = "0004_enhance_models"
down_revision = "0003_datasets"
branch_labels = None
depends_on = None


def upgrade():
    # Alter users table
    op.alter_column("users", "role", existing_type=sa.String(30), new_column_kwargs={"server_default": "user"})
    op.add_column("users", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))

    # Alter documents table
    op.add_column("documents", sa.Column("description", sa.Text(), nullable=False, server_default=""))
    op.add_column("documents", sa.Column("processing_status", sa.String(255), nullable=False, server_default=""))
    op.add_column("documents", sa.Column("file_path", sa.String(500), nullable=False, server_default=""))
    op.add_column("documents", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    
    # Update default status for documents
    op.execute("UPDATE documents SET status = 'processing' WHERE status = 'indexed'")

    # Alter recommendations table
    op.add_column("recommendations", sa.Column("dismissed", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("recommendations", sa.Column("dismissed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("recommendations", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))

    # Alter powerbi_dashboards table
    op.add_column("powerbi_dashboards", sa.Column("created_by", sa.String(36), nullable=True))
    op.add_column("powerbi_dashboards", sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.add_column("powerbi_dashboards", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))

    # Alter team_members table
    op.add_column("team_members", sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.add_column("team_members", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))


def downgrade():
    # Remove columns added to team_members
    op.drop_column("team_members", "updated_at")
    op.drop_column("team_members", "created_at")

    # Remove columns added to powerbi_dashboards
    op.drop_column("powerbi_dashboards", "updated_at")
    op.drop_column("powerbi_dashboards", "created_at")
    op.drop_column("powerbi_dashboards", "created_by")

    # Remove columns added to recommendations
    op.drop_column("recommendations", "updated_at")
    op.drop_column("recommendations", "dismissed_at")
    op.drop_column("recommendations", "dismissed")

    # Remove columns added to documents
    op.drop_column("documents", "updated_at")
    op.drop_column("documents", "file_path")
    op.drop_column("documents", "processing_status")
    op.drop_column("documents", "description")
    
    # Restore original status default
    op.execute("UPDATE documents SET status = 'indexed' WHERE status = 'processing'")
    op.alter_column("documents", "status", existing_type=sa.String(30), new_column_kwargs={"server_default": "indexed"})

    # Remove updated_at from users
    op.drop_column("users", "updated_at")
    op.alter_column("users", "role", existing_type=sa.String(30), new_column_kwargs={"server_default": "admin"})
