import React, { useState } from 'react';
import type { Transaction } from '../services/api';

interface TransactionFormProps {
  onSubmit: (transaction: Transaction) => void;
  loading?: boolean;
}

const TransactionForm: React.FC<TransactionFormProps> = ({ onSubmit, loading = false }) => {
  const [formData, setFormData] = useState<Transaction>({
    Time: 0,
    V1: 0, V2: 0, V3: 0, V4: 0, V5: 0,
    V6: 0, V7: 0, V8: 0, V9: 0, V10: 0,
    V11: 0, V12: 0, V13: 0, V14: 0, V15: 0,
    V16: 0, V17: 0, V18: 0, V19: 0, V20: 0,
    V21: 0, V22: 0, V23: 0, V24: 0, V25: 0,
    V26: 0, V27: 0, V28: 0,
    Amount: 0,
  });

  const handleChange = (field: keyof Transaction, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: parseFloat(value) || 0,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const generateSampleTransaction = () => {
    const sample: Transaction = {
      Time: Math.floor(Math.random() * 172800),
      V1: (Math.random() - 0.5) * 4,
      V2: (Math.random() - 0.5) * 4,
      V3: (Math.random() - 0.5) * 4,
      V4: (Math.random() - 0.5) * 4,
      V5: (Math.random() - 0.5) * 4,
      V6: (Math.random() - 0.5) * 4,
      V7: (Math.random() - 0.5) * 4,
      V8: (Math.random() - 0.5) * 4,
      V9: (Math.random() - 0.5) * 4,
      V10: (Math.random() - 0.5) * 4,
      V11: (Math.random() - 0.5) * 4,
      V12: (Math.random() - 0.5) * 4,
      V13: (Math.random() - 0.5) * 4,
      V14: (Math.random() - 0.5) * 4,
      V15: (Math.random() - 0.5) * 4,
      V16: (Math.random() - 0.5) * 4,
      V17: (Math.random() - 0.5) * 4,
      V18: (Math.random() - 0.5) * 4,
      V19: (Math.random() - 0.5) * 4,
      V20: (Math.random() - 0.5) * 4,
      V21: (Math.random() - 0.5) * 4,
      V22: (Math.random() - 0.5) * 4,
      V23: (Math.random() - 0.5) * 4,
      V24: (Math.random() - 0.5) * 4,
      V25: (Math.random() - 0.5) * 4,
      V26: (Math.random() - 0.5) * 4,
      V27: (Math.random() - 0.5) * 4,
      V28: (Math.random() - 0.5) * 4,
      Amount: Math.random() * 1000,
    };
    setFormData(sample);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Transaction Analysis</h2>
        <button
          type="button"
          onClick={generateSampleTransaction}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          disabled={loading}
        >
          Generate Sample
        </button>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Time
            </label>
            <input
              type="number"
              value={formData.Time}
              onChange={(e) => handleChange('Time', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              step="any"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Amount
            </label>
            <input
              type="number"
              value={formData.Amount}
              onChange={(e) => handleChange('Amount', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              step="any"
            />
          </div>

          {Array.from({ length: 28 }, (_, i) => i + 1).map(num => (
            <div key={`V${num}`}>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                V{num}
              </label>
              <input
                type="number"
                value={formData[`V${num}` as keyof Transaction]}
                onChange={(e) => handleChange(`V${num}` as keyof Transaction, e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                step="any"
              />
            </div>
          ))}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Analyzing...' : 'Analyze Transaction'}
        </button>
      </form>
    </div>
  );
};

export default TransactionForm;