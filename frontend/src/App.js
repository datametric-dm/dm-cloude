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
import OwnerDashboard from './pages/OwnerDashboard';
import FinancialFlow from './pages/FinancialFlow';
import TeamLoad from './pages/TeamLoad';
import Client360 from './pages/Client360';
import RiskAnalyzer from './pages/RiskAnalyzer';
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
                        <Route path="/owner-dashboard" element={<OwnerDashboard />} />
                        <Route path="/clients" element={<ClientsPage />} />
                        <Route path="/projects" element={<ProjectsPage />} />
                        <Route path="/project-flow" element={<ProjectFlow />} />
                        <Route path="/financial-flow" element={<FinancialFlow />} />
                        <Route path="/team-load" element={<TeamLoad />} />
                        <Route path="/client-360" element={<Client360 />} />
                        <Route path="/risk-analyzer" element={<RiskAnalyzer />} />
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
