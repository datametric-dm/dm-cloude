import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useLocation } from 'react-router-dom';
import { Plus, Search, FolderOpen, Calendar, DollarSign, Edit, Trash2 } from 'lucide-react';
import { DataTable } from '../components/ui/data-table';
import { LoadingCard } from '../components/ui/loading-spinner';
import { projectsApi, clientsApi } from '../lib/api';
import { formatDate, formatCurrency, getStatusBadgeClass, getStatusLabel } from '../lib/utils';
import { toast } from 'sonner';
import ProjectDialog from '../components/ProjectDialog';

export default function Projects() {
  const location = useLocation();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [clientFilter, setClientFilter] = useState('');
  const [directionFilter, setDirectionFilter] = useState('');  // Новый фильтр
  const [managerFilter, setManagerFilter] = useState('');  // Новый фильтр
  const [selectedProject, setSelectedProject] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const queryClient = useQueryClient();

  // Проверяем URL параметры при загрузке
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    if (searchParams.get('action') === 'new') {
      handleCreateNew();
    }
  }, [location.search]);

  const { data: projectsData, isLoading } = useQuery({
    queryKey: ['projects', { search, status: statusFilter, client_id: clientFilter, direction: directionFilter, project_manager: managerFilter }],
    queryFn: () => projectsApi.getAll({ 
      search: search || undefined,
      status: statusFilter || undefined,
      client_id: clientFilter || undefined,
      direction: directionFilter || undefined,
      project_manager: managerFilter || undefined,
      skip: 0,
      limit: 50 
    }).then(res => res.data),
  });

  const { data: clientsData } = useQuery({
    queryKey: ['clients-for-filter'],
    queryFn: () => clientsApi.getAll({ limit: 100 }).then(res => res.data),
  });

  const deleteMutation = useMutation({
    mutationFn: projectsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      toast.success('Проект успешно удалён');
    },
    onError: () => {
      toast.error('Ошибка при удалении проекта');
    },
  });

  const handleEdit = (project) => {
    setSelectedProject(project);
    setIsDialogOpen(true);
  };

  const handleDelete = (project) => {
    if (window.confirm(`Вы уверены, что хотите удалить проект "${project.name}"?`)) {
      deleteMutation.mutate(project.id);
    }
  };

  const handleCreateNew = () => {
    setSelectedProject(null);
    setIsDialogOpen(true);
  };

  const columns = [
    {
      header: 'Проект',
      accessor: 'name',
      cell: (project) => (
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
            <FolderOpen className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="font-medium text-gray-900">{project.name}</p>
            {project.description && (
              <p className="text-sm text-gray-500 truncate max-w-xs">{project.description}</p>
            )}
          </div>
        </div>
      ),
    },
    {
      header: 'Клиент',
      accessor: 'client_id',
      cell: (project) => {
        const client = clientsData?.clients?.find(c => c.id === project.client_id);
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
      cell: (project) => (
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeClass(project.status)}`}>
          {getStatusLabel('project', project.status)}
        </span>
      ),
    },
    {
      header: 'Бюджет',
      accessor: 'budget',
      cell: (project) => (
        <div>
          {project.budget && (
            <p className="text-sm text-gray-900">{formatCurrency(project.budget)}</p>
          )}
          {project.actual_cost > 0 && (
            <p className="text-sm text-gray-500">Потрачено: {formatCurrency(project.actual_cost)}</p>
          )}
        </div>
      ),
    },
    {
      header: 'Крайний срок',
      accessor: 'deadline',
      cell: (project) => (
        <div>
          {project.deadline && (
            <div className="flex items-center text-sm text-gray-600">
              <Calendar className="w-4 h-4 mr-1" />
              {formatDate(project.deadline)}
            </div>
          )}
        </div>
      ),
    },
    {
      header: 'Действия',
      accessor: 'actions',
      cell: (project) => (
        <div className="flex items-center space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleEdit(project);
            }}
            className="text-blue-600 hover:text-blue-900 p-1 rounded"
            data-testid={`edit-project-${project.id}`}
          >
            <Edit className="w-4 h-4" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleDelete(project);
            }}
            className="text-red-600 hover:text-red-900 p-1 rounded"
            disabled={deleteMutation.isPending}
            data-testid={`delete-project-${project.id}`}
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      ),
    },
  ];

  const statusOptions = [
    { value: '', label: 'Все статусы' },
    { value: 'planning', label: 'Планирование' },
    { value: 'in_progress', label: 'В процессе' },
    { value: 'review', label: 'На проверке' },
    { value: 'completed', label: 'Завершен' },
    { value: 'on_hold', label: 'Приостановлен' },
    { value: 'cancelled', label: 'Отменен' },
  ];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Проекты</h1>
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
          <h1 className="text-2xl font-bold text-gray-900">Проекты</h1>
          <p className="text-gray-600 mt-1">
            Управление проектами ({projectsData?.total || 0})
          </p>
        </div>
        
        <button
          onClick={handleCreateNew}
          className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-green-700 transition-colors"
          data-testid="create-project-btn"
        >
          <Plus className="w-5 h-5" />
          <span>Создать проект</span>
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
              placeholder="Поиск по названию или описанию..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="flex-1 border-none outline-none text-gray-900 placeholder-gray-500"
              data-testid="search-projects-input"
            />
          </div>

          {/* Фильтр по статусу */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
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
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
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

      {/* Таблица проектов */}
      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={columns}
          data={projectsData?.projects || []}
          onRowClick={(project) => {
            console.log('Project clicked:', project);
          }}
        />
      </div>

      {/* Диалог создания/редактирования */}
      <ProjectDialog
        project={selectedProject}
        isOpen={isDialogOpen}
        onClose={() => {
          setIsDialogOpen(false);
          setSelectedProject(null);
        }}
      />
    </div>
  );
}