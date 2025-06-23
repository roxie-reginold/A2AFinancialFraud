import React from 'react';
import { CheckCircle, AlertTriangle } from 'lucide-react';

interface AnalysisResultCardProps {
  result: {
    is_fraud: boolean;
    risk_score: number;
    message?: string;
  } | null;
}

const AnalysisResultCard: React.FC<AnalysisResultCardProps> = ({ result }) => {
  if (!result) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Analysis Result</h3>
        <p className="text-gray-500 text-center py-8">No analysis performed yet</p>
      </div>
    );
  }

  const isFraud = result.is_fraud;
  const message = result.message || (isFraud ? 'This transaction is fraudulent.' : 'This transaction is not fraudulent.');

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Analysis Result</h3>
      
      <div className={`p-4 rounded-lg border-l-4 ${
        isFraud 
          ? 'bg-red-50 border-red-400' 
          : 'bg-green-50 border-green-400'
      }`}>
        <div className="flex items-start space-x-3">
          {isFraud ? (
            <AlertTriangle className="w-6 h-6 text-red-600 mt-0.5" />
          ) : (
            <CheckCircle className="w-6 h-6 text-green-600 mt-0.5" />
          )}
          <div>
            <div className={`font-semibold ${
              isFraud ? 'text-red-800' : 'text-green-800'
            }`}>
              {isFraud ? 'FRAUD DETECTED' : 'LEGITIMATE TRANSACTION'}
            </div>
            <p className={`text-sm mt-1 ${
              isFraud ? 'text-red-700' : 'text-green-700'
            }`}>
              {message}
            </p>
            <div className="mt-2">
              <span className="text-sm font-medium text-gray-600">Risk Score: </span>
              <span className={`font-semibold ${
                result.risk_score > 0.7 ? 'text-red-600' :
                result.risk_score > 0.4 ? 'text-yellow-600' : 'text-green-600'
              }`}>
                {(result.risk_score * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisResultCard;