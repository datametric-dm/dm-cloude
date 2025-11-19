import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCompany } from '../contexts/CompanyContext';
import { companiesApi } from '../lib/api';
import { toast } from 'sonner';
import { Building2, Plus, ArrowRight, Users, FolderKanban, TrendingUp } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';

const CompanySelect = () => {
  const navigate = useNavigate();
  const { selectCompany, setCompanies } = useCompany();
  const [companies, setLocalCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newCompany, setNewCompany] = useState({
    name: '',
    email: '',
    phone: '',
  });

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    try {
      setLoading(true);
      const response = await companiesApi.getMy();
      const companiesData = response.data.companies || [];
      setLocalCompanies(companiesData);
      setCompanies(companiesData);
    } catch (error) {
      console.error('Failed to fetch companies:', error);
      toast.error('Не удалось загрузить компании');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCompany = (company) => {
    selectCompany(company);
    toast.success(`Выбрана компания: ${company.name}`);
    navigate('/dashboard');
  };

  const handleCreateCompany = async (e) => {
    e.preventDefault();
    
    if (!newCompany.name.trim()) {
      toast.error('Введите название компании');
      return;
    }

    try {
      setCreating(true);
      const response = await companiesApi.create(newCompany);
      const createdCompany = response.data.company;
      
      toast.success('Компания успешно создана!');
      setShowCreateDialog(false);
      setNewCompany({ name: '', email: '', phone: '' });
      
      // Refresh companies list
      await fetchCompanies();
      
      // Auto-select newly created company
      selectCompany(createdCompany);
      navigate('/dashboard');
    } catch (error) {
      console.error('Failed to create company:', error);
      toast.error(error.response?.data?.detail || 'Не удалось создать компанию');
    } finally {
      setCreating(false);
    }
  };

  const getRoleBadge = (role) => {
    const roleColors = {
      owner: 'bg-purple-100 text-purple-800',
      admin: 'bg-blue-100 text-blue-800',
      manager: 'bg-green-100 text-green-800',
      observer: 'bg-gray-100 text-gray-800',
    };

    const roleLabels = {
      owner: 'Владелец',
      admin: 'Администратор',
      manager: 'Менеджер',
      observer: 'Наблюдатель',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${roleColors[role] || roleColors.observer}`}>
        {roleLabels[role] || role}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка компаний...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <Building2 className="h-12 w-12 text-blue-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Выберите компанию
          </h1>
          <p className="text-gray-600">
            Выберите компанию для продолжения работы или создайте новую
          </p>
        </div>

        {/* Companies Grid */}
        {companies.length === 0 ? (
          <div className="text-center py-12">
            <Building2 className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              У вас пока нет компаний
            </h3>
            <p className="text-gray-600 mb-6">
              Создайте свою первую компанию для начала работы
            </p>
            <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
              <DialogTrigger asChild>
                <Button size="lg">
                  <Plus className="h-5 w-5 mr-2" />
                  Создать компанию
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Создать новую компанию</DialogTitle>
                  <DialogDescription>
                    Введите информацию о вашей компании. Вы станете владельцем.
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleCreateCompany} className="space-y-4">
                  <div>
                    <Label htmlFor="name">Название компании *</Label>
                    <Input
                      id="name"
                      placeholder="Acme Marketing Agency"
                      value={newCompany.name}
                      onChange={(e) => setNewCompany({ ...newCompany, name: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="info@acme.com"
                      value={newCompany.email}
                      onChange={(e) => setNewCompany({ ...newCompany, email: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="phone">Телефон</Label>
                    <Input
                      id="phone"
                      placeholder="+7 (999) 123-45-67"
                      value={newCompany.phone}
                      onChange={(e) => setNewCompany({ ...newCompany, phone: e.target.value })}
                    />
                  </div>
                  <div className="flex justify-end gap-3">
                    <Button 
                      type="button" 
                      variant="outline" 
                      onClick={() => setShowCreateDialog(false)}
                      disabled={creating}
                    >
                      Отмена
                    </Button>
                    <Button type="submit" disabled={creating}>
                      {creating ? 'Создание...' : 'Создать'}
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {companies.map((company) => (
                <Card 
                  key={company.id}
                  className="hover:shadow-lg transition-shadow cursor-pointer group"
                  onClick={() => handleSelectCompany(company)}
                >
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-xl mb-2 group-hover:text-blue-600 transition-colors">
                          {company.name}
                        </CardTitle>
                        {getRoleBadge(company.user_role)}
                      </div>
                      <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
                    </div>
                    {company.email && (
                      <CardDescription className="mt-2">
                        {company.email}
                      </CardDescription>
                    )}
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        <span>Команда</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <FolderKanban className="h-4 w-4" />
                        <span>Проекты</span>
                      </div>
                    </div>
                    <div className="mt-4 pt-4 border-t">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Подписка:</span>
                        <span className="font-medium text-blue-600">
                          {company.subscription_plan === 'free' && 'Бесплатно'}
                          {company.subscription_plan === 'starter' && 'Starter'}
                          {company.subscription_plan === 'professional' && 'Professional'}
                          {company.subscription_plan === 'enterprise' && 'Enterprise'}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Create New Company Button */}
            <div className="text-center">
              <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
                <DialogTrigger asChild>
                  <Button variant="outline" size="lg">
                    <Plus className="h-5 w-5 mr-2" />
                    Создать новую компанию
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Создать новую компанию</DialogTitle>
                    <DialogDescription>
                      Введите информацию о вашей компании. Вы станете владельцем.
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleCreateCompany} className="space-y-4">
                    <div>
                      <Label htmlFor="name">Название компании *</Label>
                      <Input
                        id="name"
                        placeholder="Acme Marketing Agency"
                        value={newCompany.name}
                        onChange={(e) => setNewCompany({ ...newCompany, name: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="info@acme.com"
                        value={newCompany.email}
                        onChange={(e) => setNewCompany({ ...newCompany, email: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="phone">Телефон</Label>
                      <Input
                        id="phone"
                        placeholder="+7 (999) 123-45-67"
                        value={newCompany.phone}
                        onChange={(e) => setNewCompany({ ...newCompany, phone: e.target.value })}
                      />
                    </div>
                    <div className="flex justify-end gap-3">
                      <Button 
                        type="button" 
                        variant="outline" 
                        onClick={() => setShowCreateDialog(false)}
                        disabled={creating}
                      >
                        Отмена
                      </Button>
                      <Button type="submit" disabled={creating}>
                        {creating ? 'Создание...' : 'Создать'}
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default CompanySelect;
