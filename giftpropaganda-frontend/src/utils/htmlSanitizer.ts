/**
 * Собственная функция очистки HTML без DOMPurify
 */

export const sanitizeHtml = (html: string): string => {
    if (!html) return '';
    
    let cleanedHtml = html;
    
    // Удаляем потенциально опасные теги и атрибуты
    const dangerousTags = [
        'script', 'iframe', 'object', 'embed', 'form', 'input', 'button', 'select', 'textarea'
    ];
    
    dangerousTags.forEach(tag => {
        const regex = new RegExp(`<${tag}[^>]*>.*?</${tag}>|<${tag}[^>]*/?>`, 'gi');
        cleanedHtml = cleanedHtml.replace(regex, '');
    });
    
    // Удаляем опасные атрибуты
    const dangerousAttrs = [
        'onclick', 'onload', 'onerror', 'onmouseover', 'onmouseout', 'onfocus', 'onblur',
        'onkeydown', 'onkeyup', 'onkeypress', 'onsubmit', 'onchange', 'oninput'
    ];
    
    dangerousAttrs.forEach(attr => {
        const regex = new RegExp(`\\s+${attr}="[^"]*"`, 'gi');
        cleanedHtml = cleanedHtml.replace(regex, '');
    });
    
    // Удаляем javascript: ссылки
    cleanedHtml = cleanedHtml.replace(/href="javascript:[^"]*"/gi, 'href="#"');
    
    // Удаляем data: URL (потенциально опасные)
    cleanedHtml = cleanedHtml.replace(/src="data:[^"]*"/gi, 'src=""');
    
    // Разрешаем безопасные теги и атрибуты
    const allowedTags = [
        'p', 'div', 'span', 'strong', 'em', 'b', 'i', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'br', 'hr', 'img', 'a', 'video', 'source'
    ];
    
    const allowedAttrs = [
        'src', 'href', 'alt', 'title', 'width', 'height', 'style', 'class', 'id',
        'target', 'rel', 'controls', 'autoplay', 'muted', 'loop', 'poster'
    ];
    
    // Очищаем атрибуты, оставляя только разрешенные
    cleanedHtml = cleanedHtml.replace(/<([^>]+)>/g, (match, tagContent) => {
        const tagName = tagContent.split(/\s+/)[0].toLowerCase();
        
        if (!allowedTags.includes(tagName)) {
            return ''; // Удаляем неразрешенные теги
        }
        
        // Очищаем атрибуты
        const attrRegex = /(\w+)\s*=\s*["']([^"']*)["']/g;
        let cleanTag = tagName;
        
        let attrMatch;
        while ((attrMatch = attrRegex.exec(tagContent)) !== null) {
            const attrName = attrMatch[1].toLowerCase();
            const attrValue = attrMatch[2];
            
            if (allowedAttrs.includes(attrName)) {
                // Дополнительная проверка для src и href
                if ((attrName === 'src' || attrName === 'href') && 
                    (attrValue.startsWith('javascript:') || attrValue.startsWith('data:'))) {
                    continue; // Пропускаем опасные URL
                }
                cleanTag += ` ${attrName}="${attrValue}"`;
            }
        }
        
        return `<${cleanTag}>`;
    });
    
    return cleanedHtml;
};

/**
 * Функция для очистки контента от "Читать далее" и других ненужных элементов
 */
export const cleanContent = (html: string): string => {
    if (!html) return '';
    
    let cleanedHtml = html;
    
    // Паттерны для удаления
    const patternsToRemove = [
        // Ссылки "Читать далее"
        /<a[^>]*>Читать далее<\/a>/gi,
        /<a[^>]*>читать далее<\/a>/gi,
        /<a[^>]*>Read more<\/a>/gi,
        /<a[^>]*>read more<\/a>/gi,
        
        // Ссылки с #habracut
        /<a[^>]*href="[^"]*#habracut"[^>]*>.*?<\/a>/gi,
        /<a[^>]*href="[^"]*habracut"[^>]*>.*?<\/a>/gi,
        
        // Ссылки с utm параметрами
        /<a[^>]*href="[^"]*utm_source=habrahabr[^"]*"[^>]*>.*?<\/a>/gi,
        /<a[^>]*href="[^"]*utm_medium=rss[^"]*"[^>]*>.*?<\/a>/gi,
        
        // Простой текст
        /Читать далее/gi,
        /читать далее/gi,
        /Read more/gi,
        /read more/gi,
        
        // Хэштеги
        /#habracut/gi,
        /habracut/gi
    ];
    
    patternsToRemove.forEach(pattern => {
        cleanedHtml = cleanedHtml.replace(pattern, '');
    });
    
    // Удаляем пустые параграфы
    cleanedHtml = cleanedHtml.replace(/<p>\s*<\/p>/g, '');
    
    // Удаляем множественные пробелы
    cleanedHtml = cleanedHtml.replace(/\s{2,}/g, ' ');
    
    return cleanedHtml;
};

/**
 * Функция для извлечения изображений из HTML
 */
export const extractImagesFromHtml = (html: string): Array<{src: string, alt: string}> => {
    if (!html) return [];
    
    const imgRegex = /<img[^>]+src="([^"]+)"[^>]*alt="([^"]*)"[^>]*>|<img[^>]+alt="([^"]*)"[^>]*src="([^"]+)"[^>]*>/gi;
    const images: Array<{src: string, alt: string}> = [];
    
    let match;
    while ((match = imgRegex.exec(html)) !== null) {
        const src = match[1] || match[4];
        const alt = match[2] || match[3] || '';
        if (src) {
            images.push({ src, alt });
        }
    }
    
    return images;
};

/**
 * Функция для замены img тегов на React компоненты
 */
export const replaceImgTagsWithComponents = (html: string): string => {
    if (!html) return html;
    
    // Заменяем img теги на специальные маркеры для React
    return html.replace(
        /<img([^>]+)>/gi,
        (match, attributes) => {
            // Извлекаем src и alt
            const srcMatch = attributes.match(/src="([^"]+)"/i);
            const altMatch = attributes.match(/alt="([^"]*)"/i);
            
            const src = srcMatch ? srcMatch[1] : '';
            const alt = altMatch ? altMatch[1] : '';
            
            if (src) {
                return `{{IMAGE_COMPONENT:${src}:${alt}}}`;
            }
            
            return match; // Возвращаем оригинал, если нет src
        }
    );
};

/**
 * Основная функция для обработки HTML контента
 */
export const processHtmlContent = (html: string): string => {
    if (!html) return '';
    
    // Сначала очищаем от опасного контента
    let sanitizedHtml = sanitizeHtml(html);
    
    // Затем очищаем от ненужных элементов
    sanitizedHtml = cleanContent(sanitizedHtml);
    
    return sanitizedHtml;
}; 