import React, { useState } from 'react';
import styled from 'styled-components';
import { NewsItem } from '../types';
import { formatDate } from '../utils/formatters';
import HtmlContent from './HtmlContent';
import MediaViewer from './MediaViewer';

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
`;

const ModalContent = styled.div`
  background: var(--tg-theme-bg-color, #1a1a1a);
  border-radius: 16px;
  max-width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  width: 100%;
  
  @media (min-width: 768px) {
    width: 600px;
  }
`;

const ModalHeader = styled.div`
  padding: 20px 20px 0 20px;
  position: sticky;
  top: 0;
  background: var(--tg-theme-bg-color, #1a1a1a);
  z-index: 10;
`;

const CloseButton = styled.button`
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  color: var(--tg-theme-hint-color, #999);
  font-size: 24px;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
  
  &:hover {
    background: var(--tg-theme-secondary-bg-color, #333);
  }
`;

const Title = styled.h1`
  margin: 0 0 12px 0;
  font-size: 20px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--tg-theme-text-color, #ffffff);
  padding-right: 40px;
`;

const MetaInfo = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
  font-size: 14px;
  color: var(--tg-theme-hint-color, #999);
`;

const MetaItem = styled.span`
  display: flex;
  align-items: center;
  gap: 4px;
`;

const CategoryBadge = styled.span<{ category: string }>`
  background: ${props => {
    switch (props.category) {
      case 'gifts': return 'linear-gradient(135deg, #ff6b6b, #ff8e8e)';
      case 'crypto': return 'linear-gradient(135deg, #4ecdc4, #44a08d)';
      case 'nft': return 'linear-gradient(135deg, #a8edea, #fed6e3)';
      case 'tech': return 'linear-gradient(135deg, #667eea, #764ba2)';
      case 'community': return 'linear-gradient(135deg, #f093fb, #f5576c)';
      default: return 'linear-gradient(135deg, #667eea, #764ba2)';
    }
  }};
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
`;

const ModalBody = styled.div`
  padding: 0 20px 20px 20px;
`;

const Content = styled.div`
  line-height: 1.6;
  color: var(--tg-theme-text-color, #ffffff);
  margin-bottom: 20px;
`;

const SourceLink = styled.a`
  color: var(--tg-theme-link-color, #0088cc);
  text-decoration: none;
  font-weight: 500;
  
  &:hover {
    text-decoration: underline;
  }
`;

const PublishButton = styled.button<{ isPublished: boolean }>`
  background: ${props => props.isPublished 
    ? 'var(--tg-theme-secondary-bg-color, #333)' 
    : 'var(--tg-theme-button-color, #0088cc)'};
  color: var(--tg-theme-button-text-color, #ffffff);
  border: none;
  border-radius: 8px;
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: ${props => props.isPublished ? 'default' : 'pointer'};
  opacity: ${props => props.isPublished ? 0.6 : 1};
  transition: all 0.2s ease;
  width: 100%;
  margin-top: 16px;
  
  &:hover:not(:disabled) {
    opacity: 0.8;
  }
  
  &:disabled {
    cursor: not-allowed;
  }
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

interface NewsModalProps {
  news: NewsItem;
  isOpen: boolean;
  onClose: () => void;
}

const NewsModal: React.FC<NewsModalProps> = ({ news, isOpen, onClose }) => {
  const [isPublishing, setIsPublishing] = useState(false);
  const [isPublished, setIsPublished] = useState(false);

  if (!isOpen) return null;

  const handlePublish = async () => {
    if (isPublished || isPublishing) return;
    
    setIsPublishing(true);
    try {
      const response = await fetch(`/api/news/${news.id}/publish`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const result = await response.json();
        setIsPublished(true);
        // Можно показать уведомление об успешной публикации
        console.log('Новость опубликована:', result);
      } else {
        const error = await response.json();
        console.error('Ошибка публикации:', error);
        // Можно показать уведомление об ошибке
      }
    } catch (error) {
      console.error('Ошибка при публикации:', error);
    } finally {
      setIsPublishing(false);
    }
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <ModalOverlay onClick={handleOverlayClick}>
      <ModalContent>
        <ModalHeader>
          <CloseButton onClick={onClose}>&times;</CloseButton>
          <Title>{news.title}</Title>
          <MetaInfo>
            <MetaItem>
              📅 {formatDate(news.publish_date)}
            </MetaItem>
            {news.category && (
              <CategoryBadge category={news.category}>
                {news.category}
              </CategoryBadge>
            )}
            {news.reading_time && (
              <MetaItem>
                ⏱️ {news.reading_time} мин
              </MetaItem>
            )}
            {news.views_count && (
              <MetaItem>
                👀 {news.views_count}
              </MetaItem>
            )}
            {news.author && (
              <MetaItem>
                👤 {news.author}
              </MetaItem>
            )}
          </MetaInfo>
        </ModalHeader>
        
        <ModalBody>
          {news.media && news.media.length > 0 && (
            <MediaViewer media={news.media} />
          )}
          
          <Content>
            {news.content_html ? (
              <HtmlContent content={news.content_html} />
            ) : (
              <p>{news.content}</p>
            )}
          </Content>
          
          {news.link && (
            <SourceLink href={news.link} target="_blank" rel="noopener noreferrer">
              📰 Читать источник
            </SourceLink>
          )}
          
          <PublishButton 
            isPublished={isPublished}
            onClick={handlePublish}
            disabled={isPublishing || isPublished}
          >
            {isPublishing && <LoadingSpinner />}
            {isPublished 
              ? '✅ Опубликовано в канал' 
              : isPublishing 
                ? 'Публикация...' 
                : '📢 Опубликовать в канал'
            }
          </PublishButton>
        </ModalBody>
      </ModalContent>
    </ModalOverlay>
  );
};

export default NewsModal;
