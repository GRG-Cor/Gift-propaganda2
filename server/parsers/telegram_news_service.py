import aiohttp
import asyncio
import feedparser
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta
import logging
import re
import hashlib

logger = logging.getLogger(__name__)


class TelegramNewsService:
    """Сервис для получения новостей из Telegram каналов и RSS источников"""

    def __init__(self):
        # Только канал @nextgen_NFT по запросу пользователя
        self.channels = [
            {'username': 'nextgen_NFT', 'name': 'NextGen NFT', 'category': 'nft'}
        ]

        # RSS источники согласно ТЗ - до 5 проверенных лент
        self.rss_sources = [
            {'url': 'https://vc.ru/rss', 'name': 'VC.ru', 'category': 'tech'},
            {'url': 'https://www.coindesk.com/arc/outboundfeeds/rss/', 'name': 'CoinDesk', 'category': 'crypto'},
            {'url': 'https://cointelegraph.com/rss', 'name': 'Cointelegraph', 'category': 'crypto'},
            {'url': 'https://habr.com/ru/rss/articles/', 'name': 'Habr NFT', 'category': 'nft'}
        ]

        self.cache = {}
        self.cache_ttl = timedelta(minutes=30)  # Кэш на 30 минут согласно ТЗ

        # Ключевые слова для категоризации согласно ТЗ
        self.keywords = {
            'gifts': [
                'подарок', 'подарки', 'бесплатно', 'халява', 'промокод', 'скидка',
                'акция', 'розыгрыш', 'бонус', 'даром', 'гифт', 'gift', 'freebie',
                'раздача', 'конкурс', 'приз', 'награда', 'cashback', 'кэшбек'
            ],
            'nft': [
                'nft', 'нфт', 'токен', 'коллекция', 'мета', 'opensea', 'digital art',
                'коллекционный', 'цифровое искусство', 'метавселенная', 'avatar',
                'аватар', 'pfp', 'mint', 'минт', 'drop', 'дроп', 'rare', 'раритет'
            ],
            'crypto': [
                'криптовалюта', 'биткоин', 'bitcoin', 'ethereum', 'блокчейн', 'деф',
                'defi', 'торги', 'курс', 'btc', 'eth', 'usdt', 'binance', 'трейдинг',
                'стейкинг', 'майнинг', 'altcoin', 'альткоин', 'pump', 'dump', 'hodl'
            ],
            'tech': [
                'технологии', 'it', 'ит', 'программирование', 'разработка', 'стартап',
                'инновации', 'ai', 'ии', 'machine learning', 'блокчейн', 'веб3',
                'app', 'приложение', 'software', 'hardware', 'gadget', 'гаджет'
            ],
            'community': [
                'сообщество', 'чат', 'общение', 'форум', 'дискуссия', 'мнение',
                'обсуждение', 'новости', 'анонс', 'встреча', 'event', 'мероприятие'
            ]
        }

    def categorize_content(self, title: str, description: str = "") -> str:
        """
        Автоматическая категоризация контента по ключевым словам согласно ТЗ
        Приоритет: gifts > crypto > nft > tech > community
        """
        content = (title + " " + description).lower()

        # Подсчитываем совпадения для каждой категории
        category_scores = {}
        for category, keywords in self.keywords.items():
            score = sum(1 for keyword in keywords if keyword in content)
            if score > 0:
                category_scores[category] = score

        if not category_scores:
            return 'general'

        # Возвращаем категорию с наибольшим количеством совпадений
        # При равенстве очков используем приоритет
        priority = ['gifts', 'crypto', 'nft', 'tech', 'community']

        max_score = max(category_scores.values())
        best_categories = [cat for cat, score in category_scores.items() if score == max_score]

        for priority_cat in priority:
            if priority_cat in best_categories:
                return priority_cat

        return list(category_scores.keys())[0]  # Fallback

    async def fetch_telegram_channel(self, channel_username: str) -> List[Dict[str, Any]]:
        """
        Получение новостей из Telegram канала через веб-скрапинг
        Согласно ТЗ - интеграция с Telegram каналами для получения актуальных новостей
        """
        try:
            channel_data = next((ch for ch in self.channels if ch['username'] == channel_username), None)
            if not channel_data:
                logger.warning(f"Channel {channel_username} not found in configured channels")
                return []

            # Используем публичный API Telegram для получения постов
            url = f"https://t.me/s/{channel_username}"

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            return self._parse_telegram_html(html_content, channel_data)
                        else:
                            logger.warning(f"Failed to fetch {url}, status: {response.status}")
                            return self._generate_mock_posts(channel_data)
                except aiohttp.ClientTimeout:
                    logger.warning(f"Timeout fetching {url}, using mock data")
                    return self._generate_mock_posts(channel_data)
                except Exception as e:
                    logger.warning(f"Error fetching {url}: {e}, using mock data")
                    return self._generate_mock_posts(channel_data)

        except Exception as e:
            logger.error(f"Error in fetch_telegram_channel for {channel_username}: {e}")
            return []

    def _parse_telegram_html(self, html_content: str, channel_data: Dict) -> List[Dict[str, Any]]:
        """Парсинг HTML содержимого Telegram канала с поддержкой медиа и полного контента"""
        import re
        from html import unescape
        from bs4 import BeautifulSoup

        posts = []

        try:
            # Используем BeautifulSoup для более точного парсинга
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Находим все сообщения
            message_widgets = soup.find_all('div', class_='tgme_widget_message')
            
            for i, message in enumerate(message_widgets[:15]):  # Увеличиваем лимит до 15 постов
                try:
                    # Извлекаем полный текст сообщения
                    text_widget = message.find('div', class_='tgme_widget_message_text')
                    if not text_widget:
                        continue
                    
                    # Получаем полный текст без обрезки
                    full_text = text_widget.get_text(strip=True)
                    if not full_text:
                        continue
                    
                    # Очищаем текст от лишних пробелов
                    full_text = re.sub(r'\s+', ' ', full_text).strip()
                    
                    # Извлекаем HTML контент для сохранения форматирования
                    html_content = str(text_widget)
                    
                    # Извлекаем дату
                    time_element = message.find('time')
                    date = datetime.now().isoformat()
                    if time_element and time_element.get('datetime'):
                        try:
                            date_str = time_element['datetime']
                            date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).isoformat()
                        except:
                            pass
                    
                    # Извлекаем медиа контент
                    media = None
                    
                    # Проверяем на фото - улучшенный парсинг
                    photo_wrap = message.find('a', class_='tgme_widget_message_photo_wrap')
                    if photo_wrap:
                        # Пробуем разные способы извлечения URL
                        photo_url = None
                        
                        # Способ 1: через style background-image
                        style = photo_wrap.get('style', '')
                        photo_url_match = re.search(r'background-image:url\(&quot;([^&]+)&quot;\)', style)
                        if photo_url_match:
                            photo_url = photo_url_match.group(1).replace('&amp;', '&')
                        
                        # Способ 2: через href атрибут
                        if not photo_url:
                            photo_url = photo_wrap.get('href')
                            if photo_url and photo_url.startswith('//'):
                                photo_url = 'https:' + photo_url
                        
                        # Способ 3: через img внутри
                        if not photo_url:
                            img_element = photo_wrap.find('img')
                            if img_element:
                                photo_url = img_element.get('src')
                                if photo_url and photo_url.startswith('//'):
                                    photo_url = 'https:' + photo_url
                        
                        if photo_url:
                            # Используем прямые ссылки на изображения Telegram
                            if photo_url.startswith('https://t.me/'):
                                # Извлекаем ID сообщения и создаем прямую ссылку
                                msg_id_match = re.search(r'/(\d+)(?:\?.*)?$', photo_url)
                                if msg_id_match:
                                    msg_id = msg_id_match.group(1)
                                    # Создаем прямую ссылку на изображение
                                    photo_url = f"https://t.me/nextgen_NFT/{msg_id}?single"
                            
                            media = {
                                'type': 'photo',
                                'url': photo_url,
                                'thumbnail': photo_url,
                                'width': None,
                                'height': None
                            }
                            logger.info(f"Found photo: {photo_url}")
                    
                    # Проверяем на видео - улучшенный парсинг
                    video_element = message.find('video')
                    if video_element:
                        video_url = video_element.get('src')
                        poster_url = video_element.get('poster')
                        
                        # Если нет poster, пробуем найти thumbnail
                        if not poster_url:
                            poster_element = video_element.find('img')
                            if poster_element:
                                poster_url = poster_element.get('src')
                        
                        if video_url:
                            if video_url.startswith('//'):
                                video_url = 'https:' + video_url
                            if poster_url and poster_url.startswith('//'):
                                poster_url = 'https:' + poster_url
                            
                            media = {
                                'type': 'video',
                                'url': video_url,
                                'thumbnail': poster_url,
                                'width': None,
                                'height': None
                            }
                            logger.info(f"Found video: {video_url}")
                    
                    # Проверяем на документы/файлы
                    document_wrap = message.find('a', class_='tgme_widget_message_document_wrap')
                    if document_wrap and not media:
                        doc_icon = document_wrap.find('i', class_='tgme_widget_message_document_icon')
                        if doc_icon:
                            media = {
                                'type': 'document',
                                'url': None,
                                'thumbnail': None,
                                'width': None,
                                'height': None
                            }
                    
                    # Генерируем заголовок из первых предложений
                    sentences = re.split(r'[.!?]+', full_text)
                    title = sentences[0][:150].strip() if sentences and sentences[0] else f"Пост от {channel_data['name']}"
                    
                    # Оценка времени чтения (200 слов в минуту)
                    word_count = len(full_text.split())
                    reading_time = max(1, word_count // 200)
                    
                    post = {
                        'id': hashlib.md5(f"{channel_data['username']}_{i}_{full_text[:50]}".encode()).hexdigest(),
                        'title': title,
                        'text': full_text,  # Полный текст без сокращений
                        'content_html': html_content,  # HTML контент для сохранения форматирования
                        'link': f"https://t.me/{channel_data['username']}",
                        'date': date,
                        'source': channel_data['name'],
                        'category': channel_data['category'],
                        'channel': channel_data['username'],
                        'media': media,
                        'reading_time': reading_time,
                        'word_count': word_count
                    }
                    
                    posts.append(post)
                    
                except Exception as e:
                    logger.warning(f"Error parsing message {i}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing HTML content: {e}")
        
        if not posts:  # Если парсинг не удался, используем мок данные
            return self._generate_mock_posts(channel_data)
        
        return posts

    def _generate_mock_posts(self, channel_data: Dict) -> List[Dict[str, Any]]:
        """Генерация мок данных для канала согласно ТЗ"""
        posts = []
        base_time = datetime.now()

        # Контент в зависимости от категории канала
        content_templates = {
            'gifts': [
                "🎁 Новые бесплатные подарки! Успейте получить эксклюзивные бонусы",
                "💝 Промокоды на скидки до 70%! Ограниченное предложение",
                "🎉 Розыгрыш ценных призов среди подписчиков канала",
                "🛍️ Лучшие предложения дня - не пропустите!"
            ],
            'crypto': [
                "📈 Анализ рынка: Bitcoin показывает рост на 5%",
                "💰 Новые возможности DeFi инвестиций - обзор проектов",
                "🚀 Перспективные альткоины для долгосрочных инвестиций",
                "⚡ Срочные новости: крупные движения на криптовалютном рынке"
            ],
            'nft': [
                "🖼️ Новая коллекция NFT от известного художника уже в продаже",
                "💎 Раритетные токены на аукционе - последний шанс приобрести",
                "🎨 Обзор лучших NFT художников недели",
                "📊 Статистика NFT рынка: рост объемов торгов на 15%"
            ],
            'tech': [
                "💻 Революционные технологии 2025 года - что нас ждет",
                "🔧 Обзор новейших гаджетов от мировых производителей",
                "🚀 Стартапы в сфере ИИ привлекли рекордные инвестиции",
                "📱 ТОП мобильных приложений для повышения продуктивности"
            ],
            'community': [
                "👥 Обсуждение актуальных тем в нашем сообществе",
                "💬 Важные новости и обновления для участников",
                "🔔 Анонс предстоящих мероприятий и встреч",
                "📢 Полезные советы и рекомендации от экспертов"
            ]
        }

        templates = content_templates.get(channel_data['category'], content_templates['community'])

        for i in range(5):  # Генерируем 5 постов
            post_time = base_time - timedelta(hours=i * 4 + hash(channel_data['username']) % 12)

            text = templates[i % len(templates)]
            title = text.split('.')[0][:80] + ("..." if len(text.split('.')[0]) > 80 else "")

            posts.append({
                'id': hashlib.md5(f"{channel_data['username']}_{i}_{text}".encode()).hexdigest(),
                'title': title,
                'text': text,
                'content_html': f"<p>{text}</p>",
                'link': f"https://t.me/{channel_data['username']}",
                'date': post_time.isoformat(),
                'source': channel_data['name'],
                'category': channel_data['category'],
                'channel': channel_data['username']
            })

        return posts
        """Автоматическая категоризация контента по ключевым словам"""
        content = (title + " " + description).lower()

        for category, keywords in self.keywords.items():
            if any(keyword in content for keyword in keywords):
                return category

        return 'general'

    async def fetch_rss_feed(self, source: Dict[str, str]) -> List[Dict[str, Any]]:
        """Получение новостей из RSS источника"""
        try:
            # Используем feedparser для парсинга RSS
            feed = feedparser.parse(source['url'])

            if not feed.entries:
                logger.warning(f"No entries found in RSS feed: {source['url']}")
                return []

            articles = []
            for entry in feed.entries[:10]:  # Берем только последние 10 новостей
                # Получаем описание из различных полей
                description = ""
                if hasattr(entry, 'summary'):
                    description = entry.summary
                elif hasattr(entry, 'description'):
                    description = entry.description
                elif hasattr(entry, 'content'):
                    description = entry.content[0].value if entry.content else ""

                # Очищаем HTML теги
                clean_description = re.sub(r'<[^>]+>', '', description)
                clean_description = clean_description[:200] + "..." if len(
                    clean_description) > 200 else clean_description

                # Получаем дату публикации
                pub_date = datetime.now()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    import time
                    pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    import time
                    pub_date = datetime.fromtimestamp(time.mktime(entry.updated_parsed))

                # Автоматическая категоризация
                auto_category = self.categorize_content(entry.title, clean_description)
                final_category = source.get('category', auto_category)

                # Извлекаем медиа контент
                media_list = []

                # Проверяем enclosures (вложения)
                if hasattr(entry, 'enclosures') and entry.enclosures:
                    for enclosure in entry.enclosures:
                        if hasattr(enclosure, 'type'):
                            if enclosure.type.startswith('image/'):
                                media_list.append({
                                    'type': 'photo',
                                    'url': enclosure.href,
                                    'thumbnail': enclosure.href
                                })
                            elif enclosure.type.startswith('video/'):
                                media_list.append({
                                    'type': 'video',
                                    'url': enclosure.href,
                                    'thumbnail': None
                                })

                # Проверяем media:content (альтернативный способ)
                if hasattr(entry, 'media_content') and entry.media_content:
                    for media_item in entry.media_content:
                        if media_item.get('type', '').startswith('image/'):
                            media_list.append({
                                'type': 'photo',
                                'url': media_item.get('url', ''),
                                'thumbnail': media_item.get('url', '')
                            })

                # Формируем HTML контент
                content_html = clean_description
                for media in media_list:
                    if media.get('type') == 'photo' and media.get('url'):
                        content_html += f'<br><img src="{media["url"]}" style="max-width:100%; height:auto; border-radius:8px; margin:10px 0;"/>'
                    elif media.get('type') == 'video' and media.get('url'):
                        thumbnail = media.get('thumbnail', '')
                        content_html += f'<br><video controls poster="{thumbnail}" style="max-width:100%; height:auto; border-radius:8px; margin:10px 0;">'
                        content_html += f'<source src="{media["url"]}" type="video/mp4">'
                        content_html += '</video>'

                article = {
                    'id': hashlib.md5((entry.link + entry.title).encode()).hexdigest(),
                    'title': entry.title,
                    'text': clean_description,  # Plain text
                    'content_html': content_html,  # HTML с медиа
                    'link': entry.link,
                    'date': pub_date.isoformat(),
                    'source': source['name'],
                    'category': final_category,
                    'channel': 'rss_' + source['name'].lower().replace(' ', '_'),
                    'media': media_list
                }

                articles.append(article)

            return articles

        except Exception as e:
            logger.error(f"Error fetching RSS feed {source['url']}: {e}")
            return []
        """Получить информацию о канале через Telegram API"""
        try:
            # В реальной реализации здесь будет вызов к Telegram Bot API
            # Пока возвращаем мок данные
            channel_data = next((ch for ch in self.channels if ch['username'] == username), None)
            if not channel_data:
                return None

            return {
                'username': username,
                'title': channel_data['name'],
                'description': f"Канал {channel_data['name']} - {channel_data['category']}",
                'subscribers_count': 1000 + hash(username) % 50000,  # Мок количества подписчиков
                'category': channel_data['category']
            }
        except Exception as e:
            logger.error(f"Error getting channel info for {username}: {e}")
            return None

    async def get_channel_posts(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить последние посты из канала"""
        try:
            # В реальной реализации здесь будет вызов к Telegram Bot API
            # Пока генерируем мок данные
            channel_data = next((ch for ch in self.channels if ch['username'] == username), None)
            if not channel_data:
                return []

            posts = []
            base_time = datetime.now()

            for i in range(limit):
                post_time = base_time - timedelta(hours=i * 2 + hash(username + str(i)) % 24)

                # Генерируем контент на основе категории
                if channel_data['category'] == 'gifts':
                    titles = [
                        f"🎁 Новые бесплатные подарки в {channel_data['name']}!",
                        f"💝 Эксклюзивные промокоды и скидки",
                        f"🎉 Розыгрыш призов для подписчиков",
                        f"🛍️ Лучшие предложения дня"
                    ]
                elif channel_data['category'] == 'crypto':
                    titles = [
                        f"📈 Анализ рынка криптовалют",
                        f"💰 Новые возможности для инвестиций",
                        f"🚀 Обзор перспективных проектов",
                        f"⚡ Быстрые новости из мира крипто"
                    ]
                elif channel_data['category'] == 'nft':
                    titles = [
                        f"🖼️ Новые NFT коллекции",
                        f"💎 Раритетные токены на аукционе",
                        f"🎨 Обзор NFT художников",
                        f"📊 Статистика NFT рынка"
                    ]
                elif channel_data['category'] == 'tech':
                    titles = [
                        f"💻 Новости технологий",
                        f"🔧 Обзор гаджетов",
                        f"🚀 Инновации в IT",
                        f"📱 Мобильные приложения"
                    ]
                else:
                    titles = [
                        f"📢 Новости от {channel_data['name']}",
                        f"ℹ️ Важные обновления",
                        f"📝 Полезная информация",
                        f"🔥 Горячие темы"
                    ]

                title = titles[i % len(titles)]

                posts.append({
                    'id': f"{username}_{i}",
                    'title': title,
                    'text': f"Интересный контент от канала {channel_data['name']}. Подписывайтесь для получения актуальных новостей!",
                    'date': post_time.isoformat(),
                    'views': 100 + hash(username + str(i)) % 5000,
                    'link': f"https://t.me/{username}",
                    'channel': username,
                    'category': channel_data['category']
                })

            return posts

        except Exception as e:
            logger.error(f"Error getting posts for {username}: {e}")
            return []

    async def get_all_news(self, category: str = 'all', limit: int = 50) -> List[Dict[str, Any]]:
        """
        Получить новости из всех источников согласно ТЗ:
        - Telegram каналы (основные источники)
        - RSS ленты (дополнительные источники)
        - Автоматическая категоризация и дедупликация
        """
        try:
            # Проверяем кэш
            cache_key = f"news_{category}_{limit}"
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if datetime.now() - cached_time < self.cache_ttl:
                    logger.info(f"Returning cached news for {category}, {len(cached_data)} items")
                    return cached_data

            all_posts = []

            # 1. Получаем данные из Telegram каналов (приоритетный источник согласно ТЗ)
            telegram_channels = self.channels
            if category != 'all':
                telegram_channels = [ch for ch in self.channels if ch['category'] == category]

            logger.info(f"Fetching from {len(telegram_channels)} Telegram channels")

            # Получаем посты из Telegram каналов
            telegram_tasks = []
            for channel in telegram_channels:
                telegram_tasks.append(self.fetch_telegram_channel(channel['username']))

            telegram_results = await asyncio.gather(*telegram_tasks, return_exceptions=True)

            for i, result in enumerate(telegram_results):
                if isinstance(result, list):
                    all_posts.extend(result)
                    logger.info(f"Got {len(result)} posts from {telegram_channels[i]['username']}")
                else:
                    logger.error(f"Error fetching posts from {telegram_channels[i]['username']}: {result}")

            # 2. Получаем данные из RSS источников (дополнительный источник)
            rss_sources = self.rss_sources
            if category != 'all':
                rss_sources = [src for src in self.rss_sources if src['category'] == category]

            logger.info(f"Fetching from {len(rss_sources)} RSS sources")

            # Получаем статьи из RSS
            rss_tasks = []
            for source in rss_sources:
                rss_tasks.append(self.fetch_rss_feed(source))

            rss_results = await asyncio.gather(*rss_tasks, return_exceptions=True)

            for i, result in enumerate(rss_results):
                if isinstance(result, list):
                    all_posts.extend(result)
                    logger.info(f"Got {len(result)} articles from {rss_sources[i]['name']}")
                else:
                    logger.error(f"Error fetching RSS from {rss_sources[i]['url']}: {result}")

            # 3. Обработка и дедупликация согласно ТЗ
            # Удаляем дубликаты по заголовку и ссылке
            seen = set()
            unique_posts = []
            for post in all_posts:
                # Создаем ключ для дедупликации
                title_clean = re.sub(r'[^\w\s]', '', post['title'].lower()).strip()
                key = (title_clean, post.get('link', ''))
                if key not in seen:
                    seen.add(key)
                    unique_posts.append(post)

            logger.info(f"After deduplication: {len(unique_posts)} unique posts from {len(all_posts)} total")

            # 4. Сортировка по дате (новые сначала)
            try:
                unique_posts.sort(
                    key=lambda x: datetime.fromisoformat(x['date'].replace('Z', '+00:00')),
                    reverse=True
                )
            except Exception as e:
                logger.warning(f"Error sorting by date: {e}, using original order")

            # 5. Ограничиваем количество согласно ТЗ
            final_posts = unique_posts[:limit]

            # 6. Сохраняем в кэш на 30 минут согласно ТЗ
            self.cache[cache_key] = (final_posts, datetime.now())

            logger.info(f"Returning {len(final_posts)} news items for category '{category}'")
            return final_posts

        except Exception as e:
            logger.error(f"Error in get_all_news: {e}")
            # В случае ошибки возвращаем данные из кэша, если есть
            cache_key = f"news_{category}_{limit}"
            if cache_key in self.cache:
                cached_data, _ = self.cache[cache_key]
                logger.info("Returning stale cached data due to error")
                return cached_data
            return []

            return final_posts

        except Exception as e:
            logger.error(f"Error getting all news: {e}")
            return []

    async def get_channels_info(self) -> List[Dict[str, Any]]:
        """Получить информацию о всех каналах"""
        try:
            tasks = []
            for channel in self.channels:
                tasks.append(self.get_channel_info(channel['username']))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            channels_info = []
            for result in results:
                if isinstance(result, dict):
                    channels_info.append(result)

            return channels_info

        except Exception as e:
            logger.error(f"Error getting channels info: {e}")
            return []

    async def update_news_async(self):
        """
        Асинхронное обновление новостей из всех источников
        Метод для периодического обновления в main.py
        """
        try:
            logger.info(f"Fetching from {len(self.channels)} Telegram channels")

            # Получаем новости из Telegram каналов
            all_posts = []
            for channel in self.channels:
                try:
                    posts = await self.fetch_telegram_channel(channel['username'])
                    logger.info(f"Got {len(posts)} posts from {channel['username']}")
                    all_posts.extend(posts)
                except Exception as e:
                    logger.error(f"Error fetching from channel {channel['username']}: {e}")
                    continue

            # Получаем новости из RSS источников
            logger.info(f"Fetching from {len(self.rss_sources)} RSS sources")
            for source in self.rss_sources:
                try:
                    articles = await self.fetch_rss_source(source['url'], source['name'], source['category'])
                    logger.info(f"Got {len(articles)} articles from {source['name']}")
                    all_posts.extend(articles)
                except Exception as e:
                    logger.error(f"Error fetching from RSS {source['name']}: {e}")
                    continue

            # Дедуплицируем по заголовкам
            unique_posts = []
            seen_titles = set()

            for post in all_posts:
                title_hash = hashlib.md5(post['title'].encode()).hexdigest()
                if title_hash not in seen_titles:
                    seen_titles.add(title_hash)
                    unique_posts.append(post)

            logger.info(f"After deduplication: {len(unique_posts)} unique posts from {len(all_posts)} total")

            # Сортируем по дате (новые сначала)
            try:
                unique_posts.sort(key=lambda x: x['date'], reverse=True)
            except Exception as e:
                logger.warning(f"Error sorting by date: {e}, using original order")

            # Сохраняем в базу данных
            await self.save_to_database(unique_posts[:50])  # Сохраняем только 50 самых свежих

            logger.info(f"Successfully updated {len(unique_posts[:50])} news items")

        except Exception as e:
            logger.error(f"Error in update_news_async: {e}")
            raise

    async def fetch_rss_source(self, url: str, name: str, category: str) -> List[Dict[str, Any]]:
        """Получение новостей из RSS источника"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to fetch RSS {url}, status: {response.status}")
                        return []

                    content = await response.text()
                    feed = feedparser.parse(content)

                    if not feed.entries:
                        logger.warning(f"No entries found in RSS feed: {url}")
                        return []

                    articles = []
                    for entry in feed.entries[:10]:  # Берем только 10 последних статей
                        # Извлекаем основную информацию
                        title = entry.get('title', 'Без заголовка')
                        description = entry.get('description', '') or entry.get('summary', '')
                        link = entry.get('link', '')
                        
                        # Пытаемся получить полный контент
                        full_content = entry.get('content', [{}])[0].get('value', '') if hasattr(entry, 'content') and entry.content else ''
                        if not full_content:
                            full_content = entry.get('content_encoded', '') if hasattr(entry, 'content_encoded') else ''
                        if not full_content:
                            # Пытаемся получить контент из других полей
                            full_content = getattr(entry, 'summary_detail', {}).get('value', '') if hasattr(entry, 'summary_detail') else ''
                        if not full_content:
                            full_content = description  # Fallback к описанию

                        # Парсим дату
                        date = datetime.now().isoformat()
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            try:
                                import time
                                date = datetime.fromtimestamp(time.mktime(entry.published_parsed)).isoformat()
                            except:
                                pass

                        # Извлекаем медиа контент
                        media = None

                        # Проверяем enclosures (вложения)
                        if hasattr(entry, 'enclosures') and entry.enclosures:
                            for enclosure in entry.enclosures:
                                if hasattr(enclosure, 'type'):
                                    if enclosure.type.startswith('image/'):
                                        media = {
                                            'type': 'photo',
                                            'url': enclosure.href,
                                            'thumbnail': enclosure.href
                                        }
                                        break
                                    elif enclosure.type.startswith('video/'):
                                        media = {
                                            'type': 'video',
                                            'url': enclosure.href,
                                            'thumbnail': None
                                        }
                                        break

                        # Проверяем media:content (альтернативный способ)
                        if not media and hasattr(entry, 'media_content') and entry.media_content:
                            for media_item in entry.media_content:
                                if media_item.get('type', '').startswith('image/'):
                                    media = {
                                        'type': 'photo',
                                        'url': media_item.get('url', ''),
                                        'thumbnail': media_item.get('url', '')
                                    }
                                    break

                        # Очищаем HTML теги из описания
                        import re
                        clean_description = re.sub(r'<[^>]+>', '', description)
                        # Убираем обрезку - оставляем полное описание
                        clean_description = clean_description.strip()

                        # Формируем HTML контент с полным текстом
                        # Очищаем контент от ссылок "Читать далее"
                        if full_content:
                            # Удаляем ссылки "Читать далее" и подобные
                            import re
                            patterns_to_remove = [
                                # Ссылки с текстом "Читать далее" (более точные)
                                r'<a[^>]*>Читать далее</a>',
                                r'<a[^>]*>читать далее</a>',
                                r'<a[^>]*>Read more</a>',
                                r'<a[^>]*>read more</a>',
                                
                                # Ссылки с #habracut в href (более точные)
                                r'<a[^>]*href="[^"]*#habracut"[^>]*>.*?</a>',
                                r'<a[^>]*href="[^"]*habracut"[^>]*>.*?</a>',
                                
                                # Ссылки с utm параметрами Habr (более точные)
                                r'<a[^>]*href="[^"]*utm_source=habrahabr[^"]*"[^>]*>.*?</a>',
                                r'<a[^>]*href="[^"]*utm_medium=rss[^"]*"[^>]*>.*?</a>',
                                
                                # Ссылки с любым текстом, содержащим "Читать далее"
                                r'<a[^>]*>.*?Читать далее.*?</a>',
                                r'<a[^>]*>.*?читать далее.*?</a>',
                                
                                # Простой текст (после удаления ссылок)
                                r'Читать далее',
                                r'читать далее',
                                r'Read more',
                                r'read more',
                                
                                # Хэштеги
                                r'#habracut',
                                r'habracut'
                            ]
                            
                            cleaned_content = full_content
                            for pattern in patterns_to_remove:
                                cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.IGNORECASE)
                            
                            # Дополнительная очистка: удаляем пустые параграфы
                            cleaned_content = re.sub(r'<p>\s*</p>', '', cleaned_content)
                            
                            # Удаляем множественные пробелы
                            cleaned_content = re.sub(r'\s+', ' ', cleaned_content)
                            
                            # Логируем для отладки
                            logger.info(f"Article '{title}': original length={len(full_content)}, cleaned length={len(cleaned_content)}")
                            
                            content_html = cleaned_content
                        else:
                            content_html = f"<p>{description}</p>"
                            logger.info(f"Article '{title}': using description as content_html")

                        # Формируем content из очищенного full_content
                        content_for_text = ''
                        if full_content:
                            # Очищаем HTML теги из full_content для content
                            content_for_text = re.sub(r'<[^>]+>', '', full_content)
                            content_for_text = re.sub(r'\s+', ' ', content_for_text).strip()
                            logger.info(f"Article '{title}': using full_content for text (length: {len(content_for_text)})")
                        else:
                            content_for_text = clean_description
                            logger.info(f"Article '{title}': using clean_description for text (length: {len(content_for_text)})")
                        
                        article = {
                            'id': hashlib.md5(f"{url}_{title}".encode()).hexdigest(),
                            'title': title,
                            'text': content_for_text,
                            'content_html': content_html,
                            'link': link,
                            'date': date,
                            'source': name,
                            'category': category,
                            'media': media
                        }

                        articles.append(article)

                    return articles

        except Exception as e:
            logger.error(f"Error fetching RSS from {url}: {e}")
            return []

    async def save_to_database(self, posts: List[Dict[str, Any]]):
        """Сохранение новостей в базу данных"""
        try:
            # Импортируем здесь, чтобы избежать циркулярного импорта
            import server.main as main_module
            from server.db import NewsItem

            if main_module.SessionLocal is None:
                logger.error("Database not initialized")
                return

            db = main_module.SessionLocal()

            try:
                news_items = []
                for post in posts:
                    # Получаем или создаём источник
                    from server.services.news_service import get_or_create_source
                    # Определяем тип источника и url
                    source_type = 'telegram' if post.get('channel') and not post.get('link', '').startswith('http') else 'rss'
                    source_url = post.get('link') or ''
                    category = post.get('category') or 'general'
                    source = get_or_create_source(db, post.get('source', 'unknown'), url=source_url, source_type=source_type, category=category)
                    # Проверяем, существует ли уже такая новость
                    existing = db.query(NewsItem).filter(
                        NewsItem.title == post['title']
                    ).first()

                    if existing:
                        continue  # Пропускаем дубликаты

                    # Извлекаем медиа данные
                    image_url = None
                    video_url = None
                    media_json = None

                    if post.get('media'):
                        media_json = post['media']  # Сохраняем полный JSON медиа
                        if post['media']['type'] == 'photo':
                            image_url = post['media']['url']
                        elif post['media']['type'] == 'video':
                            video_url = post['media']['url']
                            if not image_url and post['media'].get('thumbnail'):
                                image_url = post['media']['thumbnail']

                    # Получаем HTML контент если есть
                    content_html = post.get('content_html', '')
                    
                    # Оценка времени чтения (используем сохраненное значение или вычисляем)
                    reading_time = post.get('reading_time', 1)
                    if not reading_time:
                        word_count = len(post['text'].split()) if post.get('text') else 0
                        reading_time = max(1, word_count // 200)

                    news_item = NewsItem(
                        source_id=source.id,
                        title=post['title'],
                        content=post['text'],
                        content_html=content_html,  # Сохраняем HTML контент
                        link=post['link'],
                        publish_date=datetime.fromisoformat(post['date'].replace('Z', '+00:00')),
                        category=category,
                        media=media_json,  # Сохраняем JSON медиа
                        image_url=image_url,
                        video_url=video_url,
                        reading_time=reading_time,
                        views_count=0,
                        author=post.get('source'),
                        subtitle=None
                    )

                    news_items.append(news_item)

                if news_items:
                    db.bulk_save_objects(news_items)
                    db.commit()
                    logger.info(f"Saved {len(news_items)} new items to database")
                else:
                    logger.info("No new items to save")

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Ошибка при загрузке каналов: {e}")
            if 'db' in locals():
                db.rollback()
                db.close()
