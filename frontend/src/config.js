/**
 * Конфигурация Frontend БЕЗ использования .env файлов
 * Все настройки зашиты напрямую для простоты использования
 */

// Определяем окружение
const isDevelopment = process.env.NODE_ENV === 'development';
const isProduction = process.env.NODE_ENV === 'production';

// === BACKEND API URL ===
// Для preview и production: используем пустую строку (относительные пути)
// Backend доступен через тот же домен благодаря nginx проксированию
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';  // Всегда используем относительные пути

// === API ENDPOINTS ===
const API_BASE = `${BACKEND_URL}/api`;

const config = {
  // Backend URL
  BACKEND_URL,
  API_BASE,
  
  // API Endpoints
  endpoints: {
    // Auth
    login: `${API_BASE}/auth/login`,
    register: `${API_BASE}/auth/register`,
    me: `${API_BASE}/auth/me`,
    
    // Clients
    clients: `${API_BASE}/clients`,
    
    // Projects
    projects: `${API_BASE}/projects`,
    
    // Services
    services: `${API_BASE}/services`,
    
    // Invoices
    invoices: `${API_BASE}/invoices`,
    
    // Payments
    payments: `${API_BASE}/payments`,
    
    // Reports
    reports: `${API_BASE}/reports`,
    
    // Files
    files: `${API_BASE}/files`,
    
    // Health
    health: `${API_BASE}/health`,
  },
  
  // App settings
  app: {
    name: 'DataMetrics Cloud',
    version: '2.0.0',
    description: 'Система управления проектами, клиентами и финансами',
  },
  
  // UI Settings
  ui: {
    pageSize: 20,
    maxFileSize: 10 * 1024 * 1024, // 10 MB
    dateFormat: 'DD.MM.YYYY',
    timeFormat: 'HH:mm',
    currency: '₽',
  },
  
  // Debug mode
  debug: isDevelopment,
  
  // Environment
  env: process.env.NODE_ENV || 'production',
};

// Логирование в dev режиме
if (config.debug) {
  console.log('🔧 Config loaded:', config);
}

export default config;
