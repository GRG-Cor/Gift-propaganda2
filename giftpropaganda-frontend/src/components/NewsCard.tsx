import React from 'react';
import styled from 'styled-components';
import { NewsItem } from '../types';
import { formatTimeAgo, isNewNews } from '../utils/formatters';
import { getNewsStyles } from '../utils/newsStyles';
import MediaViewer from './MediaViewer';

const NewsCardContainer = styled.div<{ 
  $isNew?: boolean;
  $background: string;
  $textColor: string;
}>`
  background: ${props => props.$background};
  background-size: cover;
  background-position: center;
  border: 1px solid var(--tg-theme-hint-color, #333);
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;

  ${props => props.$isNew && `
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 3px;
      height: 100%;
      background: var(--tg-theme-button-color, #0088cc);
      z-index: 1;
      border-radius: 0 3px 3px 0;
    }
  `}

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    border-color: var(--tg-theme-button-color, #0088cc);
    
    /* Убираем висящую линию при hover */
    &::before {
      display: none;
    }
  }

  &:active {
    transform: translateY(0);
  }
`;

const NewsCardContent = styled.div`
  padding: 12px 14px;
  position: relative;
  z-index: 1;
  
  @media (min-width: 768px) {
    padding: 14px 16px;
  }
`;

const NewsHeader = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 10px;
  
  @media (min-width: 768px) {
    gap: 12px;
  }
`;

const NewsImagePreview = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  min-width: 50px;
  
  @media (min-width: 768px) {
    width: 60px;
    height: 60px;
    font-size: 24px;
    min-width: 60px;
  }
`;

const NewsTextContent = styled.div`
  flex: 1;
  min-width: 0;
`;

const NewsTitle = styled.h3<{ $textColor: string }>`
  margin: 0 0 6px 0;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.3;
  color: ${props => props.$textColor};
  white-space: pre-wrap;
  word-wrap: break-word;
  
  @media (min-width: 768px) {
    font-size: 15px;
  }
`;

const NewsPreview = styled.p<{ $subtitleColor: string }>`
  margin: 0 0 8px 0;
  font-size: 13px;
  line-height: 1.4;
  color: ${props => props.$subtitleColor};
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  white-space: pre-wrap;
  word-wrap: break-word;
`;

const NewsMetadata = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 8px;
`;

const NewsInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
  flex-wrap: wrap;
`;

const CategoryBadge = styled.span<{ $category: string }>`
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  white-space: nowrap;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const MetaItem = styled.span`
  display: flex;
  align-items: center;
  gap: 3px;
  white-space: nowrap;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
`;

const InteractionBar = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
`;

const InteractionButton = styled.button`
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  font-size: 11px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 0;
  transition: color 0.2s ease;

  &:hover {
    color: #ffffff;
  }
`;

const MediaContainer = styled.div`
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;
`;

interface NewsCardProps {
  news: NewsItem;
  onClick: (news: NewsItem) => void;
}

const NewsCard: React.FC<NewsCardProps> = ({ news, onClick }) => {
  const previewMedia = news.media && news.media.length > 0 ? news.media[0] : null;
  const styles = getNewsStyles(news);
  
  // Функция для создания короткого превью контента
  const getContentPreview = (content: string, maxLength: number = 150) => {
    if (!content) return '';
    
    // Убираем HTML теги и лишние пробелы
    const cleanContent = content.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
    
    if (cleanContent.length <= maxLength) {
      return cleanContent;
    }
    
    // Обрезаем до последнего полного слова
    const truncated = cleanContent.substring(0, maxLength);
    const lastSpaceIndex = truncated.lastIndexOf(' ');
    
    if (lastSpaceIndex > maxLength * 0.8) {
      return truncated.substring(0, lastSpaceIndex) + '...';
    }
    
    return truncated + '...';
  };

  return (
    <NewsCardContainer
      $isNew={isNewNews(news.publish_date)}
      $background={styles.background}
      $textColor={styles.textColor}
      onClick={() => onClick(news)}
    >
      {previewMedia && (
        <MediaContainer>
          <MediaViewer mediaItem={previewMedia} />
        </MediaContainer>
      )}

      <NewsCardContent>
        <NewsHeader>
          <NewsImagePreview>
            <div style={{
              width: '100%',
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              borderRadius: '6px'
            }}>
              {styles.icon}
            </div>
          </NewsImagePreview>
          
          <NewsTextContent>
            <NewsTitle $textColor={styles.textColor}>{news.title}</NewsTitle>
            <NewsPreview $subtitleColor={styles.subtitleColor}>{getContentPreview(news.content)}</NewsPreview>
          </NewsTextContent>
        </NewsHeader>

        <NewsMetadata>
          <NewsInfo>
            <CategoryBadge $category={news.category}>
              {news.category.toUpperCase()}
            </CategoryBadge>
            <MetaItem>🕒 {formatTimeAgo(news.publish_date)}</MetaItem>
            {news.reading_time && (
              <MetaItem>📖 {news.reading_time} мин</MetaItem>
            )}
            {news.views_count !== undefined && (
              <MetaItem>👁️ {news.views_count}</MetaItem>
            )}
          </NewsInfo>
          
          <InteractionBar>
            <InteractionButton>🔥</InteractionButton>
            <InteractionButton>💬</InteractionButton>
            <InteractionButton>🔖</InteractionButton>
          </InteractionBar>
        </NewsMetadata>
      </NewsCardContent>
    </NewsCardContainer>
  );
};

export default NewsCard; 