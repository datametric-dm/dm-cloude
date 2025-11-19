import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  FolderOpen,
  AlertTriangle,
  Calendar,
  BarChart3,
  PieChart,
  Activity
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart as RePieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import api from '../lib/api';

const OwnerDashboard = () => {
  const [period, setPeriod] = useState('month');

  // Fetch owner dashboard data
  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['owner-dashboard', period],
    queryFn: async () => {
      const response = await api.get(`/dashboards/owner?period=${period}`);
      return response.data;
    }
  });

  // Fetch financial flow data
  const { data: financialData } = useQuery({
    queryKey: ['financial-flow', period],
    queryFn: async () => {
      const response = await api.get(`/financial-flow/summary?period=${period}`);
      return response.data;
    }
  });

  // Fetch team load data
  const { data: teamData } = useQuery({
    queryKey: ['team-load'],
    queryFn: async () => {
      const response = await api.get('/team-load/overview');
      return response.data;
    }
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const dashboard = dashboardData || {};
  const financial = financialData?.summary || {};
  const team = teamData || {};

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  // Format percentage
  const formatPercent = (value) => {
    return `${(value || 0).toFixed(1)}%`;
  };

  // KPI Cards
  const kpiCards = [
    {
      title: 'MRR Текущий',
      value: formatCurrency(dashboard.financial_metrics?.current_mrr),
      change: dashboard.financial_metrics?.mrr_growth,
      icon: DollarSign,
      color: 'bg-green-500'
    },
    {
      title: 'Активных Проектов',
      value: dashboard.project_metrics?.active_projects || 0,
      change: dashboard.project_metrics?.projects_growth,
      icon: FolderOpen,
      color: 'bg-blue-500'
    },
    {
      title: 'Активных Клиентов',
      value: dashboard.client_metrics?.active_clients || 0,
      change: dashboard.client_metrics?.clients_growth,
      icon: Users,
      color: 'bg-purple-500'
    },
    {
      title: 'Риск Проектов',
      value: `${dashboard.risk_metrics?.projects_at_risk || 0} шт.`,
      change: null,
      icon: AlertTriangle,
      color: 'bg-red-500',
      negative: true
    }
  ];

  // Financial chart data
  const financialChartData = financial.trend?.map((item, index) => ({
    name: item.period || `Период ${index + 1}`,
    planned: item.planned_income || 0,
    actual: item.actual_income || 0
  })) || [];

  // Team load chart data
  const teamLoadData = team.members?.map(member => ({
    name: member.name,
    load: member.workload_percent || 0,
    capacity: member.available_hours || 0
  })) || [];

  // Risk distribution
  const riskData = [
    { name: 'Низкий риск', value: dashboard.risk_metrics?.low_risk || 0, color: '#10B981' },
    { name: 'Средний риск', value: dashboard.risk_metrics?.medium_risk || 0, color: '#F59E0B' },
    { name: 'Высокий риск', value: dashboard.risk_metrics?.high_risk || 0, color: '#EF4444' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Owner Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Аналитика и ключевые метрики бизнеса</p>
        </div>
        
        {/* Period Selector */}
        <div className="flex items-center space-x-2">
          {['week', 'month', 'quarter', 'year'].map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                period === p
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
              }`}
            >
              {p === 'week' && 'Неделя'}
              {p === 'month' && 'Месяц'}
              {p === 'quarter' && 'Квартал'}
              {p === 'year' && 'Год'}
            </button>
          ))}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiCards.map((card, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm text-gray-600 mb-1">{card.title}</p>
                <p className="text-2xl font-bold text-gray-900">{card.value}</p>
                {card.change !== null && card.change !== undefined && (
                  <div className={`flex items-center mt-2 text-sm ${
                    card.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {card.change >= 0 ? (
                      <TrendingUp className="h-4 w-4 mr-1" />
                    ) : (
                      <TrendingDown className="h-4 w-4 mr-1" />
                    )}
                    {formatPercent(Math.abs(card.change))}
                  </div>
                )}
              </div>
              <div className={`${card.color} p-3 rounded-lg`}>
                <card.icon className="h-6 w-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Financial Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Financial Flow Chart */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Финансовый поток</h2>
            <BarChart3 className="h-5 w-5 text-gray-400" />
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={financialChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip 
                formatter={(value) => formatCurrency(value)}
                labelStyle={{ color: '#000' }}
              />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="planned" 
                stackId="1" 
                stroke="#3B82F6" 
                fill="#93C5FD" 
                name="План"
              />
              <Area 
                type="monotone" 
                dataKey="actual" 
                stackId="2" 
                stroke="#10B981" 
                fill="#6EE7B7" 
                name="Факт"
              />
            </AreaChart>
          </ResponsiveContainer>

          {/* Financial Summary */}
          <div className="grid grid-cols-2 gap-4 mt-6 pt-6 border-t border-gray-200">
            <div>
              <p className="text-xs text-gray-500 mb-1">Прогноз MRR</p>
              <p className="text-lg font-semibold text-gray-900">
                {formatCurrency(dashboard.financial_metrics?.forecast_mrr)}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Средний чек</p>
              <p className="text-lg font-semibold text-gray-900">
                {formatCurrency(dashboard.financial_metrics?.avg_check)}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Поступления (7 дней)</p>
              <p className="text-lg font-semibold text-green-600">
                {formatCurrency(dashboard.financial_metrics?.week_received)}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Просрочка</p>
              <p className="text-lg font-semibold text-red-600">
                {formatCurrency(dashboard.financial_metrics?.total_overdue)}
              </p>
            </div>
          </div>
        </div>

        {/* Risk Distribution */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Распределение рисков</h2>
            <PieChart className="h-5 w-5 text-gray-400" />
          </div>

          <ResponsiveContainer width="100%" height={300}>
            <RePieChart>
              <Pie
                data={riskData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {riskData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </RePieChart>
          </ResponsiveContainer>

          {/* Risk Summary */}
          <div className="space-y-3 mt-6 pt-6 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Проектов в зоне риска</span>
              <span className="text-sm font-semibold text-red-600">
                {dashboard.risk_metrics?.projects_at_risk || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Клиентов с просрочкой</span>
              <span className="text-sm font-semibold text-orange-600">
                {dashboard.financial_metrics?.clients_in_overdue || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Общий риск портфеля</span>
              <span className="text-sm font-semibold text-gray-900">
                {formatPercent(dashboard.risk_metrics?.portfolio_risk)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Team and Projects */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Team Load */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Загрузка команды</h2>
            <Activity className="h-5 w-5 text-gray-400" />
          </div>

          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={teamLoadData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="load" fill="#3B82F6" name="Загрузка %" />
            </BarChart>
          </ResponsiveContainer>

          <div className="grid grid-cols-2 gap-4 mt-6 pt-6 border-t border-gray-200">
            <div>
              <p className="text-xs text-gray-500 mb-1">Средняя загрузка</p>
              <p className="text-lg font-semibold text-gray-900">
                {formatPercent(team.avg_workload || 0)}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Перегруженных</p>
              <p className="text-lg font-semibold text-orange-600">
                {team.overloaded_count || 0}
              </p>
            </div>
          </div>
        </div>

        {/* Project Pipeline */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Проектный pipeline</h2>
            <FolderOpen className="h-5 w-5 text-gray-400" />
          </div>

          <div className="space-y-4">
            {/* Pipeline stages */}
            <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-gray-900">В работе</p>
                <p className="text-xs text-gray-500 mt-1">Активные проекты</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-blue-600">
                  {dashboard.project_metrics?.active_projects || 0}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {formatCurrency(dashboard.project_metrics?.active_budget || 0)}
                </p>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-gray-900">Завершено</p>
                <p className="text-xs text-gray-500 mt-1">За выбранный период</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-green-600">
                  {dashboard.project_metrics?.completed_projects || 0}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Success Rate: {formatPercent(dashboard.project_metrics?.success_rate)}
                </p>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-orange-50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-gray-900">Планируется</p>
                <p className="text-xs text-gray-500 mt-1">В следующем периоде</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-orange-600">
                  {dashboard.project_metrics?.planned_projects || 0}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {formatCurrency(dashboard.project_metrics?.planned_budget || 0)}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow-sm p-6 text-white">
        <h2 className="text-lg font-semibold mb-4">Требуют внимания</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white bg-opacity-10 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Просроченные счета</span>
              <AlertTriangle className="h-5 w-5" />
            </div>
            <p className="text-2xl font-bold">
              {dashboard.financial_metrics?.overdue_count || 0}
            </p>
          </div>
          
          <div className="bg-white bg-opacity-10 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Проблемные проекты</span>
              <AlertTriangle className="h-5 w-5" />
            </div>
            <p className="text-2xl font-bold">
              {dashboard.project_metrics?.problematic_projects || 0}
            </p>
          </div>
          
          <div className="bg-white bg-opacity-10 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Клиенты в зоне оттока</span>
              <AlertTriangle className="h-5 w-5" />
            </div>
            <p className="text-2xl font-bold">
              {dashboard.client_metrics?.churn_risk || 0}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OwnerDashboard;
