import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useLocation } from 'react-router-dom';
import { Plus, Search, CreditCard, Calendar, DollarSign, Edit, Trash2, CheckCircle } from 'lucide-react';
import { DataTable } from '../components/ui/data-table';
import { LoadingCard } from '../components/ui/loading-spinner';
import { paymentsApi, clientsApi } from '../lib/api';
import { formatDate, formatCurrency, getStatusBadgeClass, getStatusLabel } from '../lib/utils';
import { toast } from 'sonner';
import PaymentDialog from '../components/PaymentDialog';

export default function Payments() {
  const location = useLocation();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [clientFilter, setClientFilter] = useState('');
  const [selectedPayment, setSelectedPayment] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const queryClient = useQueryClient();

  // Проверяем URL параметры при загрузке
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    if (searchParams.get('action') === 'new') {
      handleCreateNew();
    }
  }, [location.search]);

  const { data: paymentsData, isLoading } = useQuery({
    queryKey: ['payments', { search, status: statusFilter, client_id: clientFilter }],
    queryFn: () => paymentsApi.getAll({ 
      search: search || undefined,
      status: statusFilter || undefined,
      client_id: clientFilter || undefined,
      skip: 0,
      limit: 50 
    }).then(res => res.data),
  });

  const { data: clientsData } = useQuery({
    queryKey: ['clients-for-filter'],
    queryFn: () => clientsApi.getAll({ limit: 100 }).then(res => res.data),
  });

  const deleteMutation = useMutation({
    mutationFn: paymentsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      toast.success('Платёж успешно удалён');
    },
    onError: () => {
      toast.error('Ошибка при удалении платежа');
    },
  });

  const markReceivedMutation = useMutation({
    mutationFn: (paymentId) => paymentsApi.markReceived(paymentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      toast.success('Платёж отмечен как полученный');
    },
    onError: () => {
      toast.error('Ошибка при обновлении статуса платежа');
    },
  });

  const handleEdit = (payment) => {
    setSelectedPayment(payment);
    setIsDialogOpen(true);
  };

  const handleDelete = (payment) => {
    if (window.confirm(`Вы уверены, что хотите удалить платёж на сумму ${formatCurrency(payment.amount)}?`)) {
      deleteMutation.mutate(payment.id);
    }
  };

  const handleMarkReceived = (payment) => {
    if (window.confirm(`Отметить платёж на сумму ${formatCurrency(payment.amount)} как полученный?`)) {
      markReceivedMutation.mutate(payment.id);
    }
  };

  const handleCreateNew = () => {
    setSelectedPayment(null);
    setIsDialogOpen(true);
  };

  const getPaymentTypeLabel = (type) => {
    const types = {
      bank_transfer: 'Банковский перевод',
      cash: 'Наличные',
      card: 'Банковская карта',
      online: 'Онлайн платёж',
      other: 'Другое',
    };
    return types[type] || type;
  };

  const columns = [
    {
      header: 'Платёж',
      accessor: 'description',
      cell: (payment) => (
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
            <CreditCard className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p className="font-medium text-gray-900">{formatCurrency(payment.amount)}</p>
            {payment.description && (
              <p className="text-sm text-gray-500 truncate max-w-xs">{payment.description}</p>
            )}
            {payment.reference_number && (
              <p className="text-sm text-gray-400">№ {payment.reference_number}</p>
            )}
          </div>
        </div>
      ),
    },
    {
      header: 'Клиент',
      accessor: 'client_id',
      cell: (payment) => {
        const client = clientsData?.clients?.find(c => c.id === payment.client_id);
        return (
          <div>
            <p className="text-sm text-gray-900">{client?.name || 'Неизвестен'}</p>
            {client?.company && (
              <p className="text-sm text-gray-500">{client.company}</p>
            )}
          </div>
        );
      },
    },
    {
      header: 'Статус',
      accessor: 'status',
      cell: (payment) => (
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeClass(payment.status)}`}>
          {getStatusLabel('payment', payment.status)}
        </span>
      ),
    },
    {
      header: 'Тип платежа',
      accessor: 'payment_type',
      cell: (payment) => (
        <span className="text-sm text-gray-600">
          {getPaymentTypeLabel(payment.payment_type)}
        </span>
      ),
    },
    {
      header: 'Даты',
      accessor: 'dates',
      cell: (payment) => (
        <div>
          <div className="flex items-center text-sm text-gray-600 mb-1">
            <Calendar className="w-4 h-4 mr-1" />
            <span>План: {formatDate(payment.payment_date_planned)}</span>
          </div>
          {payment.payment_date_actual && (
            <div className="flex items-center text-sm text-green-600">
              <CheckCircle className="w-4 h-4 mr-1" />
              <span>Факт: {formatDate(payment.payment_date_actual)}</span>
            </div>
          )}
        </div>
      ),
    },
    {
      header: 'Действия',
      accessor: 'actions',
      cell: (payment) => (
        <div className="flex items-center space-x-2">
          {payment.status === 'planned' && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleMarkReceived(payment);
              }}
              className="text-green-600 hover:text-green-900 p-1 rounded"
              disabled={markReceivedMutation.isPending}
              data-testid={`mark-received-payment-${payment.id}`}
              title="Отметить как полученный"
            >
              <CheckCircle className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleEdit(payment);
            }}
            className="text-blue-600 hover:text-blue-900 p-1 rounded"
            data-testid={`edit-payment-${payment.id}`}
          >
            <Edit className="w-4 h-4" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleDelete(payment);
            }}
            className="text-red-600 hover:text-red-900 p-1 rounded"
            disabled={deleteMutation.isPending}
            data-testid={`delete-payment-${payment.id}`}
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      ),
    },
  ];

  const statusOptions = [
    { value: '', label: 'Все статусы' },
    { value: 'planned', label: 'Запланирован' },
    { value: 'received', label: 'Получен' },
    { value: 'overdue', label: 'Просрочен' },
    { value: 'cancelled', label: 'Отменён' },
  ];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Платежи</h1>
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
          <h1 className="text-2xl font-bold text-gray-900">Платежи</h1>
          <p className="text-gray-600 mt-1">
            Управление платежами ({paymentsData?.total || 0})
          </p>
        </div>
        
        <button
          onClick={handleCreateNew}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700 transition-colors"
          data-testid="create-payment-btn"
        >
          <Plus className="w-5 h-5" />
          <span>Добавить платёж</span>
        </button>
      </div>

      {/* Фильтры */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Поиск */}
          <div className="flex items-center space-x-2">
            <Search className="w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Поиск по описанию или номеру..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="flex-1 border-none outline-none text-gray-900 placeholder-gray-500"
              data-testid="search-payments-input"
            />
          </div>

          {/* Фильтр по статусу */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            data-testid="status-filter-select"
          >
            {statusOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          {/* Фильтр по клиенту */}
          <select
            value={clientFilter}
            onChange={(e) => setClientFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            data-testid="client-filter-select"
          >
            <option value="">Все клиенты</option>
            {clientsData?.clients?.map((client) => (
              <option key={client.id} value={client.id}>
                {client.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Таблица платежей */}
      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={columns}
          data={paymentsData?.payments || []}
          onRowClick={(payment) => {
            console.log('Payment clicked:', payment);
          }}
        />
      </div>

      {/* Диалог создания/редактирования */}
      <PaymentDialog
        payment={selectedPayment}
        isOpen={isDialogOpen}
        onClose={() => {
          setIsDialogOpen(false);
          setSelectedPayment(null);
        }}
      />
    </div>
  );
}