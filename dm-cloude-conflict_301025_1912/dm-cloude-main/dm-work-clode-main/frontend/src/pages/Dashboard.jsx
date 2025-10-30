import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Users,
  FolderOpen,
  FileText,
  CreditCard,
  TrendingUp,
  AlertTriangle,
  Calendar,
  DollarSign,
  Plus,
} from 'lucide-react';
import { StatsCard } from '../components/ui/stats-card';
import { LoadingCard } from '../components/ui/loading-spinner';
import { reportsApi, paymentsApi, invoicesApi } from '../lib/api';
import { useNavigate } from 'react-router-dom';
import { formatCurrency } from '../lib/utils';
import OverdueAlert from '../components/OverdueAlert';
import RecentActivity from '../components/RecentActivity';

export default function Dashboard() {
  const navigate = useNavigate();
  
  const { data: dashboardStats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => reportsApi.getDashboard().then(res => res.data),
  });

  const { data: overduePayments } = useQuery({
    queryKey: ['overdue-payments'],
    queryFn: () => paymentsApi.getOverdue().then(res => res.data),
  });

  const { data: overdueInvoices } = useQuery({
    queryKey: ['overdue-invoices'],
    queryFn: () => invoicesApi.getOverdue().then(res => res.data),
  });

  if (statsLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Дашборд</h1>
        </div>
        <LoadingCard />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Дашборд</h1>
          <p className="text-gray-600 mt-1">Общая информация по проектам и клиентам</p>
        </div>
        <div className="text-sm text-gray-500">
          Обновлено: {new Date().toLocaleTimeString('ru-RU')}
        </div>
      </div>

      {/* Оповещения о просрочках */}
      {(overduePayments?.count > 0 || overdueInvoices?.count > 0) && (
        <OverdueAlert 
          overduePayments={overduePayments} 
          overdueInvoices={overdueInvoices} 
        />
      )}

      {/* Основные метрики */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Всего клиентов"
          value={dashboardStats?.total_clients || 0}
          icon={Users}
          data-testid="total-clients-card"
        />
        
        <StatsCard
          title="Активные проекты"
          value={dashboardStats?.active_projects || 0}
          subtitle={`из ${dashboardStats?.total_projects || 0} общих`}
          icon={FolderOpen}
          data-testid="active-projects-card"
        />
        
        <StatsCard
          title="Общая выручка"
          value={formatCurrency(dashboardStats?.total_revenue || 0)}
          subtitle={`Ожидается: ${formatCurrency(dashboardStats?.pending_revenue || 0)}`}
          icon={TrendingUp}
          data-testid="total-revenue-card"
        />
        
        <StatsCard
          title="Просрочки"
          value={dashboardStats?.overdue_payments_count || 0}
          subtitle={formatCurrency(dashboardStats?.overdue_amount || 0)}
          icon={AlertTriangle}
          className={dashboardStats?.overdue_payments_count > 0 ? "border-red-200 bg-red-50" : ""}
          data-testid="overdue-card"
        />
      </div>

      {/* Дополнительные метрики */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatsCard
          title="Неоплаченные счета"
          value={dashboardStats?.unpaid_invoices || 0}
          icon={FileText}
          data-testid="unpaid-invoices-card"
        />
        
        <StatsCard
          title="Платежи на сегодня"
          value="0" // Будем добавлять позже
          icon={Calendar}
          data-testid="today-payments-card"
        />
        
        <StatsCard
          title="Средняя сумма проекта"
          value={dashboardStats?.total_projects > 0 
            ? formatCurrency((dashboardStats?.total_revenue || 0) / dashboardStats.total_projects)
            : formatCurrency(0)
          }
          icon={DollarSign}
          data-testid="avg-project-value-card"
        />
      </div>

      {/* Последняя активность */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentActivity />
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Быстрые действия</h3>
          <div className="space-y-3">
            <button 
              className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
              data-testid="quick-action-new-client"
              onClick={() => navigate('/clients?action=new')}
            >
              <div className="flex items-center">
                <Users className="w-5 h-5 text-blue-600 mr-3" />
                <div>
                  <p className="font-medium text-gray-900">Добавить клиента</p>
                  <p className="text-sm text-gray-500">Создать нового клиента</p>
                </div>
              </div>
            </button>
            
            <button 
              className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
              data-testid="quick-action-new-project"
              onClick={() => navigate('/projects?action=new')}
            >
              <div className="flex items-center">
                <FolderOpen className="w-5 h-5 text-green-600 mr-3" />
                <div>
                  <p className="font-medium text-gray-900">Новый проект</p>
                  <p className="text-sm text-gray-500">Создать новый проект</p>
                </div>
              </div>
            </button>
            
            <button 
              className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
              data-testid="quick-action-new-invoice"
              onClick={() => navigate('/invoices?action=new')}
            >
              <div className="flex items-center">
                <FileText className="w-5 h-5 text-purple-600 mr-3" />
                <div>
                  <p className="font-medium text-gray-900">Создать счёт</p>
                  <p className="text-sm text-gray-500">Выставить счёт клиенту</p>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
