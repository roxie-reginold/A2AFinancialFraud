import React, { useState } from 'react';

interface SimpleTransactionFormProps {
  onSubmit: (data: { accountNumber: string; amount: number; description: string }) => void;
  loading?: boolean;
}

const SimpleTransactionForm: React.FC<SimpleTransactionFormProps> = ({ onSubmit, loading = false }) => {
  const [formData, setFormData] = useState({
    accountNumber: '',
    amount: '',
    description: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      accountNumber: formData.accountNumber,
      amount: parseFloat(formData.amount) || 0,
      description: formData.description,
    });
  };

  const generateSample = () => {
    setFormData({
      accountNumber: '1234567890',
      amount: '750.00',
      description: 'Online purchase at electronics store',
    });
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Transaction Form</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">
            Account Number
          </label>
          <input
            type="text"
            value={formData.accountNumber}
            onChange={(e) => setFormData({ ...formData, accountNumber: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter account number"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">
            Amount
          </label>
          <input
            type="number"
            step="0.01"
            value={formData.amount}
            onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="0.00"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={3}
            placeholder="Transaction description"
          />
        </div>

        <div className="flex space-x-3">
          <button
            type="button"
            onClick={generateSample}
            className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
            disabled={loading}
          >
            Sample
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Submit'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SimpleTransactionForm;