# server/services/source_service.py
from sqlalchemy.orm import Session
from server.db import NewsSource
from typing import Optional


def get_or_create_source(
        db: Session,
        name: str,
        url: str,
        source_type: str,
        category: Optional[str] = None
) -> NewsSource:
    """
    Находит или создает источник новостей.
    """
    # Проверяем существующий источник по URL (уникальность)
    source = db.query(NewsSource).filter(NewsSource.url == url).first()

    if not source:
        source = NewsSource(
            name=name,
            url=url,
            source_type=source_type,
            category=category
        )
        db.add(source)
        db.flush()

    return source


def get_source_by_id(db: Session, source_id: int) -> Optional[NewsSource]:
    return db.query(NewsSource).filter(NewsSource.id == source_id).first()