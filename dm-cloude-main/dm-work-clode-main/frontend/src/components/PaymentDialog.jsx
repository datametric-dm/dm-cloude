import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { X } from 'lucide-react';
import { paymentsApi, clientsApi, invoicesApi } from '../lib/api';
import { toast } from 'sonner';

export default function PaymentDialog({ payment, isOpen, onClose }) {
  const queryClient = useQueryClient();
  const isEditing = !!payment;

  // Получаем список клиентов и счетов для выбора
  const { data: clientsData } = useQuery({
    queryKey: ['clients-for-select'],
    queryFn: () => clientsApi.getAll({ limit: 100 }).then(res => res.data),
    enabled: isOpen,
  });

  const { data: invoicesData } = useQuery({
    queryKey: ['invoices-for-select'],
    queryFn: () => invoicesApi.getAll({ limit: 100 }).then(res => res.data),
    enabled: isOpen,
  });

  const { register, handleSubmit, control, reset, formState: { errors } } = useForm({
    defaultValues: payment || {
      client_id: '',
      invoice_id: '',
      amount: '',
      payment_date_planned: '',
      payment_date_actual: '',
      status: 'planned',
      payment_type: 'bank_transfer',
      description: '',
      notes: '',
      reference_number: '',
    },
  });

  React.useEffect(() => {
    if (isOpen) {
      const defaultValues = payment ? {
        ...payment,
        payment_date_planned: payment.payment_date_planned ? new Date(payment.payment_date_planned).toISOString().split('T')[0] : '',
        payment_date_actual: payment.payment_date_actual ? new Date(payment.payment_date_actual).toISOString().split('T')[0] : '',
        amount: payment.amount?.toString() || '',
        invoice_id: payment.invoice_id || '',
      } : {
        client_id: '',
        invoice_id: '',
        amount: '',
        payment_date_planned: '',
        payment_date_actual: '',
        status: 'planned',
        payment_type: 'bank_transfer',
        description: '',
        notes: '',
        reference_number: '',
      };
      reset(defaultValues);
    }
  }, [isOpen, payment, reset]);

  const mutation = useMutation({
    mutationFn: (data) => {
      if (isEditing) {
        return paymentsApi.update(payment.id, data);
      } else {
        return paymentsApi.create(data);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      toast.success(isEditing ? 'Платёж обновлён' : 'Платёж создан');
      onClose();
    },
    onError: () => {
      toast.error('Ошибка при сохранении платежа');
    },
  });

  const onSubmit = (data) => {
    // Преобразуем данные
    const cleanData = {
      ...data,
      amount: parseFloat(data.amount) || 0,
      payment_date_planned: data.payment_date_planned ? new Date(data.payment_date_planned).toISOString() : null,
      payment_date_actual: data.payment_date_actual ? new Date(data.payment_date_actual).toISOString() : null,
      invoice_id: data.invoice_id || null,
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
    { value: 'planned', label: 'Запланирован' },
    { value: 'received', label: 'Получен' },
    { value: 'overdue', label: 'Просрочен' },
    { value: 'cancelled', label: 'Отменён' },
  ];

  const paymentTypeOptions = [
    { value: 'bank_transfer', label: 'Банковский перевод' },
    { value: 'cash', label: 'Наличные' },
    { value: 'card', label: 'Банковская карта' },
    { value: 'online', label: 'Онлайн платёж' },
    { value: 'other', label: 'Другое' },
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" onClick={onClose} />
        
        <div className="inline-block w-full max-w-2xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-medium text-gray-900">
              {isEditing ? 'Редактировать платёж' : 'Добавить платёж'}
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
              data-testid="close-payment-dialog"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Основная информация */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                      data-testid="payment-client-select"
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
                  Счёт
                </label>
                <Controller
                  name="invoice_id"
                  control={control}
                  render={({ field }) => (
                    <select
                      {...field}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      data-testid="payment-invoice-select"
                    >
                      <option value="">Не привязан к счёту</option>
                      {invoicesData?.invoices?.map((invoice) => (
                        <option key={invoice.id} value={invoice.id}>
                          {invoice.number} ({invoice.total} ₽)
                        </option>
                      ))}
                    </select>
                  )}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Сумма (руб.) *
                </label>
                <input
                  {...register('amount', { required: 'Обязательное поле' })}
                  type="number"
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  data-testid="payment-amount-input"
                />
                {errors.amount && (
                  <p className="text-red-500 text-sm mt-1">{errors.amount.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Тип платежа
                </label>
                <Controller
                  name="payment_type"
                  control={control}
                  render={({ field }) => (
                    <select
                      {...field}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      data-testid="payment-type-select"
                    >
                      {paymentTypeOptions.map((option) => (
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
                  Планируемая дата *
                </label>
                <input
                  {...register('payment_date_planned', { required: 'Обязательное поле' })}
                  type="date"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  data-testid="payment-planned-date-input"
                />
                {errors.payment_date_planned && (
                  <p className="text-red-500 text-sm mt-1">{errors.payment_date_planned.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Фактическая дата
                </label>
                <input
                  {...register('payment_date_actual')}
                  type="date"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  data-testid="payment-actual-date-input"
                />
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
                      data-testid="payment-status-select"
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
                  Номер операции
                </label>
                <input
                  {...register('reference_number')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Номер банковской операции"
                  data-testid="payment-reference-input"
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
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Назначение платежа..."
                data-testid="payment-description-textarea"
              />
            </div>

            {/* Примечания */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Примечания
              </label>
              <textarea
                {...register('notes')}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                data-testid="payment-notes-textarea"
              />
            </div>

            {/* Кнопки действий */}
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors"
                data-testid="cancel-payment-btn"
              >
                Отменить
              </button>
              <button
                type="submit"
                disabled={mutation.isPending}
                className="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
                data-testid="save-payment-btn"
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