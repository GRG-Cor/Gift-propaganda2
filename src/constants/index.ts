export const CATEGORIES = [
  { id: 'all', name: 'Все потоки', icon: '' },
  { id: 'gifts', name: 'Подарки', icon: '🎁' },
  { id: 'crypto', name: 'Крипто', icon: '₿' },
  { id: 'tech', name: 'Технологии', icon: '💻' },
  { id: 'community', name: 'Сообщество', icon: '👥' },
  { id: 'nft', name: 'NFT', icon: '🖼️' }
];

export const CATEGORY_COLORS: Record<string, string> = {
  'gifts': '#ff6b6b',
  'crypto': '#4ecdc4',
  'tech': '#45b7d1',
  'community': '#96ceb4',
  'gaming': '#feca57',
  'news': '#ff9ff3',
  'default': '#6c5ce7'
};

export const API_ENDPOINTS = {
  NEWS: '/api/news',
  STATUS: '/api/status'
};

export const PAGINATION = {
  DEFAULT_LIMIT: 20,
  DEFAULT_OFFSET: 0
}; 