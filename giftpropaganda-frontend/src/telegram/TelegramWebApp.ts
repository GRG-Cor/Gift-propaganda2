// Telegram WebApp API для React
class TelegramWebApp {
  private webApp: any = null;

  init() {
    // Проверяем, что мы внутри Telegram
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
      this.webApp = window.Telegram.WebApp;
      
      // Инициализация Mini App
      this.webApp.ready();
      this.webApp.expand();

      // Настройка темы для Mini App
      this.webApp.setHeaderColor('#1a1a1a');
      this.webApp.setBackgroundColor('#1a1a1a');

      // MainButton отключен для Mini App
      this.webApp.MainButton.hide();

      // Настройка BackButton
      this.webApp.BackButton.show();
      this.webApp.BackButton.onClick(() => {
        this.webApp.close();
      });

      console.log('Telegram Mini App инициализирован');
      console.log('Пользователь:', this.getUserData());
      console.log('Тема:', this.getThemeParams());
    } else {
      console.log('Telegram WebApp недоступен - работаем в браузере');
    }
  }

  isAvailable(): boolean {
    return this.webApp !== null;
  }

  expand() {
    if (this.webApp && this.webApp.expand) {
      this.webApp.expand();
    }
  }

  getThemeParams() {
    if (this.webApp) {
      return this.webApp.themeParams;
    }
    return {
      bg_color: '#1a1a1a',
      text_color: '#ffffff',
      hint_color: '#999999',
      link_color: '#0088cc',
      button_color: '#0088cc',
      button_text_color: '#ffffff'
    };
  }

  getUserData() {
    if (this.webApp && this.webApp.initDataUnsafe) {
      return this.webApp.initDataUnsafe.user;
    }
    return null;
  }

  getInitData() {
    if (this.webApp && this.webApp.initData) {
      return this.webApp.initData;
    }
    return '';
  }

  triggerHapticFeedback(type: 'impact' | 'notification' = 'impact') {
    if (this.webApp && this.webApp.HapticFeedback) {
      if (type === 'impact') {
        this.webApp.HapticFeedback.impactOccurred('light');
      } else if (type === 'notification') {
        this.webApp.HapticFeedback.notificationOccurred('success');
      }
    }
  }

  showPopup(title: string, message: string, buttons?: any[]) {
    if (this.webApp && this.webApp.showPopup) {
      return this.webApp.showPopup({
        title,
        message,
        buttons: buttons || [{ type: 'ok' }]
      });
    }
  }

  showAlert(message: string) {
    if (this.webApp && this.webApp.showAlert) {
      this.webApp.showAlert(message);
    } else {
      alert(message);
    }
  }

  showConfirm(message: string, callback?: (confirmed: boolean) => void) {
    if (this.webApp && this.webApp.showConfirm) {
      this.webApp.showConfirm(message, callback);
    } else {
      const confirmed = window.confirm(message);
      if (callback) callback(confirmed);
    }
  }

  close() {
    if (this.webApp && this.webApp.close) {
      this.webApp.close();
    }
  }

  openLink(url: string) {
    if (this.webApp && this.webApp.openLink) {
      this.webApp.openLink(url);
    } else {
      window.open(url, '_blank');
    }
  }

  openTelegramLink(url: string) {
    if (this.webApp && this.webApp.openTelegramLink) {
      this.webApp.openTelegramLink(url);
    } else {
      window.open(url, '_blank');
    }
  }

  setMainButton(text: string, callback?: () => void) {
    if (this.webApp && this.webApp.MainButton) {
      this.webApp.MainButton.setText(text);
      this.webApp.MainButton.show();

      if (callback) {
        this.webApp.MainButton.onClick(callback);
      }
    }
  }

  hideMainButton() {
    if (this.webApp && this.webApp.MainButton) {
      this.webApp.MainButton.hide();
    }
  }

  showMainButton() {
    if (this.webApp && this.webApp.MainButton) {
      this.webApp.MainButton.show();
    }
  }

  setBackButton(callback?: () => void) {
    if (this.webApp && this.webApp.BackButton) {
      this.webApp.BackButton.show();
      if (callback) {
        this.webApp.BackButton.onClick(callback);
      }
    }
  }

  hideBackButton() {
    if (this.webApp && this.webApp.BackButton) {
      this.webApp.BackButton.hide();
    }
  }

  // Методы для работы с Mini App
  isMiniApp(): boolean {
    return this.webApp !== null;
  }

  getPlatform(): string {
    if (this.webApp) {
      return this.webApp.platform;
    }
    return 'unknown';
  }

  getVersion(): string {
    if (this.webApp) {
      return this.webApp.version;
    }
    return 'unknown';
  }

  getColorScheme(): 'light' | 'dark' {
    if (this.webApp) {
      return this.webApp.colorScheme;
    }
    return 'dark';
  }

  // Методы для работы с данными
  sendData(data: string) {
    if (this.webApp && this.webApp.sendData) {
      this.webApp.sendData(data);
    }
  }

  switchInlineQuery(query: string, choose_chat_types?: string[]) {
    if (this.webApp && this.webApp.switchInlineQuery) {
      this.webApp.switchInlineQuery(query, choose_chat_types);
    }
  }
}

// Создаем единственный экземпляр
const telegramWebApp = new TelegramWebApp();

export default telegramWebApp;
