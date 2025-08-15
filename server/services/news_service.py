# services/news_service.py
from sqlalchemy.orm import Session
from server.db import NewsSource  # Импортируйте вашу модель NewsSource


def get_or_create_source(session: Session, source_name: str, url: str = None, source_type: str = None, category: str = None) -> NewsSource:
    """
    Находит или создаёт источник новостей.

    Args:
        session: SQLAlchemy сессия
        source_name: Название источника
        url: URL источника
        source_type: Тип источника (например, 'telegram', 'rss')
        category: Категория источника

    Returns:
        Объект NewsSource (существующий или новый)
    """
    # Пытаемся найти существующий источник
    source = session.query(NewsSource).filter_by(name=source_name).first()

    # Если не нашли - создаём новый
    if not source:
        # Заполняем обязательные поля
        source = NewsSource(
            name=source_name,
            url=url or '',
            source_type=source_type or 'telegram',
            category=category,
            is_active=True
        )
        session.add(source)
        session.flush()  # Получаем ID без коммита всей транзакции

    return source