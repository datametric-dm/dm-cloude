import React from 'react';
import { AlertTriangle, X } from 'lucide-react';
import { formatCurrency } from '../lib/utils';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { telegramApi } from '../lib/api';
import { toast } from 'sonner';

export default function OverdueAlert({ overduePayments, overdueInvoices }) {
  const [dismissed, setDismissed] = React.useState(false);
  const queryClient = useQueryClient();

  const notifyTelegramMutation = useMutation({
    mutationFn: telegramApi.notifyOverdue,
    onSuccess: () => {
      toast.success('Уведомление отправлено в Telegram');
    },
    onError: () => {
      toast.error('Ошибка отправки уведомления');
    },
  });

  if (dismissed || (!overduePayments?.count && !overdueInvoices?.count)) {
    return null;
  }

  const totalOverdueAmount = (overduePayments?.total_amount || 0) + (overdueInvoices?.total_amount || 0);
  const totalOverdueCount = (overduePayments?.count || 0) + (overdueInvoices?.count || 0);

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4" data-testid="overdue-alert">
      <div className="flex items-start justify-between">
        <div className="flex items-start">
          <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">
              Обнаружены просроченные платежи!
            </h3>
            <div className="text-sm text-red-700 mt-1">
              <p>
                Просрочено {totalOverdueCount} платежей на сумму {formatCurrency(totalOverdueAmount)}
              </p>
              {overduePayments?.count > 0 && (
                <p className="mt-1">
                  • Платежи: {overduePayments.count} ({formatCurrency(overduePayments.total_amount)})
                </p>
              )}
              {overdueInvoices?.count > 0 && (
                <p className="mt-1">
                  • Счета: {overdueInvoices.count} ({formatCurrency(overdueInvoices.total_amount)})
                </p>
              )}
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <button 
                className="bg-red-600 text-white px-3 py-1 rounded text-sm font-medium hover:bg-red-700 transition-colors"
                onClick={() => notifyTelegramMutation.mutate()}
                disabled={notifyTelegramMutation.isPending}
                data-testid="notify-telegram-btn"
              >
                {notifyTelegramMutation.isPending ? 'Отправляем...' : 'Уведомить в Telegram'}
              </button>
              <button 
                className="bg-white text-red-700 px-3 py-1 rounded text-sm font-medium border border-red-300 hover:bg-red-50 transition-colors"
                data-testid="view-overdue-btn"
              >
                Посмотреть просрочки
              </button>
            </div>
          </div>
        </div>
        <button
          onClick={() => setDismissed(true)}
          className="text-red-400 hover:text-red-600 transition-colors"
          data-testid="dismiss-alert-btn"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
