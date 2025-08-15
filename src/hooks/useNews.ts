import { useState, useEffect, useCallback } from 'react';
import { NewsItem } from '../types';
import { fetchNews } from '../api/news';

export const useNews = (category: string = 'all') => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);

  const getNews = useCallback(async (isLoadMore: boolean = false) => {
    try {
      console.log('=== API ЗАПРОС ===');
      console.log('Категория:', category);
      console.log('Страница:', page);
      console.log('Тип запроса:', isLoadMore ? 'loadMore' : 'initial');
      console.log('Время запроса:', new Date().toISOString());
      
      // Используем реальный API
      const response = await fetchNews(
        category === 'all' ? undefined : category, 
        page, 
        20
      );

      console.log('API ответ получен:', {
        success: !!response,
        data_count: response?.data?.length || 0,
        has_more: response?.data?.length === 20,
        total: response?.total || 0
      });

      if (response && response.data) {
        if (isLoadMore) {
          setNews(prev => [...prev, ...response.data]);
        } else {
          setNews(response.data);
        }
        setHasMore(response.data.length === 20);
      }
      
      console.log('========================');
      
      // Раскомментируйте для тестовых данных:
      // const testNews = generateTestNews();
      // const filteredNews = category === 'all' 
      //   ? testNews 
      //   : testNews.filter(item => item.category === category);
      // if (isLoadMore) {
      //   setNews(prev => [...prev, ...filteredNews]);
      // } else {
      //   setNews(filteredNews);
      // }
      // setHasMore(false);
    } catch (error) {
      console.error('Ошибка загрузки новостей:', error);
      setError('Не удалось загрузить новости');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [category, page]);

  const loadMore = async () => {
    if (!loadingMore && hasMore) {
      const nextPage = page + 1;
      setPage(nextPage);
      
      console.log('=== ЗАГРУЗКА ДОПОЛНИТЕЛЬНЫХ НОВОСТЕЙ ===');
      console.log('Следующая страница:', nextPage);
      console.log('Категория:', category);
      console.log('Время запроса:', new Date().toISOString());
      
      try {
        setLoadingMore(true);
        const response = await fetchNews(
          category === 'all' ? undefined : category,
          nextPage,
          20,
          false
        );
        
        console.log('Дополнительные новости загружены:', {
          success: !!response,
          data_count: response?.data?.length || 0,
          has_more: response?.data?.length === 20 && (response.total || 0) > nextPage * 20
        });
        
        setNews(prev => [...prev, ...response.data]);
        setHasMore(response.data.length === 20 && (response.total || 0) > nextPage * 20);
        
        console.log('========================');
        
        // Раскомментируйте для тестовых данных:
        // const moreTestNews = generateTestNews().map(item => ({
        //   ...item,
        //   id: item.id + 1000
        // }));
        // setNews(prev => [...prev, ...moreTestNews]);
        // setHasMore(false);
      } catch (err) {
        console.error('Ошибка при загрузке дополнительных новостей:', err);
        setPage(prev => prev - 1);
      } finally {
        setLoadingMore(false);
      }
    }
  };

  useEffect(() => {
    setPage(1);
    setHasMore(true);
    getNews();
  }, [category, getNews]);

  return {
    news,
    loading,
    error,
    hasMore,
    loadingMore,
    loadMore
  };
}; 