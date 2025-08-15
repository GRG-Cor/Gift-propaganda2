"""add_media_fields_to_news_items

Revision ID: 001
Revises:
Create Date: 2025-07-26 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Добавляем новые поля в таблицу news_items
    op.add_column('news_items', sa.Column('image_url', sa.String(1000), nullable=True))
    op.add_column('news_items', sa.Column('video_url', sa.String(1000), nullable=True))
    op.add_column('news_items', sa.Column('reading_time', sa.Integer(), nullable=True))
    op.add_column('news_items', sa.Column('views_count', sa.Integer(), nullable=True))
    op.add_column('news_items', sa.Column('author', sa.String(200), nullable=True))
    op.add_column('news_items', sa.Column('subtitle', sa.String(500), nullable=True))

def downgrade():
    # Удаляем добавленные поля
    op.drop_column('news_items', 'subtitle')
    op.drop_column('news_items', 'author')
    op.drop_column('news_items', 'views_count')
    op.drop_column('news_items', 'reading_time')
    op.drop_column('news_items', 'video_url')
    op.drop_column('news_items', 'image_url')
