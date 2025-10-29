import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useLocation } from 'react-router-dom';
import { Plus, Search, Building2, Mail, Phone, Edit, Trash2 } from 'lucide-react';
import { DataTable } from '../components/ui/data-table';
import { LoadingCard } from '../components/ui/loading-spinner';
import { clientsApi } from '../lib/api';
import { formatDate } from '../lib/utils';
import { toast } from 'sonner';
import ClientDialog from '../components/ClientDialog';

export default function Clients() {
  const location = useLocation();
  const [search, setSearch] = useState('');
  const [selectedClient, setSelectedClient] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const queryClient = useQueryClient();

  // Проверяем URL параметры при загрузке
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    if (searchParams.get('action') === 'new') {
      handleCreateNew();
    }
  }, [location.search]);

  const { data: clientsData, isLoading } = useQuery({
    queryKey: ['clients', { search }],
    queryFn: () => clientsApi.getAll({ 
      search: search || undefined,
      skip: 0,
      limit: 50 
    }).then(res => res.data),
  });

  const deleteMutation = useMutation({
    mutationFn: clientsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      toast.success('Клиент успешно удалён');
    },
    onError: () => {
      toast.error('Ошибка при удалении клиента');
    },
  });

  const handleEdit = (client) => {
    setSelectedClient(client);
    setIsDialogOpen(true);
  };

  const handleDelete = (client) => {
    if (window.confirm(`Вы уверены, что хотите удалить клиента "${client.name}"?`)) {
      deleteMutation.mutate(client.id);
    }
  };

  const handleCreateNew = () => {
    setSelectedClient(null);
    setIsDialogOpen(true);
  };

  const columns = [
    {
      header: 'Клиент',
      accessor: 'name',
      cell: (client) => (
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
            <Building2 className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p className="font-medium text-gray-900">{client.name}</p>
            {client.company && (
              <p className="text-sm text-gray-500">{client.company}</p>
            )}
          </div>
        </div>
      ),
    },
    {
      header: 'Контакты',
      accessor: 'contacts',
      cell: (client) => (
        <div className="space-y-1">
          {client.email && (
            <div className="flex items-center text-sm text-gray-600">
              <Mail className="w-4 h-4 mr-1" />
              {client.email}
            </div>
          )}
          {client.phone && (
            <div className="flex items-center text-sm text-gray-600">
              <Phone className="w-4 h-4 mr-1" />
              {client.phone}
            </div>
          )}
        </div>
      ),
    },
    {
      header: 'Контактное лицо',
      accessor: 'contact_person',
      cell: (client) => (
        <div>
          {client.contact_person && (
            <p className="text-sm text-gray-900">{client.contact_person}</p>
          )}
          {client.contact_position && (
            <p className="text-sm text-gray-500">{client.contact_position}</p>
          )}
        </div>
      ),
    },
    {
      header: 'Дата создания',
      accessor: 'created_at',
      cell: (client) => (
        <span className="text-sm text-gray-500">
          {formatDate(client.created_at)}
        </span>
      ),
    },
    {
      header: 'Действия',
      accessor: 'actions',
      cell: (client) => (
        <div className="flex items-center space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleEdit(client);
            }}
            className="text-blue-600 hover:text-blue-900 p-1 rounded"
            data-testid={`edit-client-${client.id}`}
          >
            <Edit className="w-4 h-4" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleDelete(client);
            }}
            className="text-red-600 hover:text-red-900 p-1 rounded"
            disabled={deleteMutation.isPending}
            data-testid={`delete-client-${client.id}`}
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      ),
    },
  ];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Клиенты</h1>
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
          <h1 className="text-2xl font-bold text-gray-900">Клиенты</h1>
          <p className="text-gray-600 mt-1">
            Управление базой клиентов ({clientsData?.total || 0})
          </p>
        </div>
        
        <button
          onClick={handleCreateNew}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700 transition-colors"
          data-testid="create-client-btn"
        >
          <Plus className="w-5 h-5" />
          <span>Добавить клиента</span>
        </button>
      </div>

      {/* Поиск */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center space-x-2">
          <Search className="w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Поиск по имени, компании или email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 border-none outline-none text-gray-900 placeholder-gray-500"
            data-testid="search-clients-input"
          />
        </div>
      </div>

      {/* Таблица клиентов */}
      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={columns}
          data={clientsData?.clients || []}
          onRowClick={(client) => {
            // Можно добавить переход к детальной странице
            console.log('Client clicked:', client);
          }}
        />
      </div>

      {/* Диалог создания/редактирования */}
      <ClientDialog
        client={selectedClient}
        isOpen={isDialogOpen}
        onClose={() => {
          setIsDialogOpen(false);
          setSelectedClient(null);
        }}
      />
    </div>
  );
}
