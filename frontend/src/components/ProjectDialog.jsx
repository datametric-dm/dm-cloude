import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { X, Plus, Trash2 } from 'lucide-react';
import { projectsApi, clientsApi } from '../lib/api';
import { toast } from 'sonner';

export default function ProjectDialog({ project, isOpen, onClose }) {
  const queryClient = useQueryClient();
  const isEditing = !!project;

  // Доступные направления
  const availableDirections = [
    'продвижение',
    'аналитика',
    'внедрение CRM',
    'интеграция CRM и МИС',
    'колл-центр',
    'создание сайта'
  ];

  // Состояние для направлений с бюджетами
  const [directions, setDirections] = useState(
    project?.directions?.length > 0 
      ? project.directions 
      : [{ name: '', budget: '' }]
  );

  // Получаем список клиентов для выбора
  const { data: clientsData } = useQuery({
    queryKey: ['clients-for-select'],
    queryFn: () => clientsApi.getAll({ limit: 100 }).then(res => res.data),
    enabled: isOpen,
  });

  const { register, handleSubmit, control, reset, formState: { errors } } = useForm({
    defaultValues: project || {
      name: '',
      description: '',
      client_id: '',
      status: 'planning',
      start_date: '',
      end_date: '',
      brief: '',
      requirements: '',
      deliverables: '',
      notes: '',
    },
  });

  React.useEffect(() => {
    if (isOpen) {
      const defaultValues = project ? {
        ...project,
        start_date: project.start_date ? new Date(project.start_date).toISOString().split('T')[0] : '',
        end_date: project.end_date ? new Date(project.end_date).toISOString().split('T')[0] : '',
      } : {
        name: '',
        description: '',
        client_id: '',
        status: 'planning',
        start_date: '',
        end_date: '',
        brief: '',
        requirements: '',
        deliverables: '',
        notes: '',
      };
      reset(defaultValues);
      setDirections(
        project?.directions?.length > 0 
          ? project.directions 
          : [{ name: '', budget: '' }]
      );
    }
  }, [isOpen, project, reset]);

  const mutation = useMutation({
    mutationFn: (data) => {
      if (isEditing) {
        return projectsApi.update(project.id, data);
      } else {
        return projectsApi.create(data);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      toast.success(isEditing ? 'Проект обновлён' : 'Проект создан');
      onClose();
    },
    onError: () => {
      toast.error('Ошибка при сохранении проекта');
    },
  });

  const onSubmit = (data) => {
    // Преобразуем даты и бюджет
    const cleanData = {
      ...data,
      budget: data.budget ? parseFloat(data.budget) : null,
      start_date: data.start_date || null,
      end_date: data.end_date || null,
    };
    
    // Убираем пустые строки
    Object.keys(cleanData).forEach(key => {
      if (typeof cleanData[key] === 'string' && !cleanData[key].trim()) {
        cleanData[key] = null;
      }
    });

    mutation.mutate(cleanData);
  };

  const statusOptions = [
    { value: 'planning', label: 'Планирование' },
    { value: 'in_progress', label: 'В процессе' },
    { value: 'review', label: 'На проверке' },
    { value: 'completed', label: 'Завершен' },
    { value: 'on_hold', label: 'Приостановлен' },
    { value: 'cancelled', label: 'Отменен' },
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" onClick={onClose} />
        
        <div className="inline-block w-full max-w-3xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-medium text-gray-900">
              {isEditing ? 'Редактировать проект' : 'Создать проект'}
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
              data-testid="close-project-dialog"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Основная информация */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Название проекта *
                </label>
                <input
                  {...register('name', { required: 'Обязательное поле' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  data-testid="project-name-input"
                />
                {errors.name && (
                  <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Клиент *
                </label>
                <Controller
                  name="client_id"
                  control={control}
                  rules={{ required: 'Обязательное поле' }}
                  render={({ field }) => (
                    <select
                      {...field}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      data-testid="project-client-select"
                    >
                      <option value="">Выберите клиента</option>
                      {clientsData?.clients?.map((client) => (
                        <option key={client.id} value={client.id}>
                          {client.name}
                        </option>
                      ))}
                    </select>
                  )}
                />
                {errors.client_id && (
                  <p className="text-red-500 text-sm mt-1">{errors.client_id.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Статус
                </label>
                <Controller
                  name="status"
                  control={control}
                  render={({ field }) => (
                    <select
                      {...field}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      data-testid="project-status-select"
                    >
                      {statusOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  )}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Бюджет (руб.)
                </label>
                <input
                  {...register('budget')}
                  type="number"
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  data-testid="project-budget-input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Дата начала
                </label>
                <input
                  {...register('start_date')}
                  type="date"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  data-testid="project-start-date-input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Дата окончания
                </label>
                <input
                  {...register('end_date')}
                  type="date"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  data-testid="project-end-date-input"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Описание
                </label>
                <textarea
                  {...register('description')}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  data-testid="project-description-textarea"
                />
              </div>
            </div>

            {/* Детальная информация */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Техническое задание
                </label>
                <textarea
                  {...register('brief')}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Краткое описание задач и целей проекта..."
                  data-testid="project-brief-textarea"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Требования
                </label>
                <textarea
                  {...register('requirements')}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Технические требования, используемые технологии..."
                  data-testid="project-requirements-textarea"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Результаты
                </label>
                <textarea
                  {...register('deliverables')}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Что должно быть доставлено клиенту..."
                  data-testid="project-deliverables-textarea"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Примечания
                </label>
                <textarea
                  {...register('notes')}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  data-testid="project-notes-textarea"
                />
              </div>
            </div>

            {/* Кнопки действий */}
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors"
                data-testid="cancel-project-btn"
              >
                Отменить
              </button>
              <button
                type="submit"
                disabled={mutation.isPending}
                className="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
                data-testid="save-project-btn"
              >
                {mutation.isPending ? 'Сохранение...' : (isEditing ? 'Сохранить' : 'Создать')}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}