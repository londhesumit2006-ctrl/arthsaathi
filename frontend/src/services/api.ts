import axios from 'axios';
import type { TokenResponse, CreditApplication, ApplicationResponse, CreditScoreDetail } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests - only if not already set
api.interceptors.request.use((config) => {
  if (!config.headers.Authorization) {
    const token = localStorage.getItem('jwt_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle 401 responses - clear stale tokens
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const url = error.config?.url || '';
      if (url.includes('/admin/')) {
        // Clear admin token on 401 so the redirect loop breaks
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_id');
        localStorage.removeItem('admin_email');
        localStorage.removeItem('admin_role');
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const register = async (email: string, password: string, full_name: string): Promise<TokenResponse> => {
  const response = await api.post('/api/v1/auth/register', { email, password, full_name, role: 'applicant' });
  return response.data;
};

export const login = async (email: string, password: string): Promise<TokenResponse> => {
  const response = await api.post('/api/v1/auth/login', { email, password });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/api/v1/auth/me');
  return response.data;
};

// Application API
export const submitApplication = async (application: CreditApplication): Promise<ApplicationResponse> => {
  const response = await api.post('/api/v1/applications', application);
  return response.data;
};

export const getApplications = async (): Promise<ApplicationResponse[]> => {
  const response = await api.get('/api/v1/applications');
  return response.data;
};

export const getApplication = async (applicationId: number): Promise<ApplicationResponse> => {
  const response = await api.get(`/api/v1/applications/${applicationId}`);
  return response.data;
};

export const getCreditScore = async (applicationId: number): Promise<CreditScoreDetail> => {
  const response = await api.get(`/api/v1/applications/${applicationId}/score`);
  return response.data;
};

// Admin API (legacy - kept for backward compatibility)
export const getAllApplications = async (): Promise<ApplicationResponse[]> => {
  const response = await api.get('/api/v1/admin/applications');
  return response.data;
};

export const getStatistics = async () => {
  const response = await api.get('/api/v1/admin/statistics');
  return response.data;
};

// Admin Auth API
export const adminLogin = async (email: string, password: string) => {
  const response = await api.post('/api/v1/admin/auth/login', { email, password });
  return response.data;
};

export const getAdminInfo = async () => {
  const token = localStorage.getItem('admin_token');
  const response = await api.get('/api/v1/admin/auth/me', {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

// Admin Applications API
export const getAdminApplications = async (skip: number = 0, limit: number = 100, status?: string) => {
  const token = localStorage.getItem('admin_token');
  const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() });
  if (status) params.append('status', status);
  
  const response = await api.get(`/api/v1/admin/applications?${params.toString()}`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

export const updateApplicationStatus = async (
  applicationId: number, 
  status: string, 
  notes?: string, 
  reason?: string
) => {
  const token = localStorage.getItem('admin_token');
  const response = await api.patch(
    `/api/v1/admin/applications/${applicationId}/status`,
    { status, notes, reason },
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );
  return response.data;
};

// Admin Users API
export const getAdminUsers = async (skip: number = 0, limit: number = 100) => {
  const token = localStorage.getItem('admin_token');
  const response = await api.get(`/api/v1/admin/users?skip=${skip}&limit=${limit}`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

export const createAdminUser = async (data: {
  email: string;
  password: string;
  full_name: string;
  role: string;
  permissions: string[];
}) => {
  const token = localStorage.getItem('admin_token');
  const response = await api.post('/api/v1/admin/users', data, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

export const updateAdminUser = async (
  adminId: number,
  data: {
    full_name?: string;
    role?: string;
    permissions?: string[];
  }
) => {
  const token = localStorage.getItem('admin_token');
  const response = await api.patch(`/api/v1/admin/users/${adminId}`, data, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

export const deactivateAdminUser = async (adminId: number) => {
  const token = localStorage.getItem('admin_token');
  const response = await api.delete(`/api/v1/admin/users/${adminId}`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

// Admin Analytics API
export const getDashboardMetrics = async (days: number = 30) => {
  const token = localStorage.getItem('admin_token');
  const response = await api.get(`/api/v1/admin/analytics/dashboard?days=${days}`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

export const getCreditScoreDistribution = async (days: number = 30) => {
  const token = localStorage.getItem('admin_token');
  const response = await api.get(`/api/v1/admin/analytics/credit-score-distribution?days=${days}`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

export default api;

// ArthSaathi finance APIs
export type FinanceProfile = {
  id: number; account_mode: 'household' | 'business' | 'both'; current_balance: string;
  currency: string; preferred_language: 'en' | 'hi';
};
export type FinanceOverview = {
  context_type: 'household' | 'business';
  current_balance: string; projected_balance_30_days: string; expected_income_30_days: string;
  pending_obligations_30_days: string;
  receivables_30_days: string; payables_30_days: string;
  upcoming_obligations: Array<{ id: number; title: string; amount: string; due_date: string; status: string }>;
  cash_status: 'comfortable' | 'watch' | 'shortfall'; explanation: string;
};
export type FinanceEntry = {
  id: number; context_type: 'household' | 'business'; entry_type: 'income' | 'expense';
  amount: string; category: string; description?: string; occurred_on: string;
  is_recurring: boolean; recurrence_frequency?: string; source: string; created_at: string;
};
export type FinanceObligation = {
  id: number; obligation_type: string; title: string; amount: string; due_date: string;
  status: string; recurrence_frequency?: string; notes?: string;
};
export type FinanceBusiness = { id: number; business_name: string; business_type?: string; opening_balance: string };
export type FinanceInvoice = {
  id: number; business_id: number; direction: 'receivable' | 'payable'; counterparty: string;
  invoice_number?: string; issue_date: string; due_date: string; total_amount: string;
  amount_paid: string; status: string;
};

export const getFinanceProfile = async (): Promise<FinanceProfile> => (await api.get('/api/v1/finance/profile')).data;
export const updateFinanceProfile = async (data: { account_mode: string; current_balance: number; preferred_language: string }) =>
  (await api.put('/api/v1/finance/profile', data)).data;
export const getFinanceOverview = async (contextType: 'household' | 'business' = 'household'): Promise<FinanceOverview> =>
  (await api.get('/api/v1/finance/overview', { params: { context_type: contextType } })).data;
export const getFinanceEntries = async (): Promise<FinanceEntry[]> => (await api.get('/api/v1/finance/entries')).data;
export const createFinanceEntry = async (data: Record<string, unknown>): Promise<FinanceEntry> =>
  (await api.post('/api/v1/finance/entries', data)).data;
export const deleteFinanceEntry = async (id: number) => api.delete(`/api/v1/finance/entries/${id}`);
export const getFinanceObligations = async (): Promise<FinanceObligation[]> => (await api.get('/api/v1/finance/obligations')).data;
export const createFinanceObligation = async (data: Record<string, unknown>): Promise<FinanceObligation> =>
  (await api.post('/api/v1/finance/obligations', data)).data;
export const updateFinanceObligationStatus = async (id: number, status: string) =>
  (await api.patch(`/api/v1/finance/obligations/${id}/status`, { status })).data;
export const getFinanceBusinesses = async (): Promise<FinanceBusiness[]> => (await api.get('/api/v1/finance/businesses')).data;
export const createFinanceBusiness = async (data: Record<string, unknown>): Promise<FinanceBusiness> =>
  (await api.post('/api/v1/finance/businesses', data)).data;
export const getFinanceInvoices = async (): Promise<FinanceInvoice[]> => (await api.get('/api/v1/finance/businesses/invoices')).data;
export const createFinanceInvoice = async (data: Record<string, unknown>): Promise<FinanceInvoice> =>
  (await api.post('/api/v1/finance/businesses/invoices', data)).data;
export const updateFinanceInvoicePayment = async (id: number, amount_paid: number) =>
  (await api.patch(`/api/v1/finance/businesses/invoices/${id}/payment`, { amount_paid })).data;
