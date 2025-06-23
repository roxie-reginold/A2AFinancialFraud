import React, { useState, useEffect } from 'react';
import { fraudAPI } from '../services/api';
import type { AnalysisResult, Transaction, Alert } from '../services/api';
import TransactionForm from './TransactionForm';
import AnalysisResultComponent from './AnalysisResult';
import { Activity, AlertCircle, TrendingUp } from 'lucide-react';

const Dashboard: React.FC = () => {
  const [currentResult, setCurrentResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [systemStatus, setSystemStatus] = useState<'healthy' | 'error' | 'checking'>('checking');

  useEffect(() => {
    checkSystemHealth();
    loadAlerts();
  }, []);

  const checkSystemHealth = async () => {
    try {
      setSystemStatus('checking');
      await fraudAPI.healthCheck();
      setSystemStatus('healthy');
    } catch (err) {
      setSystemStatus('error');
    }
  };

  const loadAlerts = async () => {
    try {
      const alertsData = await fraudAPI.getAlerts();
      setAlerts(alertsData);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    }
  };

  const handleTransactionSubmit = async (transaction: Transaction) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await fraudAPI.analyzeTransaction(transaction);
      setCurrentResult(result);
      
      if (result.is_fraud) {
        await fraudAPI.createAlert({
          transaction_id: result.transaction_id,
          risk_score: result.risk_score,
          message: `High-risk transaction detected with ${(result.risk_score * 100).toFixed(1)}% fraud probability`,
          status: 'pending',
        });
        await loadAlerts();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze transaction');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'error': return 'text-red-600';
      default: return 'text-yellow-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <Activity className="w-5 h-5 text-green-600" />;
      case 'error': return <AlertCircle className="w-5 h-5 text-red-600" />;
      default: return <TrendingUp className="w-5 h-5 text-yellow-600" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Fraud Detection Dashboard
          </h1>
          <div className="flex items-center space-x-2">
            {getStatusIcon(systemStatus)}
            <span className={`text-sm font-medium ${getStatusColor(systemStatus)}`}>
              System Status: {systemStatus === 'healthy' ? 'Operational' : systemStatus === 'error' ? 'Error' : 'Checking...'}
            </span>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            <p className="font-medium">Error:</p>
            <p>{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2">Total Alerts</h3>
            <p className="text-3xl font-bold text-red-600">{alerts.length}</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2">Pending Alerts</h3>
            <p className="text-3xl font-bold text-yellow-600">
              {alerts.filter(a => a.status === 'pending').length}
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2">Resolved Alerts</h3>
            <p className="text-3xl font-bold text-green-600">
              {alerts.filter(a => a.status === 'resolved').length}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <div className="space-y-6">
            <TransactionForm onSubmit={handleTransactionSubmit} loading={loading} />
            
            {alerts.length > 0 && (
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-xl font-semibold mb-4">Recent Alerts</h2>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {alerts.slice(0, 10).map((alert) => (
                    <div key={alert.id} className="p-3 border rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium text-sm">
                            Transaction: {alert.transaction_id}
                          </p>
                          <p className="text-sm text-gray-600">{alert.message}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date(alert.timestamp).toLocaleString()}
                          </p>
                        </div>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          alert.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                          alert.status === 'resolved' ? 'bg-green-100 text-green-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {alert.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div>
            {currentResult && <AnalysisResultComponent result={currentResult} />}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;