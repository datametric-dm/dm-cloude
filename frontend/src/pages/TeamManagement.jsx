import React, { useState, useEffect } from 'react';
import { useCompany } from '../contexts/CompanyContext';
import { teamApi } from '../lib/api';
import { toast } from 'sonner';
import { Users, UserPlus, Mail, Shield, Trash2, Edit } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';

const TeamManagement = () => {
  const { currentCompany } = useCompany();
  const [teamMembers, setTeamMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showInviteDialog, setShowInviteDialog] = useState(false);
  const [inviting, setInviting] = useState(false);
  const [inviteData, setInviteData] = useState({
    email: '',
    full_name: '',
    role: 'observer',
  });

  useEffect(() => {
    if (currentCompany) {
      fetchTeamMembers();
    }
  }, [currentCompany]);

  const fetchTeamMembers = async () => {
    try {
      setLoading(true);
      const response = await teamApi.getMembers(currentCompany.id);
      setTeamMembers(response.data.team_members || []);
    } catch (error) {
      console.error('Failed to fetch team members:', error);
      toast.error('Не удалось загрузить команду');
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async (e) => {
    e.preventDefault();
    
    if (!inviteData.email.trim()) {
      toast.error('Введите email');
      return;
    }

    try {
      setInviting(true);
      await teamApi.inviteUser(currentCompany.id, inviteData);
      toast.success('Пользователь приглашен!');
      setShowInviteDialog(false);
      setInviteData({ email: '', full_name: '', role: 'observer' });
      fetchTeamMembers();
    } catch (error) {
      console.error('Failed to invite user:', error);
      toast.error(error.response?.data?.detail || 'Не удалось пригласить пользователя');
    } finally {
      setInviting(false);
    }
  };

  const handleRemoveUser = async (userId) => {
    if (!confirm('Вы уверены, что хотите удалить этого пользователя из команды?')) {
      return;
    }

    try {
      await teamApi.removeUser(currentCompany.id, userId);
      toast.success('Пользователь удален из команды');
      fetchTeamMembers();
    } catch (error) {
      console.error('Failed to remove user:', error);
      toast.error(error.response?.data?.detail || 'Не удалось удалить пользователя');
    }
  };

  const getRoleBadge = (role) => {
    const variants = {
      owner: { variant: 'default', className: 'bg-purple-600' },
      admin: { variant: 'default', className: 'bg-blue-600' },
      manager: { variant: 'default', className: 'bg-green-600' },
      observer: { variant: 'secondary' },
    };

    const labels = {
      owner: 'Владелец',
      admin: 'Администратор',
      manager: 'Менеджер',
      observer: 'Наблюдатель',
    };

    const config = variants[role] || variants.observer;
    
    return (
      <Badge {...config}>
        {labels[role] || role}
      </Badge>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('ru-RU');
  };

  if (!currentCompany) {
    return (
      <div className="container mx-auto py-8">
        <Card>
          <CardContent className="py-8">
            <p className="text-center text-gray-500">Выберите компанию для управления командой</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Управление командой</h1>
          <p className="text-gray-600">Компания: {currentCompany.name}</p>
        </div>
        <Dialog open={showInviteDialog} onOpenChange={setShowInviteDialog}>
          <DialogTrigger asChild>
            <Button>
              <UserPlus className="h-4 w-4 mr-2" />
              Пригласить пользователя
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Пригласить пользователя</DialogTitle>
              <DialogDescription>
                Пригласите нового пользователя в вашу команду
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleInvite} className="space-y-4">
              <div>
                <Label htmlFor="email">Email *</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="user@example.com"
                  value={inviteData.email}
                  onChange={(e) => setInviteData({ ...inviteData, email: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="full_name">Полное имя</Label>
                <Input
                  id="full_name"
                  placeholder="Иван Иванов"
                  value={inviteData.full_name}
                  onChange={(e) => setInviteData({ ...inviteData, full_name: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="role">Роль</Label>
                <Select 
                  value={inviteData.role}
                  onValueChange={(value) => setInviteData({ ...inviteData, role: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="observer">Наблюдатель</SelectItem>
                    <SelectItem value="manager">Менеджер</SelectItem>
                    <SelectItem value="admin">Администратор</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-sm text-gray-500 mt-1">
                  {inviteData.role === 'observer' && 'Только просмотр данных'}
                  {inviteData.role === 'manager' && 'Управление проектами и клиентами'}
                  {inviteData.role === 'admin' && 'Полный доступ (кроме удаления компании)'}
                </p>
              </div>
              <div className="flex justify-end gap-3">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setShowInviteDialog(false)}
                  disabled={inviting}
                >
                  Отмена
                </Button>
                <Button type="submit" disabled={inviting}>
                  {inviting ? 'Отправка...' : 'Пригласить'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <Card>
          <CardContent className="py-8">
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Члены команды
            </CardTitle>
            <CardDescription>
              {teamMembers.length} {teamMembers.length === 1 ? 'участник' : 'участников'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {teamMembers.map((member) => (
                <div
                  key={member.user_id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                      <span className="text-blue-600 font-semibold">
                        {member.email?.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium">{member.full_name || 'Без имени'}</p>
                        {getRoleBadge(member.role)}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <Mail className="h-3 w-3" />
                        <span>{member.email}</span>
                      </div>
                      {member.joined_at && (
                        <p className="text-xs text-gray-400 mt-1">
                          Присоединился: {formatDate(member.joined_at)}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {member.role !== 'owner' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveUser(member.user_id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}

              {teamMembers.length === 0 && (
                <div className="text-center py-8">
                  <Users className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500">Пока нет членов команды</p>
                  <p className="text-sm text-gray-400 mt-1">
                    Пригласите коллег для совместной работы
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default TeamManagement;
