export const formatTimeAgo = (dateString: string): string => {
  const now = new Date();
  const date = new Date(dateString);
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'только что';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} мин назад`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} ч назад`;
  return `${Math.floor(diffInSeconds / 86400)} дн назад`;
};

export const isNewNews = (dateString: string): boolean => {
  const now = new Date();
  const date = new Date(dateString);
  const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
  return diffInHours < 24;
};

export const getCategoryColor = (category: string): string => {
  const colors: Record<string, string> = {
    'gifts': '#ff6b6b',
    'crypto': '#4ecdc4',
    'tech': '#45b7d1',
    'community': '#96ceb4',
    'gaming': '#feca57',
    'news': '#ff9ff3',
    'default': '#6c5ce7'
  };
  return colors[category] || colors.default;
}; 