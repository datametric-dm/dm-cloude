import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { BarChart3, TrendingUp, Users, FileText, Send } from 'lucide-react';
import { StatsCard } from '../components/ui/stats-card';
import { LoadingCard } from '../components/ui/loading-spinner';
import { reportsApi, telegramApi } from '../lib/api';
import { formatCurrency } from '../lib/utils';
import { toast } from 'sonner';
import { useMutation } from '@tanstack/react-query';

export default function Reports() {
  const { data: dashboardStats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => reportsApi.getDashboard().then(res => res.data),
  });

  const { data: monthlyRevenue, isLoading: revenueLoading } = useQuery({
    queryKey: ['monthly-revenue'],
    queryFn: () => reportsApi.getMonthlyRevenue().then(res => res.data),
  });

  const { data: projectDistribution, isLoading: distributionLoading } = useQuery({
    queryKey: ['project-distribution'],
    queryFn: () => reportsApi.getProjectDistribution().then(res => res.data),
  });

  const { data: clientRevenue, isLoading: clientRevenueLoading } = useQuery({
    queryKey: ['client-revenue'],
    queryFn: () => reportsApi.getClientRevenue({ limit: 10 }).then(res => res.data),
  });

  const sendReportMutation = useMutation({
    mutationFn: telegramApi.sendDailyReport,
    onSuccess: () => {
      toast.success('Ежедневный отчёт отправлен в Telegram');
    },
    onError: () => {
      toast.error('Ошибка отправки отчёта');
    },
  });

  const COLORS = ['#3B82F6', '#EF4444', '#F59E0B', '#10B981', '#8B5CF6', '#F97316'];

  if (statsLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Отчеты</h1>
        </div>
        <LoadingCard />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Заголовок и действия */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Отчеты и аналитика</h1>
          <p className="text-gray-600 mt-1">
            Детальная статистика по проектам, клиентам и финансам
          </p>
        </div>
        
        <button
          onClick={() => sendReportMutation.mutate()}
          disabled={sendReportMutation.isPending}
          className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-green-700 transition-colors disabled:opacity-50"
          data-testid="send-telegram-report-btn"
        >
          <Send className="w-5 h-5" />
          <span>
            {sendReportMutation.isPending ? 'Отправляем...' : 'Отправить отчёт в Telegram'}
          </span>
        </button>
      </div>

      {/* Основные метрики */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Всего клиентов"
          value={dashboardStats?.total_clients || 0}
          icon={Users}
          data-testid="reports-total-clients"
        />
        
        <StatsCard
          title="Активные проекты"
          value={dashboardStats?.active_projects || 0}
          subtitle={`из ${dashboardStats?.total_projects || 0} общих`}
          icon={BarChart3}
          data-testid="reports-active-projects"
        />
        
        <StatsCard
          title="Общая выручка"
          value={formatCurrency(dashboardStats?.total_revenue || 0)}
          icon={TrendingUp}
          data-testid="reports-total-revenue"
        />
        
        <StatsCard
          title="Неоплаченные счета"
          value={dashboardStats?.unpaid_invoices || 0}
          icon={FileText}
          className={dashboardStats?.unpaid_invoices > 0 ? "border-yellow-200 bg-yellow-50" : ""}
          data-testid="reports-unpaid-invoices"
        />
      </div>

      {/* Графики */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Месячная выручка */}
        <div className="bg-white rounded-lg border border-gray-200 p-6" data-testid="monthly-revenue-chart">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Месячная выручка (2025)
          </h3>
          {revenueLoading ? (
            <div className="h-64 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={monthlyRevenue || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="month" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={60}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip 
                  formatter={(value) => [formatCurrency(value), 'Выручка']}
                  labelFormatter={(label) => `Месяц: ${label}`}
                />
                <Bar dataKey="revenue" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Распределение проектов по статусам */}
        <div className="bg-white rounded-lg border border-gray-200 p-6" data-testid="project-distribution-chart">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Проекты по статусам
          </h3>
          {distributionLoading ? (
            <div className="h-64 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={projectDistribution?.distribution || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ status, count, percent }) => 
                    `${getStatusLabel(status)}: ${count} (${(percent * 100).toFixed(0)}%)`
                  }
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {(projectDistribution?.distribution || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Топ клиентов по выручке */}
      <div className="bg-white rounded-lg border border-gray-200 p-6" data-testid="top-clients-revenue">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Топ клиентов по выручке
        </h3>
        {clientRevenueLoading ? (
          <div className="py-8 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {clientRevenue?.client_revenue?.length > 0 ? (
              clientRevenue.client_revenue.map((client, index) => (
                <div key={client.client_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-blue-600">
                        {index + 1}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{client.name}</p>
                      {client.company && (
                        <p className="text-sm text-gray-500">{client.company}</p>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">
                      {formatCurrency(client.total_revenue)}
                    </p>
                    <p className="text-sm text-gray-500">выручка</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                Данные о выручке отсутствуют
              </div>
            )}
          </div>
        )}
      </div>

      {/* Дополнительная статистика */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h4 className="text-md font-semibold text-gray-900 mb-2">
            Средний чек проекта
          </h4>
          <p className="text-2xl font-bold text-blue-600">
            {dashboardStats?.total_projects > 0 
              ? formatCurrency((dashboardStats?.total_revenue || 0) / dashboardStats.total_projects)
              : formatCurrency(0)
            }
          </p>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h4 className="text-md font-semibold text-gray-900 mb-2">
            Ожидается к поступлению
          </h4>
          <p className="text-2xl font-bold text-green-600">
            {formatCurrency(dashboardStats?.pending_revenue || 0)}
          </p>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h4 className="text-md font-semibold text-gray-900 mb-2">
            Просрочено платежей
          </h4>
          <p className="text-2xl font-bold text-red-600">
            {formatCurrency(dashboardStats?.overdue_amount || 0)}
          </p>
        </div>
      </div>
    </div>
  );

  function getStatusLabel(status) {
    const statusMap = {
      planning: 'Планирование',
      in_progress: 'В процессе',
      review: 'На проверке',
      completed: 'Завершён',
      on_hold: 'Приостановлен',
      cancelled: 'Отменён',
    };
    return statusMap[status] || status;
  }
}