import { NewsItem } from '../types';

export interface NewsStyles {
  background: string;
  icon: string;
  textColor: string;
  subtitleColor: string;
}

export const getNewsStyles = (news: NewsItem): NewsStyles => {
  // Определяем фон
  let background = 'var(--tg-theme-secondary-bg-color, #1a1a1a)';
  
  if (news.background_image) {
    background = `linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url(${news.background_image})`;
  } else if (news.gradient_start && news.gradient_end) {
    background = `linear-gradient(135deg, ${news.gradient_start} 0%, ${news.gradient_end} 100%)`;
  } else if (news.background_color) {
    background = news.background_color;
  } else {
    // Градиенты по категориям по умолчанию
    const categoryGradients: Record<string, string> = {
      'gifts': 'linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%)',
      'crypto': 'linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%)',
      'tech': 'linear-gradient(135deg, #45b7d1 0%, #96c93d 100%)',
      'community': 'linear-gradient(135deg, #96ceb4 0%, #feca57 100%)',
      'nft': 'linear-gradient(135deg, #a78bfa 0%, #c084fc 100%)',
      'default': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    };
    background = categoryGradients[news.category] || categoryGradients.default;
  }

  // Определяем иконку - всегда показываем иконку
  let icon = '📰';
  
  if (news.icon && news.icon.trim() !== '') {
    icon = news.icon;
  } else {
    // Иконки по категориям по умолчанию
    const categoryIcons: Record<string, string> = {
      'gifts': '🎁',
      'crypto': '₿',
      'tech': '💻',
      'community': '👥',
      'nft': '🖼️',
      'default': '📰'
    };
    icon = categoryIcons[news.category] || categoryIcons.default;
  }

  // Определяем цвета текста для лучшей читаемости
  let textColor = '#ffffff';
  let subtitleColor = '#ffffff';
  
  // Если есть градиент или цветной фон, используем белый текст с тенью
  if (news.gradient_start || news.background_color || news.background_image) {
    textColor = '#ffffff';
    subtitleColor = '#ffffff';
  } else {
    textColor = 'var(--tg-theme-text-color, #ffffff)';
    subtitleColor = 'var(--tg-theme-text-color, #ffffff)';
  }

  return {
    background,
    icon,
    textColor,
    subtitleColor
  };
}; 