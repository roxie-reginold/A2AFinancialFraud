import React from 'react';
import type { AnalysisResult as AnalysisResultType } from '../services/api';
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react';

interface AnalysisResultProps {
  result: AnalysisResultType;
}

const AnalysisResult: React.FC<AnalysisResultProps> = ({ result }) => {
  const getRiskColor = (riskScore: number) => {
    if (riskScore >= 0.7) return 'text-red-600';
    if (riskScore >= 0.4) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getRiskBgColor = (riskScore: number) => {
    if (riskScore >= 0.7) return 'bg-red-100';
    if (riskScore >= 0.4) return 'bg-yellow-100';
    return 'bg-green-100';
  };

  const getRiskIcon = (isFraud: boolean, riskScore: number) => {
    if (isFraud) return <AlertTriangle className="w-6 h-6 text-red-600" />;
    if (riskScore >= 0.4) return <Clock className="w-6 h-6 text-yellow-600" />;
    return <CheckCircle className="w-6 h-6 text-green-600" />;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Analysis Result</h2>
      
      <div className="space-y-4">
        <div className={`p-4 rounded-lg ${getRiskBgColor(result.risk_score)}`}>
          <div className="flex items-center space-x-3">
            {getRiskIcon(result.is_fraud, result.risk_score)}
            <div>
              <h3 className="font-semibold">
                {result.is_fraud ? 'FRAUD DETECTED' : 'LEGITIMATE TRANSACTION'}
              </h3>
              <p className={`text-lg font-bold ${getRiskColor(result.risk_score)}`}>
                Risk Score: {(result.risk_score * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold mb-2">Transaction Details</h4>
            <div className="space-y-1 text-sm">
              <p><span className="font-medium">ID:</span> {result.transaction_id}</p>
              <p><span className="font-medium">Method:</span> {result.analysis_method}</p>
              <p><span className="font-medium">Confidence:</span> {(result.model_confidence * 100).toFixed(1)}%</p>
              <p><span className="font-medium">Timestamp:</span> {new Date(result.timestamp).toLocaleString()}</p>
            </div>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold mb-2">Risk Factors</h4>
            {result.risk_factors.length > 0 ? (
              <ul className="space-y-1 text-sm">
                {result.risk_factors.map((factor, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="text-yellow-600">⚠</span>
                    <span>{factor}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-600">No significant risk factors detected</p>
            )}
          </div>
        </div>

        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-300 ${
              result.risk_score >= 0.7
                ? 'bg-red-500'
                : result.risk_score >= 0.4
                ? 'bg-yellow-500'
                : 'bg-green-500'
            }`}
            style={{ width: `${result.risk_score * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
};

export default AnalysisResult;