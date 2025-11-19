import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { CompanyProvider } from './contexts/CompanyContext';
import Layout from './components/Layout';
import PrivateRoute from './components/PrivateRoute';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ClientsPage from './pages/Clients';
import ProjectsPage from './pages/Projects';
import InvoicesPage from './pages/Invoices';
import PaymentsPage from './pages/Payments';
import ReportsPage from './pages/Reports';
import CompanySelect from './pages/CompanySelect';
import TeamManagement from './pages/TeamManagement';
import ProjectFlow from './pages/ProjectFlow';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <CompanyProvider>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/companies" element={
                <PrivateRoute>
                  <CompanySelect />
                </PrivateRoute>
              } />
              <Route
                path="/*"
                element={
                  <PrivateRoute>
                    <Layout>
                      <Routes>
                        <Route path="/" element={<Navigate to="/dashboard" replace />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/clients" element={<ClientsPage />} />
                        <Route path="/projects" element={<ProjectsPage />} />
                        <Route path="/invoices" element={<InvoicesPage />} />
                        <Route path="/payments" element={<PaymentsPage />} />
                        <Route path="/reports" element={<ReportsPage />} />
                        <Route path="/team" element={<TeamManagement />} />
                      </Routes>
                    </Layout>
                  </PrivateRoute>
                }
              />
            </Routes>
            <Toaster position="top-right" richColors />
          </div>
        </Router>
      </CompanyProvider>
    </QueryClientProvider>
  );
}

export default App;
