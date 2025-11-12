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
  const [filterType, setFilterType] = React.useState('all'); // all, manager, project
  const [selectedManager, setSelectedManager] = React.useState('');
  const [selectedProject, setSelectedProject] = React.useState('');
  const [periodMonths, setPeriodMonths] = React.useState(1);

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

  // Загрузка проектов для фильтра
  const { data: projectsData } = useQuery({
    queryKey: ['projects-list'],
    queryFn: () => fetch(process.env.REACT_APP_BACKEND_URL + '/api/projects/', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || 'dummy-token'}` }
    }).then(res => res.json()).then(data => data.projects),
  });

  // Детальная аналитика в зависимости от фильтра
  const { data: detailedAnalytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['detailed-analytics', filterType, selectedManager, selectedProject, periodMonths],
    queryFn: async () => {
      const baseUrl = process.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('token') || 'dummy-token';
      const headers = { 'Authorization': `Bearer ${token}` };
      
      if (filterType === 'manager' && selectedManager) {
        const res = await fetch(`${baseUrl}/api/reports/by-manager/${encodeURIComponent(selectedManager)}?period_months=${periodMonths}`, { headers });
        return await res.json();
      } else if (filterType === 'project' && selectedProject) {
        const res = await fetch(`${baseUrl}/api/reports/project/${selectedProject}?period_months=${periodMonths}`, { headers });
        return await res.json();
      } else {
        const res = await fetch(`${baseUrl}/api/reports/summary?period_months=${periodMonths}`, { headers });
        return await res.json();
      }
    },
    enabled: !!filterType,
  });

  // Churn Analysis данные
  const [churnPeriod, setChurnPeriod] = React.useState('monthly');
  const [churnMonths, setChurnMonths] = React.useState(12);
  
  const { data: churnData, isLoading: churnLoading } = useQuery({
    queryKey: ['churn-analysis', churnPeriod, churnMonths],
    queryFn: async () => {
      const baseUrl = process.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('token') || 'dummy-token';
      const res = await fetch(`${baseUrl}/api/reports/churn-analysis?period=${churnPeriod}&months=${churnMonths}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      return await res.json();
    },
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
          ) : (projectDistribution && projectDistribution.length > 0) ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={projectDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ status, count }) => 
                    `${status}: ${count}`
                  }
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {projectDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="py-8 text-center text-gray-500">
              Нет данных для отображения
            </div>
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
            {clientRevenue && clientRevenue.length > 0 ? (
              clientRevenue.map((client, index) => (
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

      {/* Детальная аналитика по проектам */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Детальная аналитика по проектам</h3>
        
        {/* Фильтры */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Тип отчета</label>
            <select
              value={filterType}
              onChange={(e) => {
                setFilterType(e.target.value);
                setSelectedManager('');
                setSelectedProject('');
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Все проекты (Сводный)</option>
              <option value="manager">По проект-менеджеру</option>
              <option value="project">По конкретному проекту</option>
            </select>
          </div>

          {filterType === 'manager' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Проект-менеджер</label>
              <select
                value={selectedManager}
                onChange={(e) => setSelectedManager(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Выберите менеджера</option>
                <option value="Прыгункова Елена">Прыгункова Елена</option>
                <option value="Гарасюта Александр">Гарасюта Александр</option>
              </select>
            </div>
          )}

          {filterType === 'project' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Проект</label>
              <select
                value={selectedProject}
                onChange={(e) => setSelectedProject(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Выберите проект</option>
                {projectsData?.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Период</label>
            <select
              value={periodMonths}
              onChange={(e) => setPeriodMonths(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={1}>1 месяц</option>
              <option value={3}>3 месяца</option>
              <option value={6}>6 месяцев</option>
              <option value={12}>12 месяцев</option>
            </select>
          </div>
        </div>

        {/* Результаты аналитики */}
        {analyticsLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : detailedAnalytics ? (
          <div className="space-y-6">
            {/* Заголовок отчета */}
            <div className="border-b pb-4">
              <h4 className="text-xl font-semibold text-gray-900">
                {filterType === 'all' && 'Сводный отчет по всем проектам'}
                {filterType === 'manager' && `Отчет по проект-менеджеру: ${detailedAnalytics.manager_name || selectedManager}`}
                {filterType === 'project' && `Отчет по проекту: ${detailedAnalytics.project_name || 'Не указан'}`}
              </h4>
              <p className="text-sm text-gray-600 mt-1">
                Период: {periodMonths} {periodMonths === 1 ? 'месяц' : periodMonths < 5 ? 'месяца' : 'месяцев'}
              </p>
            </div>

            {/* Метрики */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <p className="text-sm font-medium text-blue-900">Месячная выручка</p>
                <p className="text-2xl font-bold text-blue-700 mt-2">
                  {formatCurrency(detailedAnalytics.monthly_revenue || 0)}
                </p>
              </div>

              <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                <p className="text-sm font-medium text-green-900">Средний чек</p>
                <p className="text-2xl font-bold text-green-700 mt-2">
                  {formatCurrency(detailedAnalytics.average_check || 0)}
                </p>
              </div>

              <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                <p className="text-sm font-medium text-yellow-900">Ожидание платежей</p>
                <p className="text-2xl font-bold text-yellow-700 mt-2">
                  {formatCurrency(detailedAnalytics.pending_payments || 0)}
                </p>
              </div>

              <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                <p className="text-sm font-medium text-red-900">Просрочено платежей</p>
                <p className="text-2xl font-bold text-red-700 mt-2">
                  {formatCurrency(detailedAnalytics.overdue_payments || 0)}
                </p>
              </div>
            </div>

            {/* Дополнительная информация */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {filterType === 'all' && (
                  <div>
                    <p className="text-sm text-gray-600">Всего проектов</p>
                    <p className="text-lg font-semibold text-gray-900 mt-1">
                      {detailedAnalytics.total_projects || 0}
                    </p>
                  </div>
                )}
                {filterType === 'manager' && (
                  <div>
                    <p className="text-sm text-gray-600">Проектов менеджера</p>
                    <p className="text-lg font-semibold text-gray-900 mt-1">
                      {detailedAnalytics.total_projects || 0}
                    </p>
                  </div>
                )}
                <div>
                  <p className="text-sm text-gray-600">Общая выручка за период</p>
                  <p className="text-lg font-semibold text-gray-900 mt-1">
                    {formatCurrency(detailedAnalytics.total_revenue || 0)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Всего счетов</p>
                  <p className="text-lg font-semibold text-gray-900 mt-1">
                    {detailedAnalytics.total_invoices || 0}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Оплаченных счетов</p>
                  <p className="text-lg font-semibold text-gray-900 mt-1">
                    {detailedAnalytics.paid_invoices || 0}
                  </p>
                </div>
              </div>
            </div>

            {/* Проекты менеджера */}
            {filterType === 'manager' && detailedAnalytics.projects && detailedAnalytics.projects.length > 0 && (
              <div>
                <h5 className="text-lg font-semibold text-gray-900 mb-4">Проекты менеджера</h5>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Название</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Статус</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Бюджет</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Выручка</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {detailedAnalytics.projects.map((project) => (
                        <tr key={project.id}>
                          <td className="px-4 py-3 text-sm text-gray-900">{project.name}</td>
                          <td className="px-4 py-3 text-sm">
                            <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                              {getStatusLabel(project.status)}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-900">{formatCurrency(project.budget || 0)}</td>
                          <td className="px-4 py-3 text-sm font-semibold text-green-600">
                            {formatCurrency(project.revenue || 0)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Распределение по менеджерам для сводного отчета */}
            {filterType === 'all' && detailedAnalytics.projects_by_manager && (
              <div>
                <h5 className="text-lg font-semibold text-gray-900 mb-4">Распределение проектов по менеджерам</h5>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(detailedAnalytics.projects_by_manager).map(([manager, count]) => (
                    <div key={manager} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <p className="text-sm text-gray-600">{manager}</p>
                      <p className="text-xl font-bold text-gray-900 mt-1">{count} проектов</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            Выберите фильтры для просмотра аналитики
          </div>
        )}
      </div>

      {/* Анализ оттока клиентов (Churn Analysis) */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Анализ оттока клиентов</h3>
        
        {/* Фильтры */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Период группировки</label>
            <select
              value={churnPeriod}
              onChange={(e) => setChurnPeriod(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="monthly">По месяцам</option>
              <option value="yearly">По годам</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Количество периодов</label>
            <select
              value={churnMonths}
              onChange={(e) => setChurnMonths(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={6}>6 периодов</option>
              <option value={12}>12 периодов</option>
              <option value={24}>24 периода</option>
            </select>
          </div>
        </div>

        {/* Результаты */}
        {churnLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : churnData ? (
          <div className="space-y-6">
            {/* Общая статистика */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                <p className="text-sm font-medium text-green-900">Новых клиентов</p>
                <p className="text-2xl font-bold text-green-700 mt-2">{churnData.total_new}</p>
              </div>
              
              <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                <p className="text-sm font-medium text-red-900">Отвалились</p>
                <p className="text-2xl font-bold text-red-700 mt-2">{churnData.total_churned}</p>
              </div>
              
              <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                <p className="text-sm font-medium text-yellow-900">Приостановлены</p>
                <p className="text-2xl font-bold text-yellow-700 mt-2">{churnData.total_suspended}</p>
              </div>
              
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <p className="text-sm font-medium text-blue-900">Процент оттока</p>
                <p className="text-2xl font-bold text-blue-700 mt-2">{churnData.churn_rate}%</p>
              </div>
            </div>

            {/* График */}
            {churnData.data && churnData.data.length > 0 && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-md font-semibold text-gray-900 mb-4">Динамика по периодам</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={churnData.data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="new_clients" fill="#10b981" name="Новые" />
                    <Bar dataKey="churned_clients" fill="#ef4444" name="Отвалились" />
                    <Bar dataKey="suspended_clients" fill="#f59e0b" name="Приостановлены" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Таблица детализации */}
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Период</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Новые</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Отвалились</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Приостановлены</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Рост</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {churnData.data?.map((row, index) => (
                    <tr key={index}>
                      <td className="px-4 py-3 text-sm text-gray-900">{row.period}</td>
                      <td className="px-4 py-3 text-sm font-semibold text-green-600">{row.new_clients}</td>
                      <td className="px-4 py-3 text-sm font-semibold text-red-600">{row.churned_clients}</td>
                      <td className="px-4 py-3 text-sm font-semibold text-yellow-600">{row.suspended_clients}</td>
                      <td className="px-4 py-3 text-sm font-semibold">
                        <span className={row.net_growth >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {row.net_growth >= 0 ? '+' : ''}{row.net_growth}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}