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

  // Доступные проект-менеджеры
  const projectManagers = [
    'Прыгункова Елена',
    'Гарасюта Александр'
  ];

  // Состояние для направлений с бюджетами и датами
  const [directions, setDirections] = useState(
    project?.directions?.length > 0 
      ? project.directions.map(d => ({
          ...d,
          start_date: d.start_date ? new Date(d.start_date).toISOString().split('T')[0] : '',
          end_date: d.end_date ? new Date(d.end_date).toISOString().split('T')[0] : ''
        }))
      : [{ name: '', budget: '', start_date: '', end_date: '' }]
  );

  // Состояние для подключенных услуг
  const [connectedServices, setConnectedServices] = useState(
    project?.connected_services || []
  );

  // Состояние для зон развития
  const [developmentZones, setDevelopmentZones] = useState(
    project?.development_zones || []
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
      priority: 3,
      project_manager: '',
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
        project_manager: '',
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
          ? project.directions.map(d => ({
              ...d,
              start_date: d.start_date ? new Date(d.start_date).toISOString().split('T')[0] : '',
              end_date: d.end_date ? new Date(d.end_date).toISOString().split('T')[0] : ''
            }))
          : [{ name: '', budget: '', start_date: '', end_date: '' }]
      );
    }
  }, [isOpen, project, reset]);

  // Функции для управления направлениями
  const addDirection = () => {
    setDirections([...directions, { name: '', budget: '', start_date: '', end_date: '' }]);
  };

  const removeDirection = (index) => {
    if (directions.length > 1) {
      setDirections(directions.filter((_, i) => i !== index));
    }
  };

  const updateDirection = (index, field, value) => {
    const newDirections = [...directions];
    newDirections[index][field] = value;
    setDirections(newDirections);
  };

  // Вычисляем общий бюджет
  const calculateTotalBudget = () => {
    return directions.reduce((sum, dir) => {
      const budget = parseFloat(dir.budget) || 0;
      return sum + budget;
    }, 0);
  };

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
    // Преобразуем даты
    const cleanData = {
      ...data,
      start_date: data.start_date || null,
      end_date: data.end_date || null,
    };
    
    // Добавляем направления (фильтруем пустые)
    const validDirections = directions
      .filter(dir => dir.name && dir.name.trim())
      .map(dir => ({
        name: dir.name,
        budget: parseFloat(dir.budget) || 0
      }));
    
    cleanData.directions = validDirections;
    
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
                  Проект-менеджер
                </label>
                <Controller
                  name="project_manager"
                  control={control}
                  render={({ field }) => (
                    <select
                      {...field}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      data-testid="project-manager-select"
                    >
                      <option value="">Выберите проект-менеджера</option>
                      {projectManagers.map((manager, idx) => (
                        <option key={idx} value={manager}>{manager}</option>
                      ))}
                    </select>
                  )}
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
                  Общий бюджет (руб.) - рассчитывается автоматически
                </label>
                <input
                  type="text"
                  value={calculateTotalBudget().toLocaleString('ru-RU') + ' ₽'}
                  disabled
                  className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700 font-semibold"
                  data-testid="project-budget-display"
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

            {/* Направления проекта */}
            <div className="border-t pt-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-md font-medium text-gray-900">Направления проекта</h4>
                <button
                  type="button"
                  onClick={addDirection}
                  className="flex items-center gap-1 px-3 py-1 text-sm bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 transition-colors"
                  data-testid="add-direction-btn"
                >
                  <Plus className="w-4 h-4" />
                  Добавить направление
                </button>
              </div>
              
              {directions.map((direction, index) => (
                <div key={index} className="mb-4 p-4 border border-gray-200 rounded-md bg-gray-50">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-medium text-gray-700">Направление #{index + 1}</span>
                    {directions.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeDirection(index)}
                        className="text-red-500 hover:text-red-700"
                        data-testid={`remove-direction-${index}-btn`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Направление *
                      </label>
                      <select
                        value={direction.name}
                        onChange={(e) => updateDirection(index, 'name', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        data-testid={`direction-${index}-name-select`}
                      >
                        <option value="">Выберите направление</option>
                        {availableDirections.map((dir, idx) => (
                          <option key={idx} value={dir}>{dir}</option>
                        ))}
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Бюджет направления (руб.)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={direction.budget}
                        onChange={(e) => updateDirection(index, 'budget', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        data-testid={`direction-${index}-budget-input`}
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Дата старта направления
                      </label>
                      <input
                        type="date"
                        value={direction.start_date}
                        onChange={(e) => updateDirection(index, 'start_date', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        data-testid={`direction-${index}-start-date-input`}
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Дата остановки направления
                      </label>
                      <input
                        type="date"
                        value={direction.end_date}
                        onChange={(e) => updateDirection(index, 'end_date', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        data-testid={`direction-${index}-end-date-input`}
                      />
                    </div>
                  </div>
                </div>
              ))}
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