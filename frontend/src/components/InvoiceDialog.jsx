import React, { useState } from 'react';
import { useForm, Controller, useFieldArray } from 'react-hook-form';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { X, Plus, Trash2 } from 'lucide-react';
import { invoicesApi, clientsApi, projectsApi } from '../lib/api';
import { toast } from 'sonner';

export default function InvoiceDialog({ invoice, isOpen, onClose }) {
  const queryClient = useQueryClient();
  const isEditing = !!invoice;

  // Получаем список клиентов и проектов для выбора
  const { data: clientsData } = useQuery({
    queryKey: ['clients-for-select'],
    queryFn: () => clientsApi.getAll({ limit: 100 }).then(res => res.data),
    enabled: isOpen,
  });

  const { data: projectsData } = useQuery({
    queryKey: ['projects-for-select'],
    queryFn: () => projectsApi.getAll({ limit: 100 }).then(res => res.data),
    enabled: isOpen,
  });

  const { register, handleSubmit, control, reset, watch, setValue, formState: { errors } } = useForm({
    defaultValues: invoice || {
      number: '',
      client_id: '',
      project_id: '',
      date_issued: '',
      date_due: '',
      tax_rate: 20.0,
      status: 'draft',
      description: '',
      notes: '',
      items: [{ description: '', quantity: 1, price: 0, total: 0 }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  });

  const watchedItems = watch('items');

  React.useEffect(() => {
    if (isOpen) {
      const defaultValues = invoice ? {
        ...invoice,
        date_due: invoice.date_due ? new Date(invoice.date_due).toISOString().split('T')[0] : '',
        tax_rate: invoice.tax_rate?.toString() || '20.0',
        subtotal: invoice.subtotal?.toString() || '',
        tax_amount: invoice.tax_amount?.toString() || '',
        total: invoice.total?.toString() || '',
        project_id: invoice.project_id || '',
      } : {
        number: `INV-${new Date().getFullYear()}-${String(Date.now()).slice(-6)}`,
        client_id: '',
        project_id: '',
        date_due: '',
        tax_rate: 20.0,
        status: 'draft',
        description: '',
        notes: '',
        items: [{ description: '', quantity: 1, price: 0, total: 0 }],
      };
      reset(defaultValues);
    }
  }, [isOpen, invoice, reset]);

  // Пересчет суммы при изменении позиций
  const watchedTaxRate = watch('tax_rate');

  React.useEffect(() => {
    if (watchedItems) {
      let subtotal = 0;
      watchedItems.forEach((item, index) => {
        const quantity = parseFloat(item.quantity) || 0;
        const price = parseFloat(item.price) || 0;
        const total = quantity * price;
        setValue(`items.${index}.total`, total);
        subtotal += total;
      });
      
      const taxRate = parseFloat(watchedTaxRate) || 0;
      const taxAmount = (subtotal * taxRate) / 100;
      const total = subtotal + taxAmount;
      
      setValue('subtotal', subtotal);
      setValue('tax_amount', taxAmount);
      setValue('total', total);
    }
  }, [watchedItems, watchedTaxRate, setValue, watch]);

  const mutation = useMutation({
    mutationFn: (data) => {
      if (isEditing) {
        return invoicesApi.update(invoice.id, data);
      } else {
        return invoicesApi.create(data);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      toast.success(isEditing ? 'Счёт обновлён' : 'Счёт создан');
      onClose();
    },
    onError: () => {
      toast.error('Ошибка при сохранении счёта');
    },
  });

  const onSubmit = (data) => {
    // Преобразуем дату в ISO формат
    const cleanData = {
      ...data,
      date_due: data.date_due ? new Date(data.date_due).toISOString() : null,
      subtotal: parseFloat(data.subtotal) || 0,
      tax_rate: parseFloat(data.tax_rate) || 0,
      tax_amount: parseFloat(data.tax_amount) || 0,
      total: parseFloat(data.total) || 0,
      project_id: data.project_id || null,
      items: data.items.map(item => ({
        ...item,
        quantity: parseFloat(item.quantity) || 1,
        price: parseFloat(item.price) || 0,
        total: parseFloat(item.total) || 0,
      })),
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
    { value: 'draft', label: 'Черновик' },
    { value: 'sent', label: 'Отправлен' },
    { value: 'paid', label: 'Оплачен' },
    { value: 'overdue', label: 'Просрочен' },
    { value: 'cancelled', label: 'Отменён' },
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" onClick={onClose} />
        
        <div className="inline-block w-full max-w-4xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg max-h-screen overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-medium text-gray-900">
              {isEditing ? 'Редактировать счёт' : 'Создать счёт'}
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
              data-testid="close-invoice-dialog"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Основная информация */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Номер счёта *
                </label>
                <input
                  {...register('number', { required: 'Обязательное поле' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  data-testid="invoice-number-input"
                />
                {errors.number && (
                  <p className="text-red-500 text-sm mt-1">{errors.number.message}</p>
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
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      data-testid="invoice-client-select"
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
                  Проект
                </label>
                <Controller
                  name="project_id"
                  control={control}
                  render={({ field }) => (
                    <select
                      {...field}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      data-testid="invoice-project-select"
                    >
                      <option value="">Не привязан к проекту</option>
                      {projectsData?.projects?.map((project) => (
                        <option key={project.id} value={project.id}>
                          {project.name}
                        </option>
                      ))}
                    </select>
                  )}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Срок оплаты *
                </label>
                <input
                  {...register('date_due', { required: 'Обязательное поле' })}
                  type="date"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  data-testid="invoice-due-date-input"
                />
                {errors.date_due && (
                  <p className="text-red-500 text-sm mt-1">{errors.date_due.message}</p>
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
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      data-testid="invoice-status-select"
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
                  НДС (%)
                </label>
                <input
                  {...register('tax_rate')}
                  type="number"
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  data-testid="invoice-tax-rate-input"
                />
              </div>
            </div>

            {/* Описание */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Описание
              </label>
              <textarea
                {...register('description')}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                data-testid="invoice-description-textarea"
              />
            </div>

            {/* Позиции счёта */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-md font-medium text-gray-900">Позиции счёта</h4>
                <button
                  type="button"
                  onClick={() => append({ description: '', quantity: 1, price: 0, total: 0 })}
                  className="flex items-center space-x-1 text-sm text-purple-600 hover:text-purple-800"
                  data-testid="add-invoice-item-btn"
                >
                  <Plus className="w-4 h-4" />
                  <span>Добавить позицию</span>
                </button>
              </div>

              <div className="space-y-3">
                {fields.map((field, index) => (
                  <div key={field.id} className="grid grid-cols-12 gap-2 items-end">
                    <div className="col-span-6">
                      {index === 0 && (
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Описание
                        </label>
                      )}
                      <input
                        {...register(`items.${index}.description`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                        placeholder="Описание работы или услуги"
                      />
                    </div>
                    
                    <div className="col-span-2">
                      {index === 0 && (
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Кол-во
                        </label>
                      )}
                      <input
                        {...register(`items.${index}.quantity`)}
                        type="number"
                        step="0.01"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                      />
                    </div>
                    
                    <div className="col-span-2">
                      {index === 0 && (
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Цена
                        </label>
                      )}
                      <input
                        {...register(`items.${index}.price`)}
                        type="number"
                        step="0.01"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                      />
                    </div>
                    
                    <div className="col-span-1">
                      {index === 0 && (
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Сумма
                        </label>
                      )}
                      <input
                        {...register(`items.${index}.total`)}
                        type="number"
                        readOnly
                        className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-sm"
                      />
                    </div>
                    
                    <div className="col-span-1 flex justify-center">
                      {fields.length > 1 && (
                        <button
                          type="button"
                          onClick={() => remove(index)}
                          className="text-red-600 hover:text-red-900 p-1 rounded"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Итоговые суммы */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="space-y-2 text-right">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Подытог:</span>
                  <span className="font-medium">{(typeof watch('subtotal') === 'number' ? watch('subtotal').toFixed(2) : '0.00')} ₽</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">НДС:</span>
                  <span className="font-medium">{(typeof watch('tax_amount') === 'number' ? watch('tax_amount').toFixed(2) : '0.00')} ₽</span>
                </div>
                <div className="flex justify-between text-lg font-bold border-t pt-2">
                  <span>Итого:</span>
                  <span>{(typeof watch('total') === 'number' ? watch('total').toFixed(2) : '0.00')} ₽</span>
                </div>
              </div>
            </div>

            {/* Примечания */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Примечания
              </label>
              <textarea
                {...register('notes')}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                data-testid="invoice-notes-textarea"
              />
            </div>

            {/* Скрытые поля для расчётных значений */}
            <input {...register('subtotal')} type="hidden" />
            <input {...register('tax_amount')} type="hidden" />
            <input {...register('total')} type="hidden" />

            {/* Кнопки действий */}
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors"
                data-testid="cancel-invoice-btn"
              >
                Отменить
              </button>
              <button
                type="submit"
                disabled={mutation.isPending}
                className="px-4 py-2 text-white bg-purple-600 rounded-md hover:bg-purple-700 transition-colors disabled:opacity-50"
                data-testid="save-invoice-btn"
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