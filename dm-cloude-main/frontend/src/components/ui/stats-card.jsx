import React from 'react';
import { cn } from '../../lib/utils';

export function StatsCard({ title, value, subtitle, icon: Icon, trend, className }) {
  return (
    <div className={cn(
      "bg-white rounded-lg border border-gray-200 p-6 shadow-sm",
      className
    )}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 font-medium">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        {Icon && (
          <div className="p-3 bg-blue-50 rounded-lg">
            <Icon className="w-6 h-6 text-blue-600" />
          </div>
        )}
      </div>
      {trend && (
        <div className="mt-4 flex items-center">
          <span className={cn(
            "text-sm font-medium",
            trend.type === 'increase' ? 'text-green-600' : 'text-red-600'
          )}>
            {trend.value}
          </span>
          <span className="text-sm text-gray-500 ml-1">{trend.label}</span>
        </div>
      )}
    </div>
  );
}
