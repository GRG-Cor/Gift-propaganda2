from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import logging

from server.db import get_db, NewsItem, NewsSource, recreate_engine, recreate_models
from server.models import NewsResponse, NewsItemResponse, MediaItem, NewsSourceResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/news/", response_model=NewsResponse)
async def get_news(
        category: Optional[str] = Query(None, description="Фильтр по категории"),
        limit: int = Query(50, description="Количество новостей", le=100),
        offset: int = Query(0, description="Смещение для пагинации"),
        page: int = Query(1, description="Номер страницы"),
        db: Session = Depends(get_db)
):
    """Получить список новостей с фильтрацией"""
    try:
        # Вычисляем offset из page
        calculated_offset = (page - 1) * limit if page > 0 else offset
        
        logger.info(f"Запрос новостей: category={category}, limit={limit}, page={page}, offset={calculated_offset}")

        # Принудительно обновляем метаданные и модели
        recreate_engine()
        NewsItem, NewsSource = recreate_models()

        # Базовый запрос
        query = db.query(NewsItem)

        # Фильтр по категории
        if category and category != "all":
            query = query.filter(NewsItem.category == category)

        # Сортировка по дате публикации
        query = query.order_by(desc(NewsItem.publish_date))

        # Пагинация
        total = query.count()
        news_items = query.offset(calculated_offset).limit(limit).all()

        logger.info(f"Найдено {len(news_items)} новостей из {total} общих")

        # Соберем source_id для всех новостей
        source_ids = [item.source_id for item in news_items if item.source_id is not None]
        sources = {}
        if source_ids:
            sources_list = db.query(NewsSource).filter(NewsSource.id.in_(source_ids)).all()
            sources = {source.id: source for source in sources_list}

        # Преобразование в response модель
        news_data = []
        for item in news_items:
            try:
                                # Получаем медиа из JSON поля
                media_list = []
                if item.media:
                    try:
                        # Добавляем отладочную информацию
                        logger.info(f"Processing media for item {item.id}: {type(item.media)} - {item.media}")
                        
                        # Если media это строка JSON, парсим её
                        if isinstance(item.media, str):
                            import json
                            media_data = json.loads(item.media)
                        else:
                            media_data = item.media
                        
                        # Проверяем, является ли media_data списком или одним объектом
                        if isinstance(media_data, list):
                            media_list = [MediaItem(**media) for media in media_data]
                        else:
                            # Если это один объект, оборачиваем в список
                            media_list = [MediaItem(**media_data)]
                            
                        logger.info(f"Successfully parsed media for {item.id}: {len(media_list)} items")
                    except Exception as e:
                        logger.warning(f"Error parsing media for {item.id}: {e}")
                        logger.warning(f"Media data: {item.media}")
                        # Пробуем создать медиа из image_url и video_url как fallback
                        if item.image_url:
                            media_list = [MediaItem(
                                type='photo',
                                url=item.image_url,
                                thumbnail=item.image_url
                            )]
                            logger.info(f"Created fallback photo media for {item.id}")
                        elif item.video_url:
                            media_list = [MediaItem(
                                type='video',
                                url=item.video_url,
                                thumbnail=item.image_url
                            )]
                            logger.info(f"Created fallback video media for {item.id}")
                else:
                    # Если медиа нет, пробуем создать из image_url и video_url
                    if item.image_url:
                        media_list = [MediaItem(
                            type='photo',
                            url=item.image_url,
                            thumbnail=item.image_url
                        )]
                        logger.info(f"Created photo media from image_url for {item.id}")
                    elif item.video_url:
                        media_list = [MediaItem(
                            type='video',
                            url=item.video_url,
                            thumbnail=item.image_url
                        )]
                        logger.info(f"Created video media from video_url for {item.id}")

                # Получаем источник
                source = sources.get(item.source_id)
                source_name = source.name if source else None
                source_url = source.url if source else None

                # Отладочная информация
                logger.info(f"Processing item {item.id}: content_html exists = {item.content_html is not None}, length = {len(item.content_html) if item.content_html else 0}")
                
                news_data.append(NewsItemResponse(
                    id=item.id,
                    title=item.title or "",
                    content=item.content or "",  # Plain text
                    content_html=item.content_html,  # HTML контент (может быть None)
                    link=item.link or "",
                    publish_date=item.publish_date.isoformat() if item.publish_date else datetime.now().isoformat(),
                    category=item.category or "general",
                    media=media_list,
                    reading_time=item.reading_time,
                    views_count=item.views_count or 0,
                    author=item.author,
                    source_name=source_name,
                    source_url=source_url,
                    source=NewsSourceResponse.from_orm(source) if source else None
                ))
            except Exception as e:
                logger.warning(f"Ошибка при обработке новости {item.id}: {e}")
                continue

        return NewsResponse(
            data=news_data,
            total=total,
            page=page,
            pages=(total + limit - 1) // limit
        )

    except Exception as e:
        logger.error(f"Ошибка при получении новостей: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении новостей: {str(e)}")


@router.get("/news/{news_id}", response_model=NewsItemResponse)
async def get_news_item(
        news_id: int,
        db: Session = Depends(get_db)
):
    """Получить конкретную новость по ID"""
    try:
        news_item = db.query(NewsItem).filter(NewsItem.id == news_id).first()

        if not news_item:
            raise HTTPException(status_code=404, detail="Новость не найдена")

        # Получаем источник
        source = db.query(NewsSource).get(news_item.source_id) if news_item.source_id else None

        # Получаем медиа
        media_list = []
        if news_item.media:
            try:
                # Добавляем отладочную информацию
                logger.info(f"Processing media for item {news_item.id}: {type(news_item.media)} - {news_item.media}")
                
                # Если media это строка JSON, парсим её
                if isinstance(news_item.media, str):
                    import json
                    media_data = json.loads(news_item.media)
                else:
                    media_data = news_item.media
                
                # Проверяем, является ли media_data списком или одним объектом
                if isinstance(media_data, list):
                    media_list = [MediaItem(**media) for media in media_data]
                else:
                    # Если это один объект, оборачиваем в список
                    media_list = [MediaItem(**media_data)]
                    
                logger.info(f"Successfully parsed media for {news_item.id}: {len(media_list)} items")
            except Exception as e:
                logger.warning(f"Error parsing media for {news_item.id}: {e}")
                logger.warning(f"Media data: {news_item.media}")
                # Пробуем создать медиа из image_url и video_url как fallback
                if news_item.image_url:
                    media_list = [MediaItem(
                        type='photo',
                        url=news_item.image_url,
                        thumbnail=news_item.image_url
                    )]
                    logger.info(f"Created fallback photo media for {news_item.id}")
                elif news_item.video_url:
                    media_list = [MediaItem(
                        type='video',
                        url=news_item.video_url,
                        thumbnail=news_item.image_url
                    )]
                    logger.info(f"Created fallback video media for {news_item.id}")
        else:
            # Если медиа нет, пробуем создать из image_url и video_url
            if news_item.image_url:
                media_list = [MediaItem(
                    type='photo',
                    url=news_item.image_url,
                    thumbnail=news_item.image_url
                )]
                logger.info(f"Created photo media from image_url for {news_item.id}")
            elif news_item.video_url:
                media_list = [MediaItem(
                    type='video',
                    url=news_item.video_url,
                    thumbnail=news_item.image_url
                )]
                logger.info(f"Created video media from video_url for {news_item.id}")

        # Увеличиваем счетчик просмотров
        if news_item.views_count is None:
            news_item.views_count = 0
        news_item.views_count += 1
        db.commit()

        return NewsItemResponse(
            id=news_item.id,
            title=news_item.title or "",
            content=news_item.content or "",
            content_html=news_item.content_html,  # Может быть None
            link=news_item.link or "",
            publish_date=news_item.publish_date.isoformat() if news_item.publish_date else datetime.now().isoformat(),
            category=news_item.category or "general",
            media=media_list,
            reading_time=news_item.reading_time,
            views_count=news_item.views_count,
            author=news_item.author,
            source_name=source.name if source else None,
            source_url=source.url if source else None,
            source=NewsSourceResponse.from_orm(source) if source else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении новости {news_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении новости: {str(e)}")


@router.get("/categories/")
async def get_categories(db: Session = Depends(get_db)):
    """Получить список доступных категорий"""
    try:
        categories = db.query(NewsItem.category).distinct().all()
        return {"categories": [cat[0] for cat in categories if cat[0]]}
    except Exception as e:
        logger.error(f"Ошибка при получении категорий: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении категорий")


@router.get("/stats/")
async def get_stats(db: Session = Depends(get_db)):
    """Получить статистику новостей"""
    try:
        total_news = db.query(NewsItem).count()

        # Статистика по категориям
        categories_stats = {}
        categories = db.query(NewsItem.category).distinct().all()

        for cat in categories:
            if cat[0]:
                count = db.query(NewsItem).filter(NewsItem.category == cat[0]).count()
                categories_stats[cat[0]] = count

        return {
            "total_news": total_news,
            "categories": categories_stats,
            "last_updated": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении статистики")