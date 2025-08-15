import asyncio
from datetime import datetime
from sqlalchemy.orm import Session

from server.db import NewsItem, NewsSource
from server.parsers import telegram_news_service

async def fetch_telegram_channels(session: Session):
    try:
        # Получаем все новости
        news = await telegram_news_service.get_all_news(category='all', limit=50)
        sources_cache = {}

        for item in news:
            # Создаем или находим источник
            source_name = item.get('source', 'Unknown')
            source_url = item.get('link', '')
            category = item.get('category', 'general')

            # Проверяем, есть ли источник в кэше
            source_key = f"{source_name}_{source_url}"
            if source_key not in sources_cache:
                # Ищем существующий источник
                existing_source = session.query(NewsSource).filter(
                    NewsSource.name == source_name,
                    NewsSource.url == source_url
                ).first()

                if existing_source:
                    sources_cache[source_key] = existing_source.id
                else:
                    # Создаем новый источник
                    new_source = NewsSource(
                        type="telegram",
                        url=source_url,
                        name=source_name,
                        category=category,
                        is_active=True
                    )
                    session.add(new_source)
                    session.flush()
                    sources_cache[source_key] = new_source.id

            source_id = sources_cache[source_key]

            # Проверяем, существует ли уже такая новость
            existing_news = session.query(NewsItem).filter(
                NewsItem.title == item['title'],
                NewsItem.source_id == source_id
            ).first()

            if not existing_news:
                # Парсим дату
                try:
                    if isinstance(item['date'], str):
                        publish_date = datetime.fromisoformat(item['date'].replace('Z', '+00:00'))
                    else:
                        publish_date = item['date']
                except:
                    publish_date = datetime.now()

                # Извлекаем медиа данные
                media = item.get('media')
                media_list = []
                message_text = item.get('text', '') or item.get('caption', '') or item['title']
                content_html = message_text
                
                if media:
                    # Обрабатываем медиа как массив или одиночный объект
                    media_items = media if isinstance(media, list) else [media]
                    
                    for media_item in media_items:
                        if media_item and isinstance(media_item, dict):
                            media_list.append({
                                'type': media_item.get('type'),
                                'url': media_item.get('url'),
                                'thumbnail': media_item.get('thumbnail'),
                                'width': media_item.get('width'),
                                'height': media_item.get('height')
                            })
                            
                            # Добавляем медиа в HTML контент
                            if media_item.get('type') == 'photo' and media_item.get('url'):
                                content_html += f'<br><img src="{media_item["url"]}" style="max-width:100%; height:auto; border-radius:8px; margin:10px 0;"/>'
                            elif media_item.get('type') == 'video' and media_item.get('url'):
                                thumbnail = media_item.get('thumbnail', '')
                                content_html += f'<br><video controls poster="{thumbnail}" style="max-width:100%; height:auto; border-radius:8px; margin:10px 0;">'
                                content_html += f'<source src="{media_item["url"]}" type="video/mp4">'
                                content_html += '</video>'
                # Создаем новость
                db_item = NewsItem(
                    source_id=source_id,
                    title=item['title'],
                    content=item.get('text', ''),  # Plain text
                    content_html=content_html,  # HTML с медиа
                    link=item.get('link', ''),
                    publish_date=publish_date,
                    category=item.get('category', 'general'),
                    media=media_list  # Сохраняем медиа как JSON
                )
                session.add(db_item)

        session.commit()
        print(f"Добавлено новостей в базу")

    except Exception as e:
        print(f"Ошибка при загрузке каналов: {e}")
        session.rollback()
        raise e