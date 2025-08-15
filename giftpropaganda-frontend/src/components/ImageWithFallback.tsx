import React, { useState } from 'react';
import styled from 'styled-components';

interface ImageWithFallbackProps {
    src: string;
    alt?: string;
    className?: string;
    onLoad?: () => void;
    onError?: () => void;
}

const StyledImage = styled.img<{ $isLoading: boolean; $hasError: boolean }>`
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    margin: 16px 0;
    display: block;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    transition: transform 0.2s ease;
    opacity: ${props => props.$isLoading ? 0.5 : props.$hasError ? 0 : 1};
    
    &:hover {
        transform: scale(1.02);
    }
`;

const LoadingPlaceholder = styled.div`
    width: 100%;
    height: 200px;
    background: linear-gradient(90deg, #2a2a2a 25%, #3a3a3a 50%, #2a2a2a 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
    border-radius: 8px;
    margin: 16px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--tg-theme-hint-color, #888);
    font-size: 14px;
    
    @keyframes loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
`;

const ErrorPlaceholder = styled.div`
    width: 100%;
    height: 200px;
    background: var(--tg-theme-secondary-bg-color, #1a1a1a);
    border: 2px dashed var(--tg-theme-hint-color, #333);
    border-radius: 8px;
    margin: 16px 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--tg-theme-hint-color, #888);
    font-size: 14px;
    text-align: center;
    
    .icon {
        font-size: 24px;
        margin-bottom: 8px;
    }
    
    .retry-button {
        margin-top: 8px;
        padding: 4px 12px;
        background: var(--tg-theme-button-color, #0088cc);
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        
        &:hover {
            opacity: 0.8;
        }
    }
`;

const ImageWithFallback: React.FC<ImageWithFallbackProps> = ({
    src,
    alt = '',
    className,
    onLoad,
    onError
}) => {
    const [isLoading, setIsLoading] = useState(true);
    const [hasError, setHasError] = useState(false);
    const [retryCount, setRetryCount] = useState(0);

    // Добавляем отладочные логи
    console.log('🔍 ImageWithFallback рендерится');
    console.log('🔍 src:', src);
    console.log('🔍 alt:', alt);
    console.log('🔍 isLoading:', isLoading);
    console.log('🔍 hasError:', hasError);
    console.log('🔍 retryCount:', retryCount);

    const handleLoad = () => {
        setIsLoading(false);
        setHasError(false);
        onLoad?.();
        console.log('✅ Изображение загружено:', src);
    };

    const handleError = () => {
        setIsLoading(false);
        setHasError(true);
        onError?.();
        console.log('❌ Ошибка загрузки изображения:', src);
    };

    const handleRetry = () => {
        setRetryCount(prev => prev + 1);
        setIsLoading(true);
        setHasError(false);
    };

    // Если изображение недоступно после 3 попыток, показываем заглушку
    if (hasError && retryCount >= 3) {
        return (
            <ErrorPlaceholder>
                <div className="icon">🖼️</div>
                <div>Изображение недоступно</div>
                <div style={{ fontSize: '12px', marginTop: '4px' }}>
                    {src.includes('cointelegraph.com') ? 'CORS ограничения' : 'Сетевая ошибка'}
                </div>
                <button className="retry-button" onClick={handleRetry}>
                    Попробовать снова
                </button>
            </ErrorPlaceholder>
        );
    }

    // Если загружается, показываем индикатор
    if (isLoading) {
        return (
            <LoadingPlaceholder>
                Загрузка изображения...
            </LoadingPlaceholder>
        );
    }

    return (
        <StyledImage
            src={src}
            alt={alt}
            className={className}
            $isLoading={isLoading}
            $hasError={hasError}
            onLoad={handleLoad}
            onError={handleError}
        />
    );
};

export default ImageWithFallback; 