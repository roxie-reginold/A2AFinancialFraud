import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const transactionData = [
  { time: '00:00', transactions: 12 },
  { time: '04:00', transactions: 8 },
  { time: '08:00', transactions: 25 },
  { time: '12:00', transactions: 32 },
  { time: '16:00', transactions: 28 },
  { time: '20:00', transactions: 15 },
];

const fraudData = [
  { name: 'Legitimate', value: 87, color: '#3B82F6' },
  { name: 'Fraudulent', value: 13, color: '#EF4444' },
];

export const TransactionsOverTimeChart: React.FC = () => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Transactions Over Time</h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={transactionData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="time" stroke="#6b7280" fontSize={12} />
          <YAxis stroke="#6b7280" fontSize={12} />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#f9fafb', 
              border: '1px solid #e5e7eb',
              borderRadius: '8px'
            }}
          />
          <Line 
            type="monotone" 
            dataKey="transactions" 
            stroke="#3B82F6" 
            strokeWidth={2}
            dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export const FraudulentTransactionsChart: React.FC = () => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Fraudulent Transactions</h3>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={fraudData}
            cx="50%"
            cy="50%"
            innerRadius={40}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
          >
            {fraudData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value) => [`${value}%`, 'Percentage']}
            contentStyle={{ 
              backgroundColor: '#f9fafb', 
              border: '1px solid #e5e7eb',
              borderRadius: '8px'
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="flex justify-center space-x-4 mt-4">
        {fraudData.map((entry, index) => (
          <div key={index} className="flex items-center space-x-2">
            <div 
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-sm text-gray-600">{entry.name}: {entry.value}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};