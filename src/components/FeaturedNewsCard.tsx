import React from 'react';
import styled from 'styled-components';
import { NewsItem } from '../types';
import { formatTimeAgo, isNewNews } from '../utils/formatters';
import { getNewsStyles } from '../utils/newsStyles';
import MediaViewer from './MediaViewer';

const FeaturedCard = styled.div<{ 
  $isNew?: boolean;
  $background: string;
  $textColor: string;
}>`
  background: ${props => props.$background};
  background-size: cover;
  background-position: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;

  ${props => props.$isNew && `
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 4px;
      height: 100%;
      background: #ffd700;
      z-index: 2;
      border-radius: 0 4px 4px 0;
    }
  `}

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
      radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
    pointer-events: none;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    
    /* Убираем висящую линию при hover */
    &::before {
      display: none;
    }
  }

  &:active {
    transform: translateY(0);
  }
`;

const FeaturedContent = styled.div`
  padding: 20px;
  position: relative;
  z-index: 1;
`;

const FeaturedHeader = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
`;

const FeaturedIcon = styled.div`
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
  min-width: 60px;
`;

const FeaturedText = styled.div`
  flex: 1;
  min-width: 0;
`;

const FeaturedTitle = styled.h3<{ $textColor: string }>`
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 700;
  line-height: 1.3;
  color: ${props => props.$textColor};
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const FeaturedPreview = styled.p<{ $subtitleColor: string }>`
  margin: 0 0 12px 0;
  font-size: 14px;
  line-height: 1.4;
  color: ${props => props.$subtitleColor};
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-weight: 500;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
`;

const FeaturedMetadata = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
`;

const FeaturedInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  flex-wrap: wrap;
`;

const FeaturedBadge = styled.span`
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const MetaItem = styled.span`
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
`;

const FeaturedMedia = styled.div`
  margin-top: 16px;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
`;

const StyledMediaViewer = styled(MediaViewer)`
  border-radius: 0;
`;

interface FeaturedNewsCardProps {
  news: NewsItem;
  onClick: (news: NewsItem) => void;
}

const FeaturedNewsCard: React.FC<FeaturedNewsCardProps> = ({ news, onClick }) => {
  const previewMedia = news.media && news.media.length > 0 ? news.media[0] : null;
  const styles = getNewsStyles(news);

  return (
    <FeaturedCard
      $isNew={isNewNews(news.publish_date)}
      $background={styles.background}
      $textColor={styles.textColor}
      onClick={() => onClick(news)}
    >
      <FeaturedContent>
        <FeaturedHeader>
          <FeaturedIcon>
            {styles.icon}
          </FeaturedIcon>
          
          <FeaturedText>
            <FeaturedTitle $textColor={styles.textColor}>{news.title}</FeaturedTitle>
            <FeaturedPreview $subtitleColor={styles.subtitleColor}>{news.content}</FeaturedPreview>
          </FeaturedText>
        </FeaturedHeader>

        <FeaturedMetadata>
          <FeaturedInfo>
            <FeaturedBadge>
              {news.category.toUpperCase()}
            </FeaturedBadge>
            <MetaItem>🕒 {formatTimeAgo(news.publish_date)}</MetaItem>
            {news.reading_time && (
              <MetaItem>📖 {news.reading_time} мин</MetaItem>
            )}
            {news.views_count !== undefined && (
              <MetaItem>👁️ {news.views_count}</MetaItem>
            )}
          </FeaturedInfo>
        </FeaturedMetadata>

        {previewMedia && (
          <FeaturedMedia>
            <StyledMediaViewer mediaItem={previewMedia} />
          </FeaturedMedia>
        )}
      </FeaturedContent>
    </FeaturedCard>
  );
};

export default FeaturedNewsCard; 