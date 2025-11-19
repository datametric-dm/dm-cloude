import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Building2,
  Mail,
  Phone,
  MapPin,
  Calendar,
  DollarSign,
  TrendingUp,
  TrendingDown,
  FileText,
  FolderOpen,
  CreditCard,
  MessageSquare,
  Clock,
  CheckCircle,
  AlertCircle,
  User
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { api } from '../lib/api';

const Client360 = () => {
  const [selectedClientId, setSelectedClientId] = useState(null);

  // Fetch all clients
  const { data: clientsData, isLoading: clientsLoading } = useQuery({
    queryKey: ['clients-list'],
    queryFn: async () => {
      const response = await api.get('/clients');
      return response.data;
    }
  });

  // Fetch client 360 data
  const { data: client360Data, isLoading: client360Loading } = useQuery({
    queryKey: ['client-360', selectedClientId],
    queryFn: async () => {
      if (!selectedClientId) return null;
      const response = await api.get(`/client-360/${selectedClientId}`);
      return response.data;
    },
    enabled: !!selectedClientId
  });

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  const clients = clientsData?.clients || [];
  const client360 = client360Data?.client || {};
  const history = client360Data?.history || {};
  const projects = client360Data?.projects || [];
  const invoices = client360Data?.invoices || [];
  const interactions = client360Data?.interactions || [];

  // Select first client by default
  React.useEffect(() => {
    if (clients.length > 0 && !selectedClientId) {
      setSelectedClientId(clients[0].id);
    }
  }, [clients, selectedClientId]);

  if (clientsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Revenue trend data
  const revenueTrend = history.revenue_trend?.map((item, index) => ({
    month: item.period || `M${index + 1}`,
    revenue: item.amount || 0
  })) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Client 360</h1>
          <p className="text-sm text-gray-500 mt-1">Полная информация о клиенте</p>
        </div>

        {/* Client Selector */}
        <select
          value={selectedClientId || ''}
          onChange={(e) => setSelectedClientId(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Выберите клиента</option>
          {clients.map((client) => (
            <option key={client.id} value={client.id}>
              {client.name}
            </option>
          ))}
        </select>
      </div>

      {!selectedClientId ? (
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <Building2 className="h-12 w-12 text-gray-400" />
          <p className="text-sm text-gray-500">Выберите клиента для просмотра</p>
        </div>
      ) : client360Loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <>
          {/* Client Header Card */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-4">
                <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center">
                  <Building2 className="h-8 w-8 text-blue-600" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{client360.name}</h2>
                  <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                    {client360.email && (
                      <div className="flex items-center">
                        <Mail className="h-4 w-4 mr-1" />
                        {client360.email}
                      </div>
                    )}
                    {client360.phone && (
                      <div className="flex items-center">
                        <Phone className="h-4 w-4 mr-1" />
                        {client360.phone}
                      </div>
                    )}
                    {client360.address && (
                      <div className="flex items-center">
                        <MapPin className="h-4 w-4 mr-1" />
                        {client360.address}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Status Badge */}
              <div>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  client360.status === 'active' ? 'bg-green-100 text-green-800' :
                  client360.status === 'inactive' ? 'bg-gray-100 text-gray-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {client360.status === 'active' && 'Активный'}
                  {client360.status === 'inactive' && 'Неактивный'}
                  {client360.status === 'at_risk' && 'В зоне риска'}
                </span>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-200">
              <div>
                <p className="text-xs text-gray-500 mb-1">Клиент с</p>
                <div className="flex items-center">
                  <Calendar className="h-4 w-4 text-gray-400 mr-1" />
                  <p className="text-sm font-semibold text-gray-900">
                    {client360.created_at ? new Date(client360.created_at).toLocaleDateString('ru-RU') : 'N/A'}
                  </p>
                </div>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Всего проектов</p>
                <div className="flex items-center">
                  <FolderOpen className="h-4 w-4 text-gray-400 mr-1" />
                  <p className="text-sm font-semibold text-gray-900">
                    {history.total_projects || 0}
                  </p>
                </div>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Общий доход</p>
                <div className="flex items-center">
                  <DollarSign className="h-4 w-4 text-gray-400 mr-1" />
                  <p className="text-sm font-semibold text-gray-900">
                    {formatCurrency(history.total_revenue)}
                  </p>
                </div>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">LTV</p>
                <div className="flex items-center">
                  <TrendingUp className="h-4 w-4 text-gray-400 mr-1" />
                  <p className="text-sm font-semibold text-gray-900">
                    {formatCurrency(history.lifetime_value)}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Активные проекты</span>
                <FolderOpen className="h-5 w-5 text-blue-500" />
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {history.active_projects || 0}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Неоплаченные счета</span>
                <FileText className="h-5 w-5 text-orange-500" />
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {history.unpaid_invoices || 0}
              </p>
              <p className="text-sm text-orange-600 mt-1">
                {formatCurrency(history.unpaid_amount)}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Средний чек</span>
                <CreditCard className="h-5 w-5 text-green-500" />
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(history.avg_check)}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Health Score</span>
                <TrendingUp className="h-5 w-5 text-purple-500" />
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {history.health_score || 0}/100
              </p>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-purple-600 h-2 rounded-full transition-all"
                  style={{ width: `${history.health_score || 0}%` }}
                />
              </div>
            </div>
          </div>

          {/* Revenue Trend Chart */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">Динамика дохода</h2>
            
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={revenueTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Area 
                  type="monotone" 
                  dataKey="revenue" 
                  stroke="#3B82F6" 
                  fill="#93C5FD" 
                  name="Доход"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Projects and Invoices */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Active Projects */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Активные проекты</h2>
              </div>
              <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                {projects.length > 0 ? projects.map((project) => (
                  <div key={project.id} className="p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-sm font-medium text-gray-900">{project.name}</h3>
                        <div className="flex items-center space-x-3 mt-1 text-xs text-gray-500">
                          <span className={`px-2 py-1 rounded ${
                            project.status === 'active' ? 'bg-green-100 text-green-800' :
                            project.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {project.status}
                          </span>
                          <span>{formatCurrency(project.budget)}</span>
                        </div>
                      </div>
                      {project.progress !== undefined && (
                        <span className="text-sm font-semibold text-gray-900">
                          {project.progress}%
                        </span>
                      )}
                    </div>
                    {project.progress !== undefined && (
                      <div className="w-full bg-gray-200 rounded-full h-1.5 mt-2">
                        <div
                          className="bg-blue-600 h-1.5 rounded-full"
                          style={{ width: `${project.progress}%` }}
                        />
                      </div>
                    )}
                  </div>
                )) : (
                  <div className="p-8 text-center">
                    <FolderOpen className="h-12 w-12 text-gray-300 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">Нет активных проектов</p>
                  </div>
                )}
              </div>
            </div>

            {/* Recent Invoices */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Последние счета</h2>
              </div>
              <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                {invoices.length > 0 ? invoices.map((invoice) => (
                  <div key={invoice.id} className="p-4 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          Счет #{invoice.invoice_number}
                        </p>
                        <div className="flex items-center space-x-3 mt-1 text-xs text-gray-500">
                          <span className="flex items-center">
                            <Calendar className="h-3 w-3 mr-1" />
                            {invoice.date ? new Date(invoice.date).toLocaleDateString('ru-RU') : 'N/A'}
                          </span>
                          <span className={`px-2 py-1 rounded ${
                            invoice.status === 'paid' ? 'bg-green-100 text-green-800' :
                            invoice.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {invoice.status === 'paid' && 'Оплачен'}
                            {invoice.status === 'pending' && 'Ожидает'}
                            {invoice.status === 'overdue' && 'Просрочен'}
                          </span>
                        </div>
                      </div>
                      <p className="text-sm font-semibold text-gray-900">
                        {formatCurrency(invoice.amount)}
                      </p>
                    </div>
                  </div>
                )) : (
                  <div className="p-8 text-center">
                    <FileText className="h-12 w-12 text-gray-300 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">Нет счетов</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Interaction Timeline */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">История взаимодействий</h2>
            
            <div className="space-y-4">
              {interactions.length > 0 ? interactions.map((interaction, index) => (
                <div key={index} className="flex items-start space-x-4">
                  <div className={`flex-shrink-0 h-10 w-10 rounded-full flex items-center justify-center ${
                    interaction.type === 'meeting' ? 'bg-blue-100' :
                    interaction.type === 'email' ? 'bg-purple-100' :
                    interaction.type === 'call' ? 'bg-green-100' :
                    'bg-gray-100'
                  }`}>
                    {interaction.type === 'meeting' && <User className="h-5 w-5 text-blue-600" />}
                    {interaction.type === 'email' && <Mail className="h-5 w-5 text-purple-600" />}
                    {interaction.type === 'call' && <Phone className="h-5 w-5 text-green-600" />}
                    {interaction.type === 'note' && <MessageSquare className="h-5 w-5 text-gray-600" />}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900">{interaction.title}</p>
                      <span className="text-xs text-gray-500">
                        {interaction.date ? new Date(interaction.date).toLocaleDateString('ru-RU') : 'N/A'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{interaction.description}</p>
                  </div>
                </div>
              )) : (
                <div className="text-center py-8">
                  <MessageSquare className="h-12 w-12 text-gray-300 mx-auto mb-2" />
                  <p className="text-sm text-gray-500">Нет записей о взаимодействиях</p>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Client360;
