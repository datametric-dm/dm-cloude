import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Calendar,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { api } from '../lib/api';

const FinancialFlow = () => {
  const [period, setPeriod] = useState('month');

  // Fetch financial flow summary
  const { data: summaryData, isLoading } = useQuery({
    queryKey: ['financial-flow-summary', period],
    queryFn: async () => {
      const response = await api.get(`/financial-flow/summary?period=${period}`);
      return response.data;
    }
  });

  // Fetch comparison data
  const { data: comparisonData } = useQuery({
    queryKey: ['financial-flow-comparison', period],
    queryFn: async () => {
      const response = await api.get(`/financial-flow/comparison?period=${period}`);
      return response.data;
    }
  });

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  const formatPercent = (value) => {
    return `${(value || 0).toFixed(1)}%`;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const summary = summaryData?.summary || {};
  const trend = summaryData?.summary?.trend || [];
  const comparison = comparisonData?.comparison || {};

  // Chart data
  const chartData = trend.map((item, index) => ({
    name: item.period || `Период ${index + 1}`,
    planned: item.planned_income || 0,
    actual: item.actual_income || 0,
    expenses: item.expenses || 0
  }));

  // Calculate variance
  const variance = summary.total_actual - summary.total_planned;
  const variancePercent = summary.total_planned > 0 
    ? ((variance / summary.total_planned) * 100) 
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Financial Flow</h1>
          <p className="text-sm text-gray-500 mt-1">Анализ плановых и фактических поступлений</p>
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

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">План доход</span>
            <Calendar className="h-5 w-5 text-blue-500" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {formatCurrency(summary.total_planned)}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Факт доход</span>
            <DollarSign className="h-5 w-5 text-green-500" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {formatCurrency(summary.total_actual)}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Отклонение</span>
            {variance >= 0 ? (
              <TrendingUp className="h-5 w-5 text-green-500" />
            ) : (
              <TrendingDown className="h-5 w-5 text-red-500" />
            )}
          </div>
          <p className={`text-2xl font-bold ${variance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {formatCurrency(Math.abs(variance))}
          </p>
          <p className={`text-sm mt-1 ${variance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {variancePercent >= 0 ? '+' : ''}{formatPercent(variancePercent)}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Выполнение плана</span>
            <CheckCircle className="h-5 w-5 text-purple-500" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {formatPercent(summary.achievement_rate || 0)}
          </p>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div
              className="bg-purple-600 h-2 rounded-full transition-all"
              style={{ width: `${Math.min(summary.achievement_rate || 0, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Main Chart */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">План vs Факт</h2>
        
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={chartData}>
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
              name="Плановый доход"
            />
            <Area 
              type="monotone" 
              dataKey="actual" 
              stackId="2" 
              stroke="#10B981" 
              fill="#6EE7B7" 
              name="Фактический доход"
            />
            <Area 
              type="monotone" 
              dataKey="expenses" 
              stackId="3" 
              stroke="#EF4444" 
              fill="#FCA5A5" 
              name="Расходы"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* By Project */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">По проектам</h2>
          
          <div className="space-y-3">
            {comparison.by_project?.map((project, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{project.name}</p>
                  <div className="flex items-center space-x-4 mt-1">
                    <span className="text-xs text-gray-500">
                      План: {formatCurrency(project.planned)}
                    </span>
                    <span className="text-xs text-gray-500">
                      Факт: {formatCurrency(project.actual)}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-sm font-semibold ${
                    project.actual >= project.planned ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatPercent((project.actual / project.planned) * 100)}
                  </p>
                </div>
              </div>
            )) || <p className="text-sm text-gray-500">Нет данных</p>}
          </div>
        </div>

        {/* By Client */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">По клиентам</h2>
          
          <div className="space-y-3">
            {comparison.by_client?.map((client, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{client.name}</p>
                  <div className="flex items-center space-x-4 mt-1">
                    <span className="text-xs text-gray-500">
                      План: {formatCurrency(client.planned)}
                    </span>
                    <span className="text-xs text-gray-500">
                      Факт: {formatCurrency(client.actual)}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-sm font-semibold ${
                    client.actual >= client.planned ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatPercent((client.actual / client.planned) * 100)}
                  </p>
                </div>
              </div>
            )) || <p className="text-sm text-gray-500">Нет данных</p>}
          </div>
        </div>
      </div>

      {/* Status Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-green-50 rounded-lg p-6 border border-green-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-green-900">В срок</span>
            <CheckCircle className="h-5 w-5 text-green-600" />
          </div>
          <p className="text-2xl font-bold text-green-900">
            {summary.on_time_count || 0}
          </p>
          <p className="text-sm text-green-700 mt-1">
            {formatCurrency(summary.on_time_amount || 0)}
          </p>
        </div>

        <div className="bg-yellow-50 rounded-lg p-6 border border-yellow-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-yellow-900">Ожидается</span>
            <Clock className="h-5 w-5 text-yellow-600" />
          </div>
          <p className="text-2xl font-bold text-yellow-900">
            {summary.pending_count || 0}
          </p>
          <p className="text-sm text-yellow-700 mt-1">
            {formatCurrency(summary.pending_amount || 0)}
          </p>
        </div>

        <div className="bg-red-50 rounded-lg p-6 border border-red-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-red-900">Просрочено</span>
            <AlertCircle className="h-5 w-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-red-900">
            {summary.overdue_count || 0}
          </p>
          <p className="text-sm text-red-700 mt-1">
            {formatCurrency(summary.overdue_amount || 0)}
          </p>
        </div>
      </div>
    </div>
  );
};

export default FinancialFlow;
