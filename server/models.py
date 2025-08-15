from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Добавляем модель для медиа
class MediaItem(BaseModel):
    type: str
    url: Optional[str] = None
    thumbnail: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

class NewsSourceResponse(BaseModel):
    id: int
    name: str
    url: str
    source_type: str
    category: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class NewsItemResponse(BaseModel):
    id: int
    title: str
    content: str
    content_html: Optional[str] = None
    link: str
    publish_date: str
    category: str
    media: Optional[List[MediaItem]] = None
    reading_time: Optional[int] = None
    views_count: Optional[int] = 0
    author: Optional[str] = None
    source_name: Optional[str] = None  # Добавьте это
    source_url: Optional[str] = None   # И это
    source: Optional[NewsSourceResponse] = None  # Полная информация об источнике
    
    class Config:
        from_attributes = True


class NewsResponse(BaseModel):
    data: List[NewsItemResponse]
    total: int
    page: int
    pages: int

class CategoryResponse(BaseModel):
    categories: List[str]

class StatsResponse(BaseModel):
    total_news: int
    categories: dict
    last_updated: str
