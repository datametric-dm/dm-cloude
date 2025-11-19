import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { toast } from 'sonner';
import { 
  Plus, 
  MoreVertical, 
  Edit2, 
  Trash2,
  Calendar,
  User,
  AlertCircle
} from 'lucide-react';
import { api } from '../lib/api';

const ProjectFlow = () => {
  const queryClient = useQueryClient();
  const [columns, setColumns] = useState([]);
  const [stages, setStages] = useState([]);
  const [showColumnDialog, setShowColumnDialog] = useState(false);
  const [showStageDialog, setShowStageDialog] = useState(false);
  const [selectedColumn, setSelectedColumn] = useState(null);
  const [selectedStage, setSelectedStage] = useState(null);

  // Fetch Kanban columns
  const { data: columnsData, isLoading: columnsLoading } = useQuery({
    queryKey: ['kanban-columns'],
    queryFn: async () => {
      const response = await api.get('/project-flow/columns');
      return response.data;
    }
  });

  // Fetch project stages
  const { data: stagesData, isLoading: stagesLoading } = useQuery({
    queryKey: ['project-stages'],
    queryFn: async () => {
      const response = await api.get('/project-flow/stages');
      return response.data;
    }
  });

  useEffect(() => {
    if (columnsData?.columns) {
      setColumns(columnsData.columns);
    }
  }, [columnsData]);

  useEffect(() => {
    if (stagesData?.stages) {
      setStages(stagesData.stages);
    }
  }, [stagesData]);

  // Create default columns if none exist
  const createDefaultColumns = useMutation({
    mutationFn: async () => {
      const defaultColumns = [
        { name: 'Backlog', type: 'backlog', color: '#94A3B8', order: 0 },
        { name: 'To Do', type: 'todo', color: '#3B82F6', order: 1 },
        { name: 'In Progress', type: 'in_progress', color: '#F59E0B', order: 2, wip_limit: 5 },
        { name: 'Review', type: 'review', color: '#8B5CF6', order: 3 },
        { name: 'Done', type: 'done', color: '#10B981', order: 4 }
      ];

      for (const col of defaultColumns) {
        await api.post('/project-flow/columns', col);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['kanban-columns']);
      toast.success('Колонки созданы успешно');
    }
  });

  // Handle drag and drop
  const onDragEnd = async (result) => {
    const { source, destination, draggableId } = result;

    if (!destination) return;
    if (source.droppableId === destination.droppableId && source.index === destination.index) {
      return;
    }

    const stage = stages.find(s => s.id === draggableId);
    const targetColumn = columns.find(c => c.id === destination.droppableId);

    if (!stage || !targetColumn) return;

    // Update stage status
    try {
      await api.put(`/project-flow/stages/${stage.id}`, {
        ...stage,
        status: targetColumn.type,
        column_id: targetColumn.id
      });

      // Update local state
      const updatedStages = stages.map(s => 
        s.id === stage.id 
          ? { ...s, status: targetColumn.type, column_id: targetColumn.id }
          : s
      );
      setStages(updatedStages);

      toast.success('Этап перемещен');
    } catch (error) {
      toast.error('Ошибка при перемещении этапа');
    }
  };

  // Group stages by column
  const getStagesByColumn = (columnId) => {
    return stages.filter(s => s.column_id === columnId);
  };

  if (columnsLoading || stagesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (columns.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <AlertCircle className="h-12 w-12 text-gray-400" />
        <h3 className="text-lg font-medium text-gray-900">Kanban доска не настроена</h3>
        <p className="text-sm text-gray-500">Создайте колонки для начала работы</p>
        <button
          onClick={() => createDefaultColumns.mutate()}
          disabled={createDefaultColumns.isLoading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {createDefaultColumns.isLoading ? 'Создание...' : 'Создать колонки по умолчанию'}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Project Flow</h1>
          <p className="text-sm text-gray-500 mt-1">Kanban доска для управления проектными этапами</p>
        </div>
        <button
          onClick={() => setShowStageDialog(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Новый этап
        </button>
      </div>

      {/* Kanban Board */}
      <DragDropContext onDragEnd={onDragEnd}>
        <div className="flex space-x-4 overflow-x-auto pb-4">
          {columns.map((column) => (
            <div
              key={column.id}
              className="flex-shrink-0 w-80 bg-gray-50 rounded-lg"
              style={{ minHeight: '500px' }}
            >
              {/* Column Header */}
              <div 
                className="p-4 border-b border-gray-200 flex items-center justify-between"
                style={{ borderTopColor: column.color, borderTopWidth: '3px' }}
              >
                <div className="flex items-center space-x-2">
                  <h3 className="font-semibold text-gray-900">{column.name}</h3>
                  <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded">
                    {getStagesByColumn(column.id).length}
                  </span>
                  {column.wip_limit && (
                    <span className="text-xs text-orange-600 bg-orange-100 px-2 py-1 rounded">
                      WIP: {column.wip_limit}
                    </span>
                  )}
                </div>
                <button className="p-1 hover:bg-gray-200 rounded">
                  <MoreVertical className="h-4 w-4 text-gray-600" />
                </button>
              </div>

              {/* Droppable Area */}
              <Droppable droppableId={column.id}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={`p-4 space-y-3 min-h-[400px] ${
                      snapshot.isDraggingOver ? 'bg-blue-50' : ''
                    }`}
                  >
                    {getStagesByColumn(column.id).map((stage, index) => (
                      <Draggable key={stage.id} draggableId={stage.id} index={index}>
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className={`bg-white p-4 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow ${
                              snapshot.isDragging ? 'shadow-lg' : ''
                            }`}
                          >
                            {/* Stage Card */}
                            <div className="space-y-2">
                              <div className="flex items-start justify-between">
                                <h4 className="font-medium text-gray-900 text-sm">
                                  {stage.name}
                                </h4>
                                <button
                                  onClick={() => {
                                    setSelectedStage(stage);
                                    setShowStageDialog(true);
                                  }}
                                  className="p-1 hover:bg-gray-100 rounded"
                                >
                                  <Edit2 className="h-3 w-3 text-gray-500" />
                                </button>
                              </div>

                              {stage.description && (
                                <p className="text-xs text-gray-600 line-clamp-2">
                                  {stage.description}
                                </p>
                              )}

                              <div className="flex items-center justify-between text-xs text-gray-500">
                                <div className="flex items-center space-x-2">
                                  {stage.due_date && (
                                    <div className="flex items-center">
                                      <Calendar className="h-3 w-3 mr-1" />
                                      {new Date(stage.due_date).toLocaleDateString('ru-RU')}
                                    </div>
                                  )}
                                  {stage.assigned_to && (
                                    <div className="flex items-center">
                                      <User className="h-3 w-3 mr-1" />
                                      {stage.assigned_to}
                                    </div>
                                  )}
                                </div>
                                {stage.progress !== undefined && (
                                  <span className="font-medium">{stage.progress}%</span>
                                )}
                              </div>

                              {/* Progress Bar */}
                              {stage.progress !== undefined && (
                                <div className="w-full bg-gray-200 rounded-full h-1.5">
                                  <div
                                    className="bg-blue-600 h-1.5 rounded-full transition-all"
                                    style={{ width: `${stage.progress}%` }}
                                  />
                                </div>
                              )}

                              {/* Stage Type Badge */}
                              {stage.stage_type && (
                                <span className="inline-block px-2 py-1 text-xs rounded bg-gray-100 text-gray-700">
                                  {stage.stage_type}
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </div>
          ))}
        </div>
      </DragDropContext>

      {/* Stage Dialog would go here */}
      {showStageDialog && (
        <StageDialog
          stage={selectedStage}
          columns={columns}
          onClose={() => {
            setShowStageDialog(false);
            setSelectedStage(null);
          }}
          onSuccess={() => {
            queryClient.invalidateQueries(['project-stages']);
            setShowStageDialog(false);
            setSelectedStage(null);
          }}
        />
      )}
    </div>
  );
};

// Stage Dialog Component
const StageDialog = ({ stage, columns, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: stage?.name || '',
    description: stage?.description || '',
    project_id: stage?.project_id || '',
    column_id: stage?.column_id || columns[0]?.id || '',
    stage_type: stage?.stage_type || 'milestone',
    due_date: stage?.due_date || '',
    assigned_to: stage?.assigned_to || '',
    progress: stage?.progress || 0
  });

  const mutation = useMutation({
    mutationFn: async (data) => {
      if (stage) {
        return api.put(`/project-flow/stages/${stage.id}`, data);
      } else {
        return api.post('/project-flow/stages', data);
      }
    },
    onSuccess: () => {
      toast.success(stage ? 'Этап обновлен' : 'Этап создан');
      onSuccess();
    },
    onError: (error) => {
      toast.error('Ошибка при сохранении этапа');
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
        <h2 className="text-xl font-bold mb-4">
          {stage ? 'Редактировать этап' : 'Новый этап'}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Название *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Описание
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="3"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Колонка *
            </label>
            <select
              value={formData.column_id}
              onChange={(e) => setFormData({ ...formData, column_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              {columns.map((col) => (
                <option key={col.id} value={col.id}>{col.name}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Тип этапа
              </label>
              <select
                value={formData.stage_type}
                onChange={(e) => setFormData({ ...formData, stage_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="milestone">Milestone</option>
                <option value="task">Task</option>
                <option value="deliverable">Deliverable</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Прогресс (%)
              </label>
              <input
                type="number"
                min="0"
                max="100"
                value={formData.progress}
                onChange={(e) => setFormData({ ...formData, progress: parseInt(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Срок
            </label>
            <input
              type="date"
              value={formData.due_date}
              onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={mutation.isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {mutation.isLoading ? 'Сохранение...' : 'Сохранить'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProjectFlow;
