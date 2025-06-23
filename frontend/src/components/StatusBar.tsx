import React from 'react';

interface StatusBarProps {
  status: 'idle' | 'in_progress' | 'completed' | 'error';
  progress?: number;
}

const StatusBar: React.FC<StatusBarProps> = ({ status, progress = 0 }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'in_progress': return 'bg-blue-500';
      case 'completed': return 'bg-green-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-300';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'in_progress': return 'IN PROGRESS';
      case 'completed': return 'COMPLETED';
      case 'error': return 'ERROR';
      default: return 'IDLE';
    }
  };

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-600">STATUS:</span>
        <span className="text-sm font-semibold text-gray-800">{getStatusText()}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${getStatusColor()}`}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
};

export default StatusBar;