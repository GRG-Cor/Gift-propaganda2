import feedparser
import logging
from sqlalchemy.orm import Session
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

async def fetch_rss_feeds(session: Session) -> List[Dict[str, Any]]:
    """Получение новостей из RSS источников"""
    try:
        logger.info("Fetching RSS feeds...")

        # Список RSS источников
        rss_sources = [
            {"url": "https://vc.ru/rss", "name": "VC.ru", "category": "tech"},
            {"url": "https://forklog.com/feed/", "name": "ForkLog", "category": "crypto"}
        ]

        articles = []
        for source in rss_sources:
            try:
                feed = feedparser.parse(source["url"])
                for entry in feed.entries[:5]:  # Берем только 5 последних
                    article = {
                        "title": entry.title,
                        "link": entry.link,
                        "description": getattr(entry, 'summary', ''),
                        "source": source["name"],
                        "category": source["category"]
                    }
                    articles.append(article)
            except Exception as e:
                logger.error(f"Error parsing RSS {source['url']}: {e}")

        logger.info(f"RSS feeds fetched successfully, {len(articles)} articles")
        return articles

    except Exception as e:
        logger.error(f"Error fetching RSS feeds: {e}")
        return []
