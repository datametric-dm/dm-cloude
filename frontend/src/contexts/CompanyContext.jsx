import React, { createContext, useContext, useState, useEffect } from 'react';

const CompanyContext = createContext();

export const CompanyProvider = ({ children }) => {
  const [currentCompany, setCurrentCompany] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load current company from localStorage
    const savedCompany = localStorage.getItem('current_company');
    if (savedCompany) {
      try {
        setCurrentCompany(JSON.parse(savedCompany));
      } catch (e) {
        console.error('Failed to parse saved company', e);
      }
    }
    setLoading(false);
  }, []);

  const selectCompany = (company) => {
    setCurrentCompany(company);
    localStorage.setItem('current_company', JSON.stringify(company));
  };

  const clearCompany = () => {
    setCurrentCompany(null);
    localStorage.removeItem('current_company');
  };

  const value = {
    currentCompany,
    companies,
    setCompanies,
    selectCompany,
    clearCompany,
    loading,
  };

  return (
    <CompanyContext.Provider value={value}>
      {children}
    </CompanyContext.Provider>
  );
};

export const useCompany = () => {
  const context = useContext(CompanyContext);
  if (!context) {
    throw new Error('useCompany must be used within CompanyProvider');
  }
  return context;
};
