import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Transaction {
  Time: number;
  V1: number;
  V2: number;
  V3: number;
  V4: number;
  V5: number;
  V6: number;
  V7: number;
  V8: number;
  V9: number;
  V10: number;
  V11: number;
  V12: number;
  V13: number;
  V14: number;
  V15: number;
  V16: number;
  V17: number;
  V18: number;
  V19: number;
  V20: number;
  V21: number;
  V22: number;
  V23: number;
  V24: number;
  V25: number;
  V26: number;
  V27: number;
  V28: number;
  Amount: number;
}

export interface AgentStepResult {
  agent_name: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  risk_score?: number;
  duration_ms?: number;
  result_message?: string;
  details?: string[];
}

export interface AnalysisResult {
  transaction_id: string;
  risk_score: number;
  is_fraud: boolean;
  analysis_method: string;
  model_confidence: number;
  risk_factors: string[];
  timestamp: string;
  agent_steps?: AgentStepResult[];
}

export interface Alert {
  id: string;
  transaction_id: string;
  risk_score: number;
  message: string;
  timestamp: string;
  status: 'pending' | 'acknowledged' | 'resolved';
}

export const fraudAPI = {
  // Analyze single transaction
  analyzeTransaction: async (transaction: Transaction): Promise<AnalysisResult> => {
    const response = await api.post('/analyze', transaction);
    return response.data;
  },

  // Bulk analyze transactions
  analyzeBulk: async (transactions: Transaction[]): Promise<AnalysisResult[]> => {
    const response = await api.post('/analyze/bulk', { transactions });
    return response.data;
  },

  // Get analysis result by transaction ID
  getAnalysis: async (transactionId: string): Promise<AnalysisResult> => {
    const response = await api.get(`/transactions/${transactionId}/analysis`);
    return response.data;
  },

  // Create alert
  createAlert: async (alert: Omit<Alert, 'id' | 'timestamp'>): Promise<Alert> => {
    const response = await api.post('/alerts', alert);
    return response.data;
  },

  // Get all alerts
  getAlerts: async (): Promise<Alert[]> => {
    const response = await api.get('/alerts');
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;