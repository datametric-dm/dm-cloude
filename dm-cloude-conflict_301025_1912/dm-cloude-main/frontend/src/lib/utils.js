import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount) {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatDate(date) {
  return new Date(date).toLocaleDateString('ru-RU');
}

export function formatDateTime(date) {
  return new Date(date).toLocaleString('ru-RU');
}

export function getStatusBadgeClass(status) {
  const statusClasses = {
    // Проекты
    planning: 'bg-yellow-100 text-yellow-800',
    in_progress: 'bg-blue-100 text-blue-800',
    review: 'bg-purple-100 text-purple-800',
    completed: 'bg-green-100 text-green-800',
    on_hold: 'bg-gray-100 text-gray-800',
    cancelled: 'bg-red-100 text-red-800',
    
    // Платежи
    planned: 'bg-yellow-100 text-yellow-800',
    received: 'bg-green-100 text-green-800',
    overdue: 'bg-red-100 text-red-800',
    
    // Счета
    draft: 'bg-gray-100 text-gray-800',
    sent: 'bg-blue-100 text-blue-800',
    paid: 'bg-green-100 text-green-800',
  };
  
  return statusClasses[status] || 'bg-gray-100 text-gray-800';
}

export function getStatusLabel(status, type = 'project') {
  const labels = {
    project: {
      planning: 'Планирование',
      in_progress: 'В работе',
      review: 'На проверке',
      completed: 'Завершён',
      on_hold: 'Приостановлен',
      cancelled: 'Отменён',
    },
    payment: {
      planned: 'Планируемый',
      received: 'Получен',
      overdue: 'Просрочен',
      cancelled: 'Отменён',
    },
    invoice: {
      draft: 'Черновик',
      sent: 'Отправлен',
      paid: 'Оплачен',
      overdue: 'Просрочен',
      cancelled: 'Отменён',
    },
  };
  
  return labels[type]?.[status] || status;
}
