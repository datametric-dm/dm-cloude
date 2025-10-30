import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { X, Plus, Trash2 } from 'lucide-react';
import { clientsApi } from '../lib/api';
import { toast } from 'sonner';

export default function ClientDialog({ client, isOpen, onClose }) {
  const queryClient = useQueryClient();
  const isEditing = !!client;

  // Состояние для контактных лиц
  const [contacts, setContacts] = useState(
    client?.contacts || [{ name: '', position: '', phone: '', email: '' }]
  );

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: client || {
      name: '',
      email: '',
      phone: '',
      address: '',
      inn: '',
      kpp: '',
      ogrn: '',
      edo: '',
      notes: '',
    },
  });

  React.useEffect(() => {
    if (isOpen) {
      const defaultValues = client || {
        name: '',
        email: '',
        phone: '',
        address: '',
        inn: '',
        kpp: '',
        ogrn: '',
        edo: '',
        notes: '',
      };
      reset(defaultValues);
      setContacts(client?.contacts || [{ name: '', position: '', phone: '', email: '' }]);
    }
  }, [isOpen, client, reset]);

  // Функции для управления контактами
  const addContact = () => {
    setContacts([...contacts, { name: '', position: '', phone: '', email: '' }]);
  };

  const removeContact = (index) => {
    if (contacts.length > 1) {
      setContacts(contacts.filter((_, i) => i !== index));
    }
  };

  const updateContact = (index, field, value) => {
    const newContacts = [...contacts];
    newContacts[index][field] = value;
    setContacts(newContacts);
  };

  const mutation = useMutation({
    mutationFn: (data) => {
      if (isEditing) {
        return clientsApi.update(client.id, data);
      } else {
        return clientsApi.create(data);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      toast.success(isEditing ? 'Клиент обновлён' : 'Клиент создан');
      onClose();
    },
    onError: () => {
      toast.error('Ошибка при сохранении клиента');
    },
  });

  const onSubmit = (data) => {
    // Убираем пустые строки и добавляем контакты
    const cleanData = Object.fromEntries(
      Object.entries(data).map(([key, value]) => [
        key,
        typeof value === 'string' ? value.trim() || null : value,
      ])
    );
    
    // Добавляем контакты (фильтруем пустые)
    cleanData.contacts = contacts.filter(contact => 
      contact.name || contact.position || contact.phone || contact.email
    );
    
    mutation.mutate(cleanData);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" onClick={onClose} />
        
        <div className="inline-block w-full max-w-2xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-medium text-gray-900">
              {isEditing ? 'Редактировать клиента' : 'Добавить клиента'}
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
              data-testid="close-client-dialog"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Основная информация */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Название клиента *
                </label>
                <input
                  {...register('name', { required: 'Обязательное поле' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  data-testid="client-name-input"
                />
                {errors.name && (
                  <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Компания
                </label>
                <input
                  {...register('company')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  data-testid="client-company-input"
                />
              </div>
            </div>

            {/* Контакты */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  {...register('email')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  data-testid="client-email-input"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Телефон
                </label>
                <input
                  {...register('phone')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  data-testid="client-phone-input"
                />
              </div>
            </div>

            {/* Адрес */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Адрес
              </label>
              <textarea
                {...register('address')}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                data-testid="client-address-input"
              />
            </div>

            {/* Реквизиты */}
            <div className="border-t pt-4">
              <h4 className="text-md font-medium text-gray-900 mb-3">Реквизиты</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    ИНН
                  </label>
                  <input
                    {...register('inn')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    data-testid="client-inn-input"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    КПП
                  </label>
                  <input
                    {...register('kpp')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    data-testid="client-kpp-input"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    ОГРН
                  </label>
                  <input
                    {...register('ogrn')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    data-testid="client-ogrn-input"
                  />
                </div>
              </div>
              
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Система ЭДО
                </label>
                <input
                  {...register('edo')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Название системы электронного документооборота"
                  data-testid="client-edo-input"
                />
              </div>
            </div>

            {/* Контактные лица */}
            <div className="border-t pt-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-md font-medium text-gray-900">Контактные лица</h4>
                <button
                  type="button"
                  onClick={addContact}
                  className="flex items-center gap-1 px-3 py-1 text-sm bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 transition-colors"
                  data-testid="add-contact-btn"
                >
                  <Plus className="w-4 h-4" />
                  Добавить контакт
                </button>
              </div>
              
              {contacts.map((contact, index) => (
                <div key={index} className="mb-4 p-4 border border-gray-200 rounded-md bg-gray-50">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-medium text-gray-700">Контакт #{index + 1}</span>
                    {contacts.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeContact(index)}
                        className="text-red-500 hover:text-red-700"
                        data-testid={`remove-contact-${index}-btn`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        ФИО
                      </label>
                      <input
                        value={contact.name}
                        onChange={(e) => updateContact(index, 'name', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        data-testid={`contact-${index}-name-input`}
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Должность
                      </label>
                      <input
                        value={contact.position}
                        onChange={(e) => updateContact(index, 'position', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        data-testid={`contact-${index}-position-input`}
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Телефон
                      </label>
                      <input
                        value={contact.phone}
                        onChange={(e) => updateContact(index, 'phone', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        data-testid={`contact-${index}-phone-input`}
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Email
                      </label>
                      <input
                        type="email"
                        value={contact.email}
                        onChange={(e) => updateContact(index, 'email', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        data-testid={`contact-${index}-email-input`}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Примечания */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Примечания
              </label>
              <textarea
                {...register('notes')}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                data-testid="client-notes-input"
              />
            </div>

            {/* Кнопки */}
            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                data-testid="cancel-client-btn"
              >
                Отменить
              </button>
              <button
                type="submit"
                disabled={mutation.isPending}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
                data-testid="save-client-btn"
              >
                {mutation.isPending ? 'Сохранение...' : (isEditing ? 'Обновить' : 'Создать')}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
