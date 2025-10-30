import React from 'react';
import { cn } from '../../lib/utils';

export function LoadingSpinner({ size = 'md', className }) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  return (
    <div className={cn("flex items-center justify-center", className)}>
      <div className={cn(
        "animate-spin rounded-full border-2 border-gray-300 border-t-blue-600",
        sizeClasses[size]
      )} />
    </div>
  );
}

export function LoadingCard() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-8 shadow-sm">
      <LoadingSpinner size="lg" className="py-8" />
      <p className="text-center text-gray-500 mt-4">Загрузка...</p>
    </div>
  );
}
