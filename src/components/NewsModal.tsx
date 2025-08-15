import React, { useEffect } from 'react';
import styled from 'styled-components';
import MediaViewer from './MediaViewer';
import TelegramWebApp from '../telegram/TelegramWebApp';
import DOMPurify from 'dompurify';
import { NewsItem } from '../types';
import { formatTimeAgo } from '../utils/formatters';

interface NewsModalProps {
    news: NewsItem;
    isOpen: boolean;
    onClose: () => void;
}

const ModalOverlay = styled.div<{ $isOpen: boolean }>`
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.9);
    backdrop-filter: blur(10px);
    z-index: 1000;
    opacity: ${props => props.$isOpen ? 1 : 0};
    visibility: ${props => props.$isOpen ? 'visible' : 'hidden'};
    transition: all 0.3s ease;
`;

const ModalContainer = styled.div<{ $isOpen: boolean }>`
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    background: var(--tg-theme-bg-color, #0f0f0f);
    color: var(--tg-theme-text-color, #ffffff);
    transform: translateY(${props => props.$isOpen ? '0' : '100%'});
    transition: transform 0.3s ease;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
`;

const ModalHeader = styled.div`
    position: sticky;
    top: 0;
    background: var(--tg-theme-bg-color, #0f0f0f);
    padding: 12px 16px;
    border-bottom: 1px solid var(--tg-theme-hint-color, #333);
    backdrop-filter: blur(10px);
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: space-between;
`;

const BackButton = styled.button`
    background: none;
    border: none;
    color: var(--tg-theme-button-color, #0088cc);
    font-size: 16px;
    cursor: pointer;
    padding: 8px;
    margin: -8px;
    border-radius: 6px;
    transition: background 0.2s ease;

    &:hover {
        background: var(--tg-theme-secondary-bg-color, #1a1a1a);
    }
`;

const ShareButton = styled.button`
    background: none;
    border: none;
    color: var(--tg-theme-text-color, #ffffff);
    font-size: 16px;
    cursor: pointer;
    padding: 8px;
    margin: -8px;
    border-radius: 6px;
    transition: background 0.2s ease;

    &:hover {
        background: var(--tg-theme-secondary-bg-color, #1a1a1a);
    }
`;

const ModalContent = styled.div`
    flex: 1;
    padding: 0 16px 40px 16px;
    max-width: 800px;
    margin: 0 auto;
    width: 100%;
`;

const ArticleHeader = styled.div`
    margin: 20px 0;
`;

const CategoryBadge = styled.span`
    display: inline-block;
    padding: 4px 8px;
    background: var(--tg-theme-button-color, #0088cc);
    color: var(--tg-theme-button-text-color, #ffffff);
    border-radius: 4px;
    font-size: 11px;
    font-weight: 500;
    margin-bottom: 12px;
`;

const ArticleTitle = styled.h1`
    font-size: 24px;
    font-weight: 700;
    line-height: 1.3;
    margin: 0 0 16px 0;
    color: var(--tg-theme-text-color, #ffffff);
`;

const ArticleSubtitle = styled.p`
    font-size: 16px;
    line-height: 1.5;
    color: var(--tg-theme-hint-color, #999);
    margin: 0 0 20px 0;
`;

const ArticleMeta = styled.div`
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
    font-size: 13px;
    color: var(--tg-theme-hint-color, #888);
    flex-wrap: wrap;
`;

const MetaItem = styled.span`
    display: flex;
    align-items: center;
    gap: 4px;
`;

const ArticleContent = styled.div`
    font-size: 16px;
    line-height: 1.6;
    color: var(--tg-theme-text-color, #ffffff);

    p {
        margin: 0 0 16px 0;
    }

    h2, h3, h4 {
        margin: 24px 0 12px 0;
        color: var(--tg-theme-text-color, #ffffff);
    }

    ul, ol {
        margin: 0 0 16px 0;
        padding-left: 20px;
    }

    blockquote {
        margin: 16px 0;
        padding: 12px 16px;
        background: var(--tg-theme-secondary-bg-color, #1a1a1a);
        border-left: 4px solid var(--tg-theme-button-color, #0088cc);
        border-radius: 0 4px 4px 0;
    }

    code {
        background: var(--tg-theme-secondary-bg-color, #1a1a1a);
        padding: 2px 4px;
        border-radius: 4px;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 14px;
    }
`;

const InteractionBar = styled.div`
    margin-top: 32px;
    padding: 16px 0;
    border-top: 1px solid var(--tg-theme-hint-color, #333);
    display: flex;
    align-items: center;
    justify-content: space-between;
`;

const InteractionButtons = styled.div`
    display: flex;
    gap: 20px;
`;

const InteractionButton = styled.button`
    background: none;
    border: none;
    color: var(--tg-theme-hint-color, #888);
    font-size: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    border-radius: 6px;
    transition: all 0.2s ease;

    &:hover {
        background: var(--tg-theme-secondary-bg-color, #1a1a1a);
        color: var(--tg-theme-text-color, #ffffff);
    }

    &.active {
        color: var(--tg-theme-button-color, #0088cc);
    }
`;

const ReadOriginalButton = styled.a`
    background: var(--tg-theme-button-color, #0088cc);
    color: var(--tg-theme-button-text-color, #ffffff);
    text-decoration: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    transition: opacity 0.2s ease;

    &:hover {
        opacity: 0.8;
    }
`;

const DescriptionSection = styled.div`
    margin: 24px 0;
    padding: 20px;
    background: var(--tg-theme-secondary-bg-color, #1a1a1a);
    border-radius: 12px;
    border: 1px solid var(--tg-theme-hint-color, #333);
`;

const DescriptionTitle = styled.h3`
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 16px 0;
    color: var(--tg-theme-text-color, #ffffff);
`;

const LinksContainer = styled.div`
    display: flex;
    flex-direction: column;
    gap: 12px;
`;

const LinkItem = styled.a`
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--tg-theme-button-color, #0088cc);
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    padding: 8px 12px;
    background: rgba(0, 136, 204, 0.1);
    border-radius: 8px;
    transition: all 0.2s ease;

    &:hover {
        background: rgba(0, 136, 204, 0.2);
        transform: translateY(-1px);
    }
`;

const LinkIcon = styled.span`
    font-size: 16px;
`;

const LinkText = styled.span`
    flex: 1;
`;

const HighlightText = styled.span`
    color: #ff6b6b;
    font-weight: 600;
`;

const ImportantNotice = styled.div`
    margin-top: 16px;
    padding: 12px;
    background: rgba(255, 107, 107, 0.1);
    border: 1px solid rgba(255, 107, 107, 0.3);
    border-radius: 8px;
    font-size: 14px;
    line-height: 1.5;
    color: var(--tg-theme-text-color, #ffffff);
`;

const SourceInfo = styled.div`
  margin-top: 20px;
  font-size: 14px;
  color: var(--tg-theme-hint-color, #888);
`;

const NewsModal: React.FC<NewsModalProps> = ({news, isOpen, onClose}) => {
    // Отладочная информация
    useEffect(() => {
        if (isOpen) {
            console.log('=== NEWS MODAL DEBUG ===');
            console.log('news object:', news);
            console.log('content_html exists:', !!news.content_html);
            console.log('content_html value:', news.content_html);
            console.log('content value:', news.content);
            console.log('========================');
        }
    }, [isOpen, news]);

    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
            TelegramWebApp.expand();
        } else {
            document.body.style.overflow = 'auto';
        }

        return () => {
            document.body.style.overflow = 'auto';
        };
    }, [isOpen]);

    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape') {
                onClose();
            }
        };

        if (isOpen) {
            document.addEventListener('keydown', handleEscape);
        }

        return () => {
            document.removeEventListener('keydown', handleEscape);
        };
    }, [isOpen, onClose]);

    const handleBackClick = () => {
        TelegramWebApp.triggerHapticFeedback('impact');
        onClose();
    };

    const handleShare = () => {
        TelegramWebApp.triggerHapticFeedback('impact');
        if (navigator.share) {
            navigator.share({
                title: news.title,
                text: news.content.substring(0, 200) + '...',
                url: news.link
            });
        }
    };

    const handleInteraction = (type: string) => {
        TelegramWebApp.triggerHapticFeedback('impact');
    };

    const createMarkup = (html: string) => {
        return {
            __html: DOMPurify.sanitize(html, {
                ADD_TAGS: ['iframe'],
                ADD_ATTR: ['allow', 'allowfullscreen', 'frameborder', 'scrolling']
            })
        };
    };

    return (
        <ModalOverlay $isOpen={isOpen} onClick={onClose}>
            <ModalContainer $isOpen={isOpen} onClick={(e) => e.stopPropagation()}>
                <ModalHeader>
                    <BackButton onClick={handleBackClick}>← Назад</BackButton>
                    <ShareButton onClick={handleShare}>📤</ShareButton>
                </ModalHeader>

                <ModalContent>
                    <ArticleHeader>
                        <CategoryBadge>{news.category.toUpperCase()}</CategoryBadge>
                        <ArticleTitle>{news.title}</ArticleTitle>
                        {news.subtitle && <ArticleSubtitle>{news.subtitle}</ArticleSubtitle>}

                        <ArticleMeta>
                            {news.author && <MetaItem>👤 {news.author}</MetaItem>}
                            <MetaItem>🕒 {formatTimeAgo(news.publish_date)}</MetaItem>
                            {news.reading_time && (
                                <MetaItem>📖 {news.reading_time} мин чтения</MetaItem>
                            )}
                            {news.views_count !== undefined && (
                                <MetaItem>👁️ {news.views_count} просмотров</MetaItem>
                            )}
                        </ArticleMeta>
                    </ArticleHeader>

                    {news.media && news.media.length > 0 && (
                        <div style={{ marginBottom: '20px' }}>
                            {news.media.map((mediaItem, index) => (
                                <MediaViewer key={index} mediaItem={mediaItem}/>
                            ))}
                        </div>
                    )}

                    {news.content_html ? (
                        <ArticleContent dangerouslySetInnerHTML={createMarkup(news.content_html)}/>
                    ) : news.content ? (
                        <ArticleContent>
                            <p>{news.content}</p>
                        </ArticleContent>
                    ) : (
                        <ArticleContent>
                            <p>Контент недоступен</p>
                        </ArticleContent>
                    )}

                    {/* Описание с ссылками */}
                    <DescriptionSection>
                        <DescriptionTitle>📋 Полезные ссылки</DescriptionTitle>
                        
                        <LinksContainer>
                            <LinkItem href="https://t.me/source" target="_blank" rel="noopener noreferrer">
                                <LinkIcon>💡</LinkIcon>
                                <LinkText>Источник</LinkText>
                            </LinkItem>
                            
                            <LinkItem href="https://t.me/nft_chat" target="_blank" rel="noopener noreferrer">
                                <LinkIcon>🚀</LinkIcon>
                                <LinkText>Чат для покупки/продажи NFT</LinkText>
                            </LinkItem>
                            
                            <LinkItem href="https://t.me/portals" target="_blank" rel="noopener noreferrer">
                                <LinkIcon>❤️</LinkIcon>
                                <LinkText>Portals ❤️</LinkText>
                            </LinkItem>
                        </LinksContainer>

                        <ImportantNotice>
                            <HighlightText>‼️ На Portals теперь доступны розыгрыши!</HighlightText>
                            <br />
                            Запустить розыгрыш вы можете перейдя во вкладку профиль, а потом giveaways.
                        </ImportantNotice>
                    </DescriptionSection>

                    {news.source?.name && (
                        <SourceInfo>
                            Источник:{" "}
                            {news.source?.name}
                        </SourceInfo>
                    )}

                    <InteractionBar>
                        <InteractionButtons>
                            <InteractionButton onClick={() => handleInteraction('like')}>
                                🔥 +2
                            </InteractionButton>
                            <InteractionButton onClick={() => handleInteraction('comment')}>
                                💬 0
                            </InteractionButton>
                            <InteractionButton onClick={() => handleInteraction('bookmark')}>
                                🔖 3
                            </InteractionButton>
                        </InteractionButtons>

                        <ReadOriginalButton
                            href={news.link}
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            Читать оригинал 🔗
                        </ReadOriginalButton>
                    </InteractionBar>
                </ModalContent>
            </ModalContainer>
        </ModalOverlay>
    );
};

export default NewsModal;
