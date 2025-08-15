import React from 'react';
import styled from 'styled-components';
import ImageWithFallback from './ImageWithFallback';
import { extractImagesFromHtml, processHtmlContent } from '../utils/htmlSanitizer';

interface HtmlContentProps {
    html: string;
    className?: string;
}

const ContentContainer = styled.div`
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

    a {
        color: var(--tg-theme-button-color, #0088cc);
        text-decoration: none;
        
        &:hover {
            text-decoration: underline;
        }
    }
`;

const HtmlContent: React.FC<HtmlContentProps> = ({ html, className }) => {
    if (!html) return null;

    // Добавляем отладочные логи
    console.log('🔍 HtmlContent рендерится');
    console.log('🔍 HTML вход:', html);
    console.log('🔍 HTML длина:', html.length);

    // Извлекаем изображения из HTML
    const images = extractImagesFromHtml(html);
    console.log('🔍 Извлеченные изображения:', images);
    
    // Создаем HTML без изображений (они будут отображаться отдельно)
    const htmlWithoutImages = html.replace(/<img[^>]+>/gi, '');
    console.log('🔍 HTML без изображений:', htmlWithoutImages);
    
    // Обрабатываем HTML
    const processedHtml = processHtmlContent(htmlWithoutImages);
    console.log('🔍 Обработанный HTML:', processedHtml);

    return (
        <ContentContainer className={className}>
            {/* Отображаем изображения отдельно */}
            {images.map((image, index) => {
                console.log(`🔍 Рендерим изображение ${index + 1}:`, image);
                return (
                    <ImageWithFallback
                        key={`image-${index}`}
                        src={image.src}
                        alt={image.alt}
                    />
                );
            })}
            
            {/* Отображаем остальной HTML контент */}
            <div 
                dangerouslySetInnerHTML={{ __html: processedHtml }}
            />
        </ContentContainer>
    );
};

export default HtmlContent; 