import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Header from './components/Header';
import NewsCard from './components/NewsCard';
import FeaturedNewsCard from './components/FeaturedNewsCard';
import NewsModal from './components/NewsModal';
import { useNews } from './hooks/useNews';
import { CATEGORIES } from './constants';
import { NewsItem } from './types';
import TelegramWebApp from './telegram/TelegramWebApp';

const AppContainer = styled.div`
  min-height: 100vh;
  background: var(--tg-theme-bg-color, #0f0f0f);
  color: var(--tg-theme-text-color, #ffffff);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  padding: 0;
  margin: 0;
`;

const NewsContainer = styled.div`
  padding: 0 16px 20px 16px;
  max-width: 800px;
  margin: 0 auto;
  
  /* Отступ для первого элемента */
  > *:first-child {
    margin-top: 16px;
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  
  &::after {
    content: '';
    width: 32px;
    height: 32px;
    border: 3px solid var(--tg-theme-hint-color, #333);
    border-top: 3px solid var(--tg-theme-button-color, #0088cc);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: var(--tg-theme-destructive-text-color, #ff4444);
  font-size: 16px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: var(--tg-theme-hint-color, #999);
  
  h3 {
    margin: 0 0 8px 0;
    font-size: 18px;
    color: var(--tg-theme-text-color, #ffffff);
  }
  
  p {
    margin: 0;
    font-size: 14px;
  }
`;

const LoadMoreButton = styled.button`
  background: var(--tg-theme-button-color, #0088cc);
  color: var(--tg-theme-button-text-color, #ffffff);
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  opacity: 1;
  transition: all 0.2s ease;
  margin: 20px auto;
  display: block;

  &:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

const App: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNews, setSelectedNews] = useState<NewsItem | null>(null);

  const { news, loading, error, hasMore, loadingMore, loadMore } = useNews(selectedCategory);

  useEffect(() => {
    TelegramWebApp.init();
    TelegramWebApp.expand();
    
    // Логируем информацию о Mini App
    console.log('=== TELEGRAM MINI APP INFO ===');
    console.log('Доступен:', TelegramWebApp.isAvailable());
    console.log('Платформа:', TelegramWebApp.getPlatform());
    console.log('Версия:', TelegramWebApp.getVersion());
    console.log('Цветовая схема:', TelegramWebApp.getColorScheme());
    console.log('Пользователь:', TelegramWebApp.getUserData());
    console.log('=============================');
  }, []);

  const handleNewsClick = (newsItem: NewsItem) => {
    setSelectedNews(newsItem);
    TelegramWebApp.triggerHapticFeedback('impact');
    
    // Логируем API запрос для получения данных новости
    console.log('=== API ЗАПРОС ДЛЯ НОВОСТИ ===');
    console.log('ID новости:', newsItem.id);
    console.log('Заголовок:', newsItem.title);
    console.log('Категория:', newsItem.category);
    console.log('Дата публикации:', newsItem.publish_date);
    console.log('Ссылка:', newsItem.link);
    
    // Показываем, какой API запрос был выполнен
    console.log('API запрос для получения этой новости:');
    console.log('URL:', `/api/news/${newsItem.id}`);
    console.log('Метод: GET');
    console.log('Параметры:', {
      id: newsItem.id,
      category: newsItem.category,
      include_media: true,
      include_source: true
    });
    
    console.log('Полученные данные из API:', {
      background_image: newsItem.background_image,
      background_color: newsItem.background_color,
      icon: newsItem.icon,
      gradient_start: newsItem.gradient_start,
      gradient_end: newsItem.gradient_end,
      media_count: newsItem.media?.length || 0,
      content_html: newsItem.content_html ? 'Есть HTML контент' : 'Нет HTML контента',
      content_length: newsItem.content?.length || 0
    });
    
    console.log('Текущая категория:', selectedCategory);
    console.log('Поисковый запрос:', searchQuery);
    console.log('Всего новостей загружено:', news.length);
    console.log('========================');
  };

  const handleCategoryChange = (categoryId: string) => {
    setSelectedCategory(categoryId);
    setSearchQuery('');
  };

  const filteredNews = news.filter(item =>
    item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Разделяем новости на featured (первые 2) и обычные
  const featuredNews = filteredNews.slice(0, 2);
  const regularNews = filteredNews.slice(2);

  if (loading) {
    return (
      <AppContainer>
        <Header
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedCategory={selectedCategory}
          onCategoryChange={handleCategoryChange}
          categories={CATEGORIES}
        />
        <LoadingSpinner />
      </AppContainer>
    );
  }

  if (error) {
    return (
      <AppContainer>
        <Header
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedCategory={selectedCategory}
          onCategoryChange={handleCategoryChange}
          categories={CATEGORIES}
        />
        <ErrorMessage>{error}</ErrorMessage>
      </AppContainer>
    );
  }

  return (
    <AppContainer>
      <Header
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        selectedCategory={selectedCategory}
        onCategoryChange={handleCategoryChange}
        categories={CATEGORIES}
      />

      <NewsContainer>
        {filteredNews.length === 0 ? (
          <EmptyState>
            <h3>📭 Новостей не найдено</h3>
            <p>Попробуйте изменить категорию или поисковый запрос</p>
          </EmptyState>
        ) : (
          <>
            {/* Featured новости с собственным фоном */}
            {featuredNews.map(item => (
              <FeaturedNewsCard
                key={item.id}
                news={item}
                onClick={handleNewsClick}
              />
            ))}
            
            {/* Обычные новости */}
            {regularNews.map(item => (
              <NewsCard
                key={item.id}
                news={item}
                onClick={handleNewsClick}
              />
            ))}
            
            {hasMore && (
              <LoadMoreButton
                onClick={loadMore}
                disabled={loadingMore}
              >
                {loadingMore ? 'Загрузка...' : 'Загрузить еще'}
              </LoadMoreButton>
            )}
          </>
        )}
      </NewsContainer>

      {selectedNews && (
        <NewsModal
          news={selectedNews}
          isOpen={!!selectedNews}
          onClose={() => setSelectedNews(null)}
        />
      )}
    </AppContainer>
  );
};

export default App;
