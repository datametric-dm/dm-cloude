import axios from 'axios';
import config from '../config';

// Используем конфигурацию из config.js (без .env файлов)
export const api = axios.create({
  baseURL: config.API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 секунд
});

// Логирование запросов в dev режиме
if (config.debug) {
  console.log('🌐 API initialized:', config.API_BASE);
}

// Добавляем interceptor для автоматической вставки токена и company ID
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add Company ID header for multi-tenancy
    const currentCompany = localStorage.getItem('current_company');
    if (currentCompany) {
      try {
        const company = JSON.parse(currentCompany);
        if (company && company.id) {
          config.headers['X-Company-ID'] = company.id;
        }
      } catch (e) {
        console.error('Failed to parse current company', e);
      }
    }
    
    // Add User ID header
    const user = localStorage.getItem('user');
    if (user) {
      try {
        const userData = JSON.parse(user);
        if (userData && userData.id) {
          config.headers['X-User-ID'] = userData.id;
        }
      } catch (e) {
        console.error('Failed to parse user', e);
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Добавляем interceptor для обработки ошибок авторизации
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Токен истек или невалидный - перенаправляем на логин
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Клиенты
export const clientsApi = {
  getAll: (params = {}) => api.get('/clients/', { params }),
  getById: (id) => api.get(`/clients/${id}`),
  create: (data) => api.post('/clients/', data),
  update: (id, data) => api.put(`/clients/${id}`, data),
  delete: (id) => api.delete(`/clients/${id}`),
};

// Проекты
export const projectsApi = {
  getAll: (params = {}) => api.get('/projects/', { params }),
  getById: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post('/projects/', data),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
  getByStatus: (status) => api.get(`/projects/by-status/${status}`),
};

// Услуги
export const servicesApi = {
  getAll: (params = {}) => api.get('/services/', { params }),
  getById: (id) => api.get(`/services/${id}`),
  create: (data) => api.post('/services/', data),
  update: (id, data) => api.put(`/services/${id}`, data),
  getCategories: () => api.get('/services/categories/'),
};

// Счета
export const invoicesApi = {
  getAll: (params = {}) => api.get('/invoices/', { params }),
  getById: (id) => api.get(`/invoices/${id}`),
  create: (data) => api.post('/invoices/', data),
  update: (id, data) => api.put(`/invoices/${id}`, data),
  getOverdue: () => api.get('/invoices/overdue/list'),
};

// Платежи
export const paymentsApi = {
  getAll: (params = {}) => api.get('/payments/', { params }),
  getById: (id) => api.get(`/payments/${id}`),
  create: (data) => api.post('/payments/', data),
  update: (id, data) => api.put(`/payments/${id}`, data),
  delete: (id) => api.delete(`/payments/${id}`),
  getOverdue: () => api.get('/payments/overdue/list'),
  markReceived: (id) => api.post(`/payments/${id}/mark-received`),
};

// Отчеты
export const reportsApi = {
  getDashboard: () => api.get('/reports/dashboard'),
  getMonthlyRevenue: (year = new Date().getFullYear()) => api.get('/reports/monthly-revenue', { params: { year } }),
  getProjectDistribution: () => api.get('/reports/project-status-distribution'),
  getClientRevenue: (params = {}) => api.get('/reports/client-revenue', { params }),
  getOverdueSummary: () => api.get('/reports/overdue-summary'),
};

// Файлы
export const filesApi = {
  upload: (projectId, formData) => api.post(`/files/upload/${projectId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getProjectFiles: (projectId, category) => api.get(`/files/project/${projectId}`, { params: { category } }),
  deleteFile: (id) => api.delete(`/files/${id}`),
};

// Telegram
export const telegramApi = {
  test: () => api.get('/telegram/test'),
  notifyOverdue: () => api.post('/telegram/notify-overdue'),
  sendDailyReport: () => api.post('/telegram/daily-report'),
};
