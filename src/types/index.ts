export interface NewsItem {
  id: number;
  title: string;
  content: string;
  content_html?: string;
  link?: string;
  publish_date: string;
  category: string;
  source?: {
    id: number;
    name: string;
  };
  media?: MediaItem[];
  reading_time?: number;
  views_count?: number;
  author?: string;
  subtitle?: string;
  // Новые поля для дизайна
  background_image?: string;
  background_color?: string;
  icon?: string;
  gradient_start?: string;
  gradient_end?: string;
}

export interface MediaItem {
  type: 'photo' | 'video';
  url: string;
  thumbnail?: string;
  width?: number;
  height?: number;
}

export interface Category {
  id: string;
  name: string;
  icon: string;
}

export interface APIStatus {
  apiHealth: {
    local: boolean;
    prod: boolean;
  };
} 