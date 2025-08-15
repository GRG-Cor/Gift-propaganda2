"""add_content_html_to_news_items

Revision ID: 002
Revises: 001
Create Date: 2025-07-26 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Добавляем колонку content_html в таблицу news_items
    op.add_column('news_items', sa.Column('content_html', sa.Text(), nullable=True))

def downgrade():
    # Удаляем колонку content_html
    op.drop_column('news_items', 'content_html') 