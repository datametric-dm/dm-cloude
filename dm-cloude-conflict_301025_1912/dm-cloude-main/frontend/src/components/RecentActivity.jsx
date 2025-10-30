import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Clock, Users, FolderOpen, FileText, CreditCard } from 'lucide-react';
import { LoadingSpinner } from './ui/loading-spinner';
import { clientsApi, projectsApi, paymentsApi } from '../lib/api';
import { formatDistanceToNow } from 'date-fns';
import { ru } from 'date-fns/locale';

export default function RecentActivity() {
  const { data: recentClients, isLoading: clientsLoading } = useQuery({
    queryKey: ['recent-clients'],
    queryFn: () => clientsApi.getAll({ skip: 0, limit: 3 }).then(res => res.data),
  });

  const { data: recentProjects, isLoading: projectsLoading } = useQuery({
    queryKey: ['recent-projects'],
    queryFn: () => projectsApi.getAll({ skip: 0, limit: 3 }).then(res => res.data),
  });

  const { data: recentPayments, isLoading: paymentsLoading } = useQuery({
    queryKey: ['recent-payments'],
    queryFn: () => paymentsApi.getAll({ skip: 0, limit: 3 }).then(res => res.data),
  });

  const isLoading = clientsLoading || projectsLoading || paymentsLoading;

  // Объединяем все активности и сортируем по дате
  const activities = React.useMemo(() => {
    const items = [];
    
    if (recentClients?.clients) {
      recentClients.clients.forEach(client => {
        items.push({
          id: `client-${client.id}`,
          type: 'client',
          title: `Новый клиент: ${client.name}`,
          subtitle: client.company,
          date: new Date(client.created_at),
          icon: Users,
          color: 'blue',
        });
      });
    }

    if (recentProjects?.projects) {
      recentProjects.projects.forEach(project => {
        items.push({
          id: `project-${project.id}`,
          type: 'project',
          title: `Новый проект: ${project.name}`,
          subtitle: `Статус: ${getStatusLabel(project.status)}`,
          date: new Date(project.created_at),
          icon: FolderOpen,
          color: 'green',
        });
      });
    }

    if (recentPayments?.payments) {
      recentPayments.payments.forEach(payment => {
        items.push({
          id: `payment-${payment.id}`,
          type: 'payment',
          title: `Платёж: ${payment.amount} ₽`,
          subtitle: `Статус: ${getPaymentStatusLabel(payment.status)}`,
          date: new Date(payment.created_at),
          icon: CreditCard,
          color: 'purple',
        });
      });
    }

    return items
      .sort((a, b) => b.date - a.date)
      .slice(0, 6);
  }, [recentClients, recentProjects, recentPayments]);

  function getStatusLabel(status) {
    const statusMap = {
      planning: 'Планирование',
      in_progress: 'В работе',
      review: 'На проверке',
      completed: 'Завершён',
      on_hold: 'Приостановлен',
      cancelled: 'Отменён',
    };
    return statusMap[status] || status;
  }

  function getPaymentStatusLabel(status) {
    const statusMap = {
      planned: 'Планируемый',
      received: 'Получен',
      overdue: 'Просрочен',
      cancelled: 'Отменён',
    };
    return statusMap[status] || status;
  }

  const colorClasses = {
    blue: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    purple: 'text-purple-600 bg-purple-50',
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6" data-testid="recent-activity">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Последняя активность</h3>
        <Clock className="w-5 h-5 text-gray-400" />
      </div>

      {isLoading ? (
        <LoadingSpinner className="py-8" />
      ) : activities.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          Нет последней активности
        </div>
      ) : (
        <div className="space-y-3">
          {activities.map((activity) => {
            const Icon = activity.icon;
            return (
              <div
                key={activity.id}
                className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                data-testid={`activity-${activity.type}`}
              >
                <div className={`p-2 rounded-lg ${colorClasses[activity.color]}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 text-sm truncate">
                    {activity.title}
                  </p>
                  <p className="text-sm text-gray-500 truncate">
                    {activity.subtitle}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    {formatDistanceToNow(activity.date, { 
                      addSuffix: true, 
                      locale: ru 
                    })}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
