// Типы для Telegram WebApp API
declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp;
    };
  }
}

interface TelegramWebApp {
  ready(): void;
  expand(): void;
  close(): void;
  
  // Тема и цвета
  setHeaderColor(color: string): void;
  setBackgroundColor(color: string): void;
  themeParams: {
    bg_color?: string;
    text_color?: string;
    hint_color?: string;
    link_color?: string;
    button_color?: string;
    button_text_color?: string;
  };
  
  // Пользователь
  initDataUnsafe: {
    user?: {
      id: number;
      is_bot: boolean;
      first_name: string;
      last_name?: string;
      username?: string;
      language_code?: string;
    };
    chat?: {
      id: number;
      type: string;
      title?: string;
      username?: string;
    };
  };
  
  // Данные
  initData: string;
  
  // Платформа
  platform: string;
  version: string;
  colorScheme: 'light' | 'dark';
  
  // Кнопки
  MainButton: {
    text: string;
    color: string;
    textColor: string;
    isVisible: boolean;
    isActive: boolean;
    isProgressVisible: boolean;
    setText(text: string): void;
    onClick(callback: () => void): void;
    show(): void;
    hide(): void;
    enable(): void;
    disable(): void;
    showProgress(leaveActive?: boolean): void;
    hideProgress(): void;
  };
  
  BackButton: {
    isVisible: boolean;
    onClick(callback: () => void): void;
    show(): void;
    hide(): void;
  };
  
  // Haptic Feedback
  HapticFeedback: {
    impactOccurred(style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft'): void;
    notificationOccurred(type: 'error' | 'success' | 'warning'): void;
    selectionChanged(): void;
  };
  
  // Попапы
  showPopup(params: {
    title: string;
    message: string;
    buttons?: Array<{
      id?: string;
      type: 'default' | 'ok' | 'close' | 'cancel' | 'destructive';
      text?: string;
    }>;
  }): Promise<string>;
  
  showAlert(message: string): Promise<void>;
  showConfirm(message: string, callback?: (confirmed: boolean) => void): Promise<boolean>;
  
  // Ссылки
  openLink(url: string): void;
  openTelegramLink(url: string): void;
  
  // Данные
  sendData(data: string): void;
  switchInlineQuery(query: string, choose_chat_types?: string[]): void;
}

export {};
