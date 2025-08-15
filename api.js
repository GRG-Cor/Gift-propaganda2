// Простой API для GitHub Pages
const API_DATA = {
  news: [
    {
      id: 1,
      title: "🎉 Добро пожаловать в Gift Propaganda!",
      content: "Ваш агрегатор новостей готов к использованию.",
      content_html: "<p>Ваш агрегатор новостей готов к использованию.</p>",
      publish_date: new Date().toISOString(),
      category: "welcome",
      link: "#",
      media: []
    },
    {
      id: 2,
      title: "📰 Последние новости из мира криптовалют",
      content: "Актуальные новости о Bitcoin, Ethereum и других криптовалютах.",
      content_html: "<p>Актуальные новости о Bitcoin, Ethereum и других криптовалютах.</p>",
      publish_date: new Date().toISOString(),
      category: "crypto",
      link: "#",
      media: []
    },
    {
      id: 3,
      title: "🎮 Новости игровой индустрии",
      content: "Самые свежие новости из мира игр и технологий.",
      content_html: "<p>Самые свежие новости из мира игр и технологий.</p>",
      publish_date: new Date().toISOString(),
      category: "gaming",
      link: "#",
      media: []
    }
  ],
  categories: ["welcome", "crypto", "gaming", "tech", "community"]
};

// Имитация API endpoints
window.API = {
  async getNews(category = null, page = 1, limit = 20) {
    let filteredNews = API_DATA.news;
    
    if (category && category !== 'all') {
      filteredNews = filteredNews.filter(item => item.category === category);
    }
    
    const start = (page - 1) * limit;
    const end = start + limit;
    const paginatedNews = filteredNews.slice(start, end);
    
    return {
      status: "success",
      data: paginatedNews,
      total: filteredNews.length,
      page: page,
      pages: Math.ceil(filteredNews.length / limit)
    };
  },
  
  async getNewsById(id) {
    const news = API_DATA.news.find(item => item.id === parseInt(id));
    return news || null;
  },
  
  async getCategories() {
    return {
      status: "success",
      data: API_DATA.categories
    };
  }
}; 