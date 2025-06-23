import React, { useState, useEffect } from 'react';
import { 
  Eye, 
  Brain, 
  Bot, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  ArrowRight,
  Shield,
  Zap
} from 'lucide-react';

export interface AgentStep {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  status: 'pending' | 'processing' | 'completed' | 'error';
  result?: string;
  duration?: number;
  riskScore?: number;
  details?: string[];
}

interface AgentWorkflowVisualizationProps {
  currentStep?: string;
  steps?: AgentStep[];
  onStepUpdate?: (stepId: string, result: Partial<AgentStep>) => void;
}

const defaultSteps: AgentStep[] = [
  {
    id: 'monitor',
    name: 'Transaction Monitor',
    description: 'Initial transaction screening and anomaly detection',
    icon: <Eye className="w-5 h-5" />,
    status: 'pending',
    details: [
      'Amount validation',
      'Time pattern analysis', 
      'Frequency checking',
      'Geographic validation'
    ]
  },
  {
    id: 'hybrid',
    name: 'Hybrid Analysis',
    description: 'ML model risk assessment and pattern recognition',
    icon: <Brain className="w-5 h-5" />,
    status: 'pending',
    details: [
      'Feature extraction',
      'ML model prediction',
      'Pattern matching',
      'Behavioral analysis'
    ]
  },
  {
    id: 'ai_analysis',
    name: 'AI Deep Analysis',
    description: 'Advanced AI analysis using Gemini for complex patterns',
    icon: <Bot className="w-5 h-5" />,
    status: 'pending',
    details: [
      'Context understanding',
      'Complex pattern detection',
      'Risk factor identification',
      'Confidence assessment'
    ]
  },
  {
    id: 'alert',
    name: 'Alert Generation',
    description: 'Risk evaluation and alert notifications',
    icon: <AlertTriangle className="w-5 h-5" />,
    status: 'pending',
    details: [
      'Risk threshold evaluation',
      'Alert priority assignment',
      'Notification routing',
      'Case documentation'
    ]
  }
];

const AgentWorkflowVisualization: React.FC<AgentWorkflowVisualizationProps> = ({ 
  currentStep,
  steps = defaultSteps
}) => {
  const [activeSteps, setActiveSteps] = useState<AgentStep[]>(steps);
  const [overallStatus, setOverallStatus] = useState<'idle' | 'processing' | 'completed' | 'error'>('idle');

  // Update activeSteps when steps prop changes
  useEffect(() => {
    setActiveSteps(steps);
  }, [steps]);

  // Update step status based on currentStep prop
  useEffect(() => {
    if (currentStep) {
      setOverallStatus('processing');
    } else {
      const allCompleted = activeSteps.every(step => step.status === 'completed');
      const hasError = activeSteps.some(step => step.status === 'error');
      if (hasError) {
        setOverallStatus('error');
      } else if (allCompleted && activeSteps.length > 0) {
        setOverallStatus('completed');
      } else {
        setOverallStatus('idle');
      }
    }
  }, [currentStep, activeSteps]);

  const getStepStatusIcon = (status: AgentStep['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'processing':
        return <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      case 'error':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStepColor = (status: AgentStep['status']) => {
    switch (status) {
      case 'completed':
        return 'border-green-500 bg-green-50';
      case 'processing':
        return 'border-blue-500 bg-blue-50 shadow-md';
      case 'error':
        return 'border-red-500 bg-red-50';
      default:
        return 'border-gray-300 bg-gray-50';
    }
  };

  const getRiskScoreColor = (score?: number) => {
    if (!score) return 'text-gray-500';
    if (score >= 0.8) return 'text-red-600';
    if (score >= 0.5) return 'text-yellow-600';
    return 'text-green-600';
  };

  const formatDuration = (duration?: number) => {
    if (!duration) return '';
    return duration < 1000 ? `${duration}ms` : `${(duration / 1000).toFixed(1)}s`;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <Shield className="w-5 h-5 text-blue-600" />
          Agent Workflow Analysis
        </h3>
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-500" />
          <span className="text-sm font-medium text-gray-600">
            {overallStatus === 'processing' ? 'Processing...' : 
             overallStatus === 'completed' ? 'Completed' : 'Ready'}
          </span>
          {/* Debug info */}
          <span className="text-xs text-gray-400">
            ({activeSteps.length} agents)
          </span>
        </div>
      </div>

      {/* Debug info - remove in production */}
      {activeSteps.length === 0 && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-sm text-yellow-800">
            No agents configured. Waiting for transaction submission...
          </p>
        </div>
      )}

      {/* Agent Steps */}
      <div className="space-y-4">
        {activeSteps.map((step, index) => (
          <div key={step.id} className="relative">
            {/* Connection line */}
            {index < activeSteps.length - 1 && (
              <div className="absolute left-6 top-16 w-0.5 h-8 bg-gray-300"></div>
            )}
            
            {/* Step Card */}
            <div className={`relative border-2 rounded-lg p-4 transition-all duration-300 ${getStepColor(step.status)}`}>
              <div className="flex items-start gap-4">
                {/* Agent Icon */}
                <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ${
                  step.status === 'completed' ? 'bg-green-100 text-green-700' :
                  step.status === 'processing' ? 'bg-blue-100 text-blue-700' :
                  step.status === 'error' ? 'bg-red-100 text-red-700' :
                  'bg-gray-100 text-gray-500'
                }`}>
                  {step.icon}
                </div>

                {/* Step Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-gray-800">{step.name}</h4>
                    <div className="flex items-center gap-2">
                      {step.duration && (
                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                          {formatDuration(step.duration)}
                        </span>
                      )}
                      {getStepStatusIcon(step.status)}
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3">{step.description}</p>

                  {/* Step Details */}
                  {step.status !== 'pending' && (
                    <div className="space-y-2">
                      {step.details && (
                        <div className="grid grid-cols-2 gap-2">
                          {step.details.map((detail, idx) => (
                            <div key={idx} className="flex items-center gap-1">
                              <div className={`w-2 h-2 rounded-full ${
                                step.status === 'completed' ? 'bg-green-500' :
                                step.status === 'processing' ? 'bg-blue-500' :
                                'bg-gray-400'
                              }`}></div>
                              <span className="text-xs text-gray-600">{detail}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Risk Score Display */}
                      {step.riskScore !== undefined && (
                        <div className="flex items-center gap-2 mt-2">
                          <span className="text-sm font-medium text-gray-600">Risk Score:</span>
                          <span className={`text-sm font-bold ${getRiskScoreColor(step.riskScore)}`}>
                            {(step.riskScore * 100).toFixed(1)}%
                          </span>
                        </div>
                      )}

                      {/* Result Message */}
                      {step.result && (
                        <div className={`text-sm p-2 rounded ${
                          step.status === 'completed' ? 'bg-green-100 text-green-800' :
                          step.status === 'error' ? 'bg-red-100 text-red-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {step.result}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Arrow for flow */}
                {index < activeSteps.length - 1 && step.status === 'completed' && (
                  <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2">
                    <ArrowRight className="w-4 h-4 text-gray-400" />
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Final Verdict */}
      {overallStatus === 'completed' && (
        <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
          <h4 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
            <Shield className="w-4 h-4 text-blue-600" />
            Final Security Assessment
          </h4>
          <div className="text-sm text-gray-700">
            All agents have completed their analysis. Check the Analysis Result card for the final verdict.
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentWorkflowVisualization;