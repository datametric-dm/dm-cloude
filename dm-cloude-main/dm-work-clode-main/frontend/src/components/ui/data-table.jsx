import React from 'react';
import { cn } from '../../lib/utils';

export function DataTable({ columns, data, onRowClick, className }) {
  return (
    <div className={cn("overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg", className)}>
      <table className="min-w-full divide-y divide-gray-300">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((column, index) => (
              <th
                key={index}
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((row, rowIndex) => (
            <tr
              key={rowIndex}
              onClick={() => onRowClick && onRowClick(row)}
              className={cn(
                onRowClick && "cursor-pointer hover:bg-gray-50"
              )}
            >
              {columns.map((column, colIndex) => (
                <td key={colIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {column.cell ? column.cell(row) : row[column.accessor]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {data.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">Данные отсутствуют</p>
        </div>
      )}
    </div>
  );
}
