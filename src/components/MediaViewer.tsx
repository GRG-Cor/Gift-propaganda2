import React, { useState } from 'react';
import styled from 'styled-components';
import { MediaItem } from '../types';

const MediaContainer = styled.div`
  position: relative;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  background: var(--tg-theme-secondary-bg-color, #1a1a1a);
  margin-bottom: 16px;
`;

const MediaImage = styled.img<{ $hasVideo?: boolean }>`
  width: 100%;
  height: auto;
  max-height: 400px;
  object-fit: cover;
  cursor: ${props => props.$hasVideo ? 'pointer' : 'default'};
  transition: transform 0.2s ease;
  display: block;

  &:hover {
    transform: ${props => props.$hasVideo ? 'scale(1.02)' : 'none'};
  }
`;

const VideoElement = styled.video`
  width: 100%;
  height: auto;
  max-height: 400px;
  background: #000;
  display: block;
`;

const PlayButton = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 50px;
  height: 50px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(4px);

  &:hover {
    background: rgba(0, 0, 0, 0.8);
    transform: translate(-50%, -50%) scale(1.1);
  }

  &::before {
    content: '▶️';
    font-size: 18px;
    margin-left: 2px;
  }
`;

const MediaType = styled.div`
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  backdrop-filter: blur(4px);
`;

const ErrorPlaceholder = styled.div`
  width: 100%;
  height: 120px;
  background: var(--tg-theme-hint-color, #333);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--tg-theme-text-color, #ffffff);
  font-size: 14px;
  border-radius: 8px;
`;

interface MediaViewerProps {
  mediaItem: MediaItem;
  className?: string;
}

const MediaViewer: React.FC<MediaViewerProps> = ({
  mediaItem,
  className
}) => {
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const [mediaError, setMediaError] = useState(false);

  const handlePlayVideo = () => {
    setIsVideoPlaying(true);
  };

  const handleMediaError = () => {
    setMediaError(true);
  };

  if (mediaError) {
    return (
      <MediaContainer className={className}>
        <ErrorPlaceholder>
          {mediaItem.type === 'photo' ? '📷 Изображение недоступно' : '🎬 Видео недоступно'}
        </ErrorPlaceholder>
      </MediaContainer>
    );
  }

  if (mediaItem.type === 'video' && isVideoPlaying) {
    return (
      <MediaContainer className={className}>
        <VideoElement
          controls
          autoPlay
          poster={mediaItem.thumbnail}
          onError={handleMediaError}
        >
          <source src={mediaItem.url} type="video/mp4" />
          <source src={mediaItem.url} type="video/webm" />
          Ваш браузер не поддерживает воспроизведение видео.
        </VideoElement>
        <MediaType>📹 ВИДЕО</MediaType>
      </MediaContainer>
    );
  }

  if (mediaItem.type === 'photo') {
    return (
      <MediaContainer className={className}>
        <MediaImage
          src={mediaItem.url}
          alt="Media content"
          onError={handleMediaError}
        />
        <MediaType>📷 ФОТО</MediaType>
      </MediaContainer>
    );
  }

  if (mediaItem.type === 'video') {
    return (
      <MediaContainer className={className}>
        {mediaItem.thumbnail ? (
          <>
            <MediaImage
              src={mediaItem.thumbnail}
              alt="Video thumbnail"
              $hasVideo={true}
              onError={handleMediaError}
              onClick={handlePlayVideo}
            />
            <PlayButton onClick={handlePlayVideo} />
          </>
        ) : (
          <div onClick={handlePlayVideo} style={{ cursor: 'pointer', padding: '20px', textAlign: 'center' }}>
            Нажмите для воспроизведения видео
          </div>
        )}
        <MediaType>📹 ВИДЕО</MediaType>
      </MediaContainer>
    );
  }

  return null;
};

export default MediaViewer;