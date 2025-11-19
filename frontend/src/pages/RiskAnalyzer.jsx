import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Shield,
  AlertCircle,
  CheckCircle,
  Clock,
  DollarSign,
  Users,
  FolderOpen,
  XCircle
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';
import { api } from '../lib/api';

const RiskAnalyzer = () => {
  const [period, setPeriod] = useState('month');

  // Fetch risk overview
  const { data: riskData, isLoading } = useQuery({
    queryKey: ['risk-analyzer', period],
    queryFn: async () => {
      const response = await api.get(`/risk-analyzer/overview?period=${period}`);
      return response.data;
    }
  });

  // Fetch risk recommendations
  const { data: recommendationsData } = useQuery({
    queryKey: ['risk-recommendations'],
    queryFn: async () => {
      const response = await api.get('/risk-analyzer/recommendations');
      return response.data;
    }
  });

  const formatPercent = (value) => {
    return `${(value || 0).toFixed(1)}%`;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const overview = riskData?.overview || {};
  const projects = riskData?.projects || [];
  const clients = riskData?.clients || [];
  const recommendations = recommendationsData?.recommendations || [];

  // Risk distribution
  const riskDistribution = [
    { name: 'Низкий', value: overview.low_risk_count || 0, color: '#10B981' },
    { name: 'Средний', value: overview.medium_risk_count || 0, color: '#F59E0B' },
    { name: 'Высокий', value: overview.high_risk_count || 0, color: '#EF4444' },
    { name: 'Критический', value: overview.critical_risk_count || 0, color: '#7C3AED' }
  ];

  // Risk factors radar
  const riskFactors = [
    { factor: 'Бюджет', score: overview.budget_risk || 0 },
    { factor: 'Сроки', score: overview.timeline_risk || 0 },
    { factor: 'Команда', score: overview.team_risk || 0 },
    { factor: 'Клиент', score: overview.client_risk || 0 },
    { factor: 'Качество', score: overview.quality_risk || 0 }
  ];

  // Get risk level color
  const getRiskColor = (level) => {
    switch(level) {
      case 'low': return 'green';
      case 'medium': return 'yellow';
      case 'high': return 'red';
      case 'critical': return 'purple';
      default: return 'gray';
    }
  };

  const getRiskIcon = (level) => {
    switch(level) {
      case 'low': return CheckCircle;
      case 'medium': return AlertCircle;
      case 'high': return AlertTriangle;
      case 'critical': return XCircle;
      default: return Shield;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Risk Analyzer</h1>
          <p className="text-sm text-gray-500 mt-1">Анализ и мониторинг рисков портфеля</p>
        </div>
        
        {/* Period Selector */}
        <div className="flex items-center space-x-2">
          {['week', 'month', 'quarter'].map((p) => (
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
            </button>
          ))}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Общий риск</span>
            <Shield className="h-5 w-5 text-blue-500" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {formatPercent(overview.overall_risk_score)}
          </p>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div
              className={`h-2 rounded-full ${
                overview.overall_risk_score > 75 ? 'bg-red-600' :
                overview.overall_risk_score > 50 ? 'bg-yellow-600' :
                'bg-green-600'
              }`}
              style={{ width: `${overview.overall_risk_score || 0}%` }}
            />
          </div>
        </div>

        <div className="bg-red-50 rounded-lg p-6 border border-red-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-red-900">Критические риски</span>
            <XCircle className="h-5 w-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-red-900">
            {overview.critical_risk_count || 0}
          </p>
          <p className="text-sm text-red-700 mt-1">
            {formatCurrency(overview.critical_risk_value)}
          </p>
        </div>

        <div className="bg-yellow-50 rounded-lg p-6 border border-yellow-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-yellow-900">Высокие риски</span>
            <AlertTriangle className="h-5 w-5 text-yellow-600" />
          </div>
          <p className="text-2xl font-bold text-yellow-900">
            {overview.high_risk_count || 0}
          </p>
          <p className="text-sm text-yellow-700 mt-1">
            {formatCurrency(overview.high_risk_value)}
          </p>
        </div>

        <div className="bg-green-50 rounded-lg p-6 border border-green-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-green-900">Под контролем</span>
            <CheckCircle className="h-5 w-5 text-green-600" />
          </div>
          <p className="text-2xl font-bold text-green-900">
            {overview.low_risk_count || 0}
          </p>
          <p className="text-sm text-green-700 mt-1">
            {formatPercent(overview.low_risk_percent)}
          </p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Distribution */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Распределение рисков</h2>
          
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {riskDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>

          <div className="grid grid-cols-2 gap-4 mt-6 pt-6 border-t border-gray-200">
            <div>
              <p className="text-xs text-gray-500 mb-1">Всего объектов</p>
              <p className="text-lg font-semibold text-gray-900">
                {overview.total_items || 0}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Требуют внимания</p>
              <p className="text-lg font-semibold text-red-600">
                {(overview.high_risk_count || 0) + (overview.critical_risk_count || 0)}
              </p>
            </div>
          </div>
        </div>

        {/* Risk Factors Radar */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Факторы риска</h2>
          
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={riskFactors}>
              <PolarGrid />
              <PolarAngleAxis dataKey="factor" />
              <PolarRadiusAxis angle={90} domain={[0, 100]} />
              <Radar 
                name="Уровень риска" 
                dataKey="score" 
                stroke="#EF4444" 
                fill="#EF4444" 
                fillOpacity={0.6} 
              />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-500 mb-2">Критические факторы:</p>
            <div className="flex flex-wrap gap-2">
              {riskFactors
                .filter(f => f.score > 70)
                .map((factor, idx) => (
                  <span key={idx} className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded">
                    {factor.factor}
                  </span>
                ))}
            </div>
          </div>
        </div>
      </div>

      {/* At-Risk Projects */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Проекты в зоне риска</h2>
        </div>
        
        <div className="divide-y divide-gray-200">
          {projects.length > 0 ? projects.map((project) => {
            const RiskIcon = getRiskIcon(project.risk_level);
            const color = getRiskColor(project.risk_level);
            
            return (
              <div key={project.id} className="p-6 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <RiskIcon className={`h-5 w-5 text-${color}-600`} />
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">{project.name}</h3>
                        <p className="text-xs text-gray-500 mt-1">{project.client_name}</p>
                      </div>
                    </div>

                    {/* Risk Factors */}
                    <div className="mt-3 flex flex-wrap gap-2">
                      {project.risk_factors?.map((factor, idx) => (
                        <span key={idx} className={`px-2 py-1 bg-${color}-100 text-${color}-800 text-xs rounded`}>
                          {factor}
                        </span>
                      ))}
                    </div>

                    {/* Indicators */}
                    <div className="mt-3 grid grid-cols-4 gap-4 text-xs">
                      <div>
                        <p className="text-gray-500">Бюджет</p>
                        <p className="font-semibold text-gray-900">{formatCurrency(project.budget)}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Прогресс</p>
                        <p className="font-semibold text-gray-900">{project.progress || 0}%</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Срок</p>
                        <p className="font-semibold text-gray-900">
                          {project.days_remaining > 0 ? `${project.days_remaining}д` : 'Просрочен'}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">Риск</p>
                        <p className={`font-semibold text-${color}-600`}>
                          {formatPercent(project.risk_score)}
                        </p>
                      </div>
                    </div>
                  </div>

                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-${color}-100 text-${color}-800`}>
                    {project.risk_level === 'low' && 'Низкий'}
                    {project.risk_level === 'medium' && 'Средний'}
                    {project.risk_level === 'high' && 'Высокий'}
                    {project.risk_level === 'critical' && 'Критический'}
                  </span>
                </div>
              </div>
            );
          }) : (
            <div className="p-8 text-center">
              <CheckCircle className="h-12 w-12 text-green-300 mx-auto mb-2" />
              <p className="text-sm text-gray-500">Проектов в зоне риска не обнаружено</p>
            </div>
          )}
        </div>
      </div>

      {/* At-Risk Clients */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Клиенты в зоне риска оттока</h2>
        </div>
        
        <div className="divide-y divide-gray-200">
          {clients.length > 0 ? clients.map((client) => (
            <div key={client.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="text-sm font-medium text-gray-900">{client.name}</h3>
                  
                  <div className="mt-2 flex items-center space-x-6 text-xs text-gray-600">
                    <div className="flex items-center">
                      <DollarSign className="h-4 w-4 mr-1" />
                      LTV: {formatCurrency(client.lifetime_value)}
                    </div>
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 mr-1" />
                      Последний контакт: {client.days_since_last_contact}д назад
                    </div>
                    <div className="flex items-center">
                      <FolderOpen className="h-4 w-4 mr-1" />
                      Проектов: {client.project_count}
                    </div>
                  </div>

                  <div className="mt-2 flex flex-wrap gap-2">
                    {client.churn_indicators?.map((indicator, idx) => (
                      <span key={idx} className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded">
                        {indicator}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="text-right">
                  <p className="text-xs text-gray-500">Риск оттока</p>
                  <p className="text-lg font-semibold text-red-600">
                    {formatPercent(client.churn_risk)}
                  </p>
                </div>
              </div>
            </div>
          )) : (
            <div className="p-8 text-center">
              <CheckCircle className="h-12 w-12 text-green-300 mx-auto mb-2" />
              <p className="text-sm text-gray-500">Клиентов в зоне оттока не обнаружено</p>
            </div>
          )}
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow-sm p-6 text-white">
        <h2 className="text-lg font-semibold mb-4">Рекомендации по снижению рисков</h2>
        
        <div className="space-y-3">
          {recommendations.length > 0 ? recommendations.map((rec, index) => (
            <div key={index} className="flex items-start space-x-3 bg-white bg-opacity-10 rounded-lg p-4">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-white bg-opacity-20 flex items-center justify-center">
                  <span className="text-sm font-bold">{index + 1}</span>
                </div>
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">{rec.title}</p>
                <p className="text-sm opacity-90 mt-1">{rec.description}</p>
                {rec.priority && (
                  <span className={`inline-block mt-2 px-2 py-1 text-xs rounded ${
                    rec.priority === 'high' ? 'bg-red-500' :
                    rec.priority === 'medium' ? 'bg-yellow-500' :
                    'bg-green-500'
                  }`}>
                    Приоритет: {rec.priority === 'high' ? 'Высокий' : rec.priority === 'medium' ? 'Средний' : 'Низкий'}
                  </span>
                )}
              </div>
            </div>
          )) : (
            <div className="text-center py-4">
              <p className="text-sm opacity-90">Все риски под контролем, рекомендаций нет</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RiskAnalyzer;
