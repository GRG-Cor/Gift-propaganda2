"""
Миграция 003: Добавление полей для автоматической публикации постов в Telegram канал
"""

def upgrade():
    """
    Добавляет новые поля в таблицу news_items для отслеживания публикации в канал
    """
    return [
        """
        ALTER TABLE news_items 
        ADD COLUMN is_published_to_channel BOOLEAN DEFAULT FALSE
        """,
        """
        ALTER TABLE news_items 
        ADD COLUMN published_to_channel_at TIMESTAMP
        """,
        """
        ALTER TABLE news_items 
        ADD COLUMN telegram_message_id INTEGER
        """
    ]


def downgrade():
    """
    Удаляет добавленные поля
    """
    return [
        """
        ALTER TABLE news_items 
        DROP COLUMN IF EXISTS is_published_to_channel
        """,
        """
        ALTER TABLE news_items 
        DROP COLUMN IF EXISTS published_to_channel_at
        """,
        """
        ALTER TABLE news_items 
        DROP COLUMN IF EXISTS telegram_message_id
        """
    ]
