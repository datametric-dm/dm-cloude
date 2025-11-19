import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  FolderOpen,
  FileText,
  CreditCard,
  BarChart3,
  Menu,
  X,
  Building2,
  LogOut,
  User as UserIcon,
  ChevronDown,
  UserCog,
  TrendingUp,
  AlertTriangle,
  Eye,
} from 'lucide-react';
import { cn } from '../lib/utils';
import { toast } from 'sonner';
import { useCompany } from '../contexts/CompanyContext';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from './ui/dropdown-menu';

const navigation = [
  { name: 'Дашборд', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Owner Dashboard', href: '/owner-dashboard', icon: TrendingUp },
  { name: 'Клиенты', href: '/clients', icon: Users },
  { name: 'Проекты', href: '/projects', icon: FolderOpen },
  { name: 'Project Flow', href: '/project-flow', icon: FolderOpen },
  { name: 'Financial Flow', href: '/financial-flow', icon: BarChart3 },
  { name: 'Team Load', href: '/team-load', icon: Users },
  { name: 'Счета', href: '/invoices', icon: FileText },
  { name: 'Платежи', href: '/payments', icon: CreditCard },
  { name: 'Отчеты', href: '/reports', icon: BarChart3 },
  { name: 'Команда', href: '/team', icon: UserCog },
];

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { currentCompany, clearCompany } = useCompany();
  
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    clearCompany();
    toast.success('Вы успешно вышли из системы');
    navigate('/login');
  };

  const handleSwitchCompany = () => {
    navigate('/companies');
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Мобильное меню overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        >
          <div className="fixed inset-0 bg-black opacity-25" />
        </div>
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <Building2 className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-lg font-bold text-gray-900">DataMetrics</h1>
              <p className="text-xs text-gray-500">Cloud MVP</p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Company Selector */}
        {currentCompany && (
          <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
            <DropdownMenu>
              <DropdownMenuTrigger className="w-full">
                <div className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                  <div className="flex items-center gap-2 min-w-0">
                    <Building2 className="h-5 w-5 text-blue-600 flex-shrink-0" />
                    <div className="text-left min-w-0 flex-1">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {currentCompany.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {currentCompany.user_role === 'owner' && 'Владелец'}
                        {currentCompany.user_role === 'admin' && 'Администратор'}
                        {currentCompany.user_role === 'manager' && 'Менеджер'}
                        {currentCompany.user_role === 'observer' && 'Наблюдатель'}
                      </p>
                    </div>
                  </div>
                  <ChevronDown className="h-4 w-4 text-gray-400 flex-shrink-0" />
                </div>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-56">
                <DropdownMenuLabel>Текущая компания</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleSwitchCompany}>
                  <Building2 className="h-4 w-4 mr-2" />
                  Сменить компанию
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        )}

        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                  isActive
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                )}
                onClick={() => setSidebarOpen(false)}
              >
                <Icon
                  className={cn(
                    'mr-3 h-5 w-5 flex-shrink-0',
                    isActive ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-500'
                  )}
                />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500">
            DataMetrics Cloud MVP v2.0
            <br />
            Система управления проектами
          </div>
        </div>
      </div>

      {/* Основной контент */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Верхняя панель */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between h-16 px-6">
            <button
              onClick={() => setSidebarOpen(true)}
              className="text-gray-500 lg:hidden"
            >
              <Menu className="w-6 h-6" />
            </button>
            
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                {new Date().toLocaleDateString('ru-RU', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </div>
              
              <div className="flex items-center space-x-3 ml-6 pl-6 border-l border-gray-300">
                <div className="flex items-center space-x-2 text-sm">
                  <UserIcon className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-700">{user.email || 'Пользователь'}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  data-testid="logout-button"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Выйти</span>
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Основной контент */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
