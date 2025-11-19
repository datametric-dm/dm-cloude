import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Users,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  Activity
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { api } from '../lib/api';

const TeamLoad = () => {
  const [selectedMember, setSelectedMember] = useState(null);

  // Fetch team load overview
  const { data: overviewData, isLoading } = useQuery({
    queryKey: ['team-load-overview'],
    queryFn: async () => {
      const response = await api.get('/team-load/overview');
      return response.data;
    }
  });

  // Fetch detailed member data if selected
  const { data: memberData } = useQuery({
    queryKey: ['team-member-load', selectedMember],
    queryFn: async () => {
      if (!selectedMember) return null;
      const response = await api.get(`/team-load/member/${selectedMember}`);
      return response.data;
    },
    enabled: !!selectedMember
  });

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

  const overview = overviewData || {};
  const members = overview.members || [];

  // Chart data
  const chartData = members.map(member => ({
    name: member.name,
    workload: member.workload_percent || 0,
    capacity: member.available_hours || 0,
    allocated: member.allocated_hours || 0
  }));

  // Load distribution
  const loadDistribution = [
    { name: 'Недогружены', value: overview.underloaded_count || 0, color: '#10B981' },
    { name: 'Норма', value: overview.normal_count || 0, color: '#3B82F6' },
    { name: 'Перегружены', value: overview.overloaded_count || 0, color: '#EF4444' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Team Load</h1>
          <p className="text-sm text-gray-500 mt-1">Мониторинг загрузки команды</p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Всего сотрудников</span>
            <Users className="h-5 w-5 text-blue-500" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {overview.total_members || 0}
          </p>
        </div>

        <div className="bg-green-50 rounded-lg p-6 border border-green-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-green-900">Недогружены</span>
            <TrendingUp className="h-5 w-5 text-green-600" />
          </div>
          <p className="text-2xl font-bold text-green-900">
            {overview.underloaded_count || 0}
          </p>
          <p className="text-sm text-green-700 mt-1">
            {'<'} 70% загрузки
          </p>
        </div>

        <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-900">Норма</span>
            <CheckCircle className="h-5 w-5 text-blue-600" />
          </div>
          <p className="text-2xl font-bold text-blue-900">
            {overview.normal_count || 0}
          </p>
          <p className="text-sm text-blue-700 mt-1">
            70-100% загрузки
          </p>
        </div>

        <div className="bg-red-50 rounded-lg p-6 border border-red-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-red-900">Перегружены</span>
            <AlertTriangle className="h-5 w-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-red-900">
            {overview.overloaded_count || 0}
          </p>
          <p className="text-sm text-red-700 mt-1">
            {'>'} 100% загрузки
          </p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Workload Bar Chart */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Загрузка сотрудников</h2>
          
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="workload" fill="#3B82F6" name="Загрузка %" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Load Distribution Pie Chart */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Распределение нагрузки</h2>
          
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={loadDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {loadDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>

          <div className="mt-6 space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Средняя загрузка</span>
              <span className="font-semibold text-gray-900">
                {formatPercent(overview.avg_workload || 0)}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Общая доступность</span>
              <span className="font-semibold text-gray-900">
                {overview.total_capacity || 0} ч
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Выделено</span>
              <span className="font-semibold text-gray-900">
                {overview.total_allocated || 0} ч
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Team Members List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Детализация по сотрудникам</h2>
        </div>
        
        <div className="divide-y divide-gray-200">
          {members.map((member) => {
            const workloadPercent = member.workload_percent || 0;
            let statusColor = 'green';
            let statusText = 'Недогружен';
            
            if (workloadPercent >= 70 && workloadPercent <= 100) {
              statusColor = 'blue';
              statusText = 'Норма';
            } else if (workloadPercent > 100) {
              statusColor = 'red';
              statusText = 'Перегружен';
            }

            return (
              <div 
                key={member.id}
                className="p-6 hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => setSelectedMember(member.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0">
                        <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                          <span className="text-sm font-medium text-blue-600">
                            {member.name?.charAt(0) || 'U'}
                          </span>
                        </div>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">{member.name}</h3>
                        <p className="text-xs text-gray-500">{member.role || 'Сотрудник'}</p>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-6">
                    <div className="text-right">
                      <p className="text-xs text-gray-500">Загрузка</p>
                      <p className="text-sm font-semibold text-gray-900">
                        {formatPercent(workloadPercent)}
                      </p>
                    </div>

                    <div className="text-right">
                      <p className="text-xs text-gray-500">Часы</p>
                      <p className="text-sm font-semibold text-gray-900">
                        {member.allocated_hours || 0} / {member.available_hours || 0}
                      </p>
                    </div>

                    <div className="text-right">
                      <p className="text-xs text-gray-500">Проектов</p>
                      <p className="text-sm font-semibold text-gray-900">
                        {member.project_count || 0}
                      </p>
                    </div>

                    <div>
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-${statusColor}-100 text-${statusColor}-800`}>
                        {statusText}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        workloadPercent > 100 ? 'bg-red-600' :
                        workloadPercent >= 70 ? 'bg-blue-600' :
                        'bg-green-600'
                      }`}
                      style={{ width: `${Math.min(workloadPercent, 100)}%` }}
                    />
                  </div>
                </div>

                {/* Active Projects Preview */}
                {member.active_projects && member.active_projects.length > 0 && (
                  <div className="mt-3 flex items-center space-x-2">
                    <Clock className="h-4 w-4 text-gray-400" />
                    <div className="flex items-center space-x-2 text-xs text-gray-600">
                      {member.active_projects.slice(0, 3).map((project, idx) => (
                        <span key={idx} className="px-2 py-1 bg-gray-100 rounded">
                          {project}
                        </span>
                      ))}
                      {member.active_projects.length > 3 && (
                        <span className="text-gray-500">
                          +{member.active_projects.length - 3} еще
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default TeamLoad;
