import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      console.log('Попытка входа с email:', email);
      
      // Прямой fetch запрос - используем относительный путь
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
      });

      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка входа');
      }

      const data = await response.json();
      console.log('Login response:', data);

      const { access_token, user } = data;
      
      // Сохраняем токен и данные пользователя
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      console.log('Токен сохранен, длина:', access_token.length);
      console.log('User сохранен:', user);
      
      toast.success(`Добро пожаловать, ${user.full_name || user.email}!`);
      
      // Небольшая задержка перед редиректом на страницу выбора компании
      setTimeout(() => {
        navigate('/companies');
      }, 100);
      
    } catch (error) {
      console.error('Login error:', error);
      const message = error.message || 'Ошибка входа в систему';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="bg-white p-8 rounded-lg shadow-2xl w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            DataMetrics Cloud
          </h1>
          <p className="text-gray-600">Система управления проектами</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="adminDM@test.com"
              required
              className="mt-1"
              data-testid="login-email-input"
            />
          </div>

          <div>
            <Label htmlFor="password">Пароль</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="mt-1"
              data-testid="login-password-input"
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={loading}
            data-testid="login-submit-button"
          >
            {loading ? 'Вход...' : 'Войти'}
          </Button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-600">
          <p>Учетные данные:</p>
          <p className="font-mono mt-1">adminDM@test.com / adminDM4321!</p>
        </div>
      </div>
    </div>
  );
}
