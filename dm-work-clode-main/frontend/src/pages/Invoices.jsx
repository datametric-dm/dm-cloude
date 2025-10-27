import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useLocation } from 'react-router-dom';
import { Plus, Search, FileText, Calendar, DollarSign, Edit, Trash2 } from 'lucide-react';
import { DataTable } from '../components/ui/data-table';
import { LoadingCard } from '../components/ui/loading-spinner';
import { invoicesApi, clientsApi } from '../lib/api';
import { formatDate, formatCurrency, getStatusBadgeClass, getStatusLabel } from '../lib/utils';
import { toast } from 'sonner';
import InvoiceDialog from '../components/InvoiceDialog';

export default function Invoices() {
  const location = useLocation();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [clientFilter, setClientFilter] = useState('');
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const queryClient = useQueryClient();

  // Проверяем URL параметры при загрузке
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    if (searchParams.get('action') === 'new') {
      handleCreateNew();
    }
  }, [location.search]);

  const { data: invoicesData, isLoading } = useQuery({
    queryKey: ['invoices', { search, status: statusFilter, client_id: clientFilter }],
    queryFn: () => invoicesApi.getAll({ 
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
    mutationFn: invoicesApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      toast.success('Счёт успешно удалён');
    },
    onError: () => {
      toast.error('Ошибка при удалении счёта');
    },
  });

  const handleEdit = (invoice) => {
    setSelectedInvoice(invoice);
    setIsDialogOpen(true);
  };

  const handleDelete = (invoice) => {
    if (window.confirm(`Вы уверены, что хотите удалить счёт "${invoice.number}"?`)) {
      deleteMutation.mutate(invoice.id);
    }
  };

  const handleCreateNew = () => {
    setSelectedInvoice(null);
    setIsDialogOpen(true);
  };

  const columns = [
    {
      header: 'Счёт',
      accessor: 'number',
      cell: (invoice) => (
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
            <FileText className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <p className="font-medium text-gray-900">{invoice.number}</p>
            {invoice.description && (
              <p className="text-sm text-gray-500 truncate max-w-xs">{invoice.description}</p>
            )}
          </div>
        </div>
      ),
    },
    {
      header: 'Клиент',
      accessor: 'client_id',
      cell: (invoice) => {
        const client = clientsData?.clients?.find(c => c.id === invoice.client_id);
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
      cell: (invoice) => (
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeClass(invoice.status)}`}>
          {getStatusLabel('invoice', invoice.status)}
        </span>
      ),
    },
    {
      header: 'Сумма',
      accessor: 'total',
      cell: (invoice) => (
        <div>
          <p className="text-sm text-gray-900 font-medium">{formatCurrency(invoice.total)}</p>
          {invoice.tax_amount > 0 && (
            <p className="text-sm text-gray-500">НДС: {formatCurrency(invoice.tax_amount)}</p>
          )}
        </div>
      ),
    },
    {
      header: 'Даты',
      accessor: 'dates',
      cell: (invoice) => (
        <div>
          <div className="flex items-center text-sm text-gray-600 mb-1">
            <Calendar className="w-4 h-4 mr-1" />
            <span>Выставлен: {formatDate(invoice.date_issued)}</span>
          </div>
          {invoice.date_due && (
            <div className="flex items-center text-sm text-gray-600">
              <Calendar className="w-4 h-4 mr-1" />
              <span>К оплате: {formatDate(invoice.date_due)}</span>
            </div>
          )}
        </div>
      ),
    },
    {
      header: 'Действия',
      accessor: 'actions',
      cell: (invoice) => (
        <div className="flex items-center space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleEdit(invoice);
            }}
            className="text-blue-600 hover:text-blue-900 p-1 rounded"
            data-testid={`edit-invoice-${invoice.id}`}
          >
            <Edit className="w-4 h-4" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleDelete(invoice);
            }}
            className="text-red-600 hover:text-red-900 p-1 rounded"
            disabled={deleteMutation.isPending}
            data-testid={`delete-invoice-${invoice.id}`}
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      ),
    },
  ];

  const statusOptions = [
    { value: '', label: 'Все статусы' },
    { value: 'draft', label: 'Черновик' },
    { value: 'sent', label: 'Отправлен' },
    { value: 'paid', label: 'Оплачен' },
    { value: 'overdue', label: 'Просрочен' },
    { value: 'cancelled', label: 'Отменён' },
  ];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Счета</h1>
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
          <h1 className="text-2xl font-bold text-gray-900">Счета</h1>
          <p className="text-gray-600 mt-1">
            Управление счетами ({invoicesData?.total || 0})
          </p>
        </div>
        
        <button
          onClick={handleCreateNew}
          className="bg-purple-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-purple-700 transition-colors"
          data-testid="create-invoice-btn"
        >
          <Plus className="w-5 h-5" />
          <span>Создать счёт</span>
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
              placeholder="Поиск по номеру или описанию..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="flex-1 border-none outline-none text-gray-900 placeholder-gray-500"
              data-testid="search-invoices-input"
            />
          </div>

          {/* Фильтр по статусу */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
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
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
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

      {/* Таблица счетов */}
      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={columns}
          data={invoicesData?.invoices || []}
          onRowClick={(invoice) => {
            console.log('Invoice clicked:', invoice);
          }}
        />
      </div>

      {/* Диалог создания/редактирования */}
      <InvoiceDialog
        invoice={selectedInvoice}
        isOpen={isDialogOpen}
        onClose={() => {
          setIsDialogOpen(false);
          setSelectedInvoice(null);
        }}
      />
    </div>
  );
}