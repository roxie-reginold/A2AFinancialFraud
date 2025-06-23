import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

interface AlertBannerProps {
  show: boolean;
  message: string;
  type: 'warning' | 'error' | 'success';
  onClose: () => void;
}

const AlertBanner: React.FC<AlertBannerProps> = ({ show, message, type, onClose }) => {
  if (!show) return null;

  const getBgColor = () => {
    switch (type) {
      case 'warning': return 'bg-yellow-100 border-yellow-400 text-yellow-800';
      case 'error': return 'bg-red-100 border-red-400 text-red-800';
      case 'success': return 'bg-green-100 border-green-400 text-green-800';
      default: return 'bg-yellow-100 border-yellow-400 text-yellow-800';
    }
  };

  const getIcon = () => {
    switch (type) {
      case 'warning': return <AlertTriangle className="w-5 h-5" />;
      case 'error': return <AlertTriangle className="w-5 h-5" />;
      case 'success': return <AlertTriangle className="w-5 h-5" />;
      default: return <AlertTriangle className="w-5 h-5" />;
    }
  };

  return (
    <div className={`border-l-4 p-4 rounded-md ${getBgColor()} mb-4`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {getIcon()}
          <span className="font-medium">{message}</span>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-black hover:bg-opacity-10 rounded"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default AlertBanner;