import React, { useState } from 'react';
import Sidebar from './Sidebar';
import AlertBanner from './AlertBanner';
import SimpleTransactionForm from './SimpleTransactionForm';
import StatusBar from './StatusBar';
import AnalysisResultCard from './AnalysisResultCard';
import AgentWorkflowVisualization, { type AgentStep } from './AgentWorkflowVisualization';
import { TransactionsOverTimeChart, FraudulentTransactionsChart } from './Charts';
import { Eye, Brain, Bot, AlertTriangle } from 'lucide-react';

const NewDashboard: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [alert, setAlert] = useState<{ show: boolean; message: string; type: 'warning' | 'error' | 'success' }>({ show: false, message: '', type: 'warning' });
  const [status, setStatus] = useState<'idle' | 'in_progress' | 'completed' | 'error'>('idle');
  const [progress, setProgress] = useState(0);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [currentAgentStep, setCurrentAgentStep] = useState<string>('');
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);

  // Helper function to generate step results
  const getStepResults = (stepName: string, data: { accountNumber: string; amount: number; description: string }) => {
    const amount = data.amount;
    const description = data.description.toLowerCase();
    
    switch (stepName) {
      case 'monitor':
        const isHighAmount = amount > 1000;
        const isSuspiciousDesc = description.includes('cash') || description.includes('withdraw');
        const riskScore = (isHighAmount ? 0.3 : 0.1) + (isSuspiciousDesc ? 0.2 : 0.0);
        return {
          riskScore,
          result: isHighAmount || isSuspiciousDesc 
            ? 'Transaction flagged for further analysis' 
            : 'Transaction passed initial screening'
        };
      
      case 'hybrid':
        const mlRisk = Math.min(0.9, amount / 5000 * 0.7 + Math.random() * 0.3);
        return {
          riskScore: mlRisk,
          result: mlRisk > 0.5 
            ? 'ML model detected suspicious patterns' 
            : 'ML model shows normal transaction behavior'
        };
      
      case 'ai_analysis':
        const contextRisk = description.includes('online') ? 0.2 : 
                           description.includes('atm') ? 0.4 :
                           description.includes('cash') ? 0.6 : 0.3;
        const aiRisk = Math.min(0.95, contextRisk + (amount > 2000 ? 0.3 : 0.1) + Math.random() * 0.2);
        return {
          riskScore: aiRisk,
          result: aiRisk > 0.7 
            ? 'AI detected high-risk transaction patterns'
            : aiRisk > 0.4
            ? 'AI identified moderate risk factors'
            : 'AI analysis shows low risk'
        };
      
      case 'alert':
        const finalRisk = Math.max(amount / 3000 * 0.6, Math.random() * 0.8);
        return {
          riskScore: finalRisk,
          result: finalRisk > 0.8 
            ? 'HIGH PRIORITY: Fraud alert generated'
            : finalRisk > 0.5
            ? 'MEDIUM PRIORITY: Alert created for review'
            : 'LOW PRIORITY: Transaction logged for monitoring'
        };
      
      default:
        return { riskScore: 0, result: 'Step completed' };
    }
  };

  const handleTransactionSubmit = async (data: { accountNumber: string; amount: number; description: string }) => {
    setStatus('in_progress');
    setProgress(0);
    setAlert({ show: false, message: '', type: 'warning' });
    setAnalysisResult(null);
    setCurrentAgentStep('');

    // Initialize agent steps
    const initialSteps: AgentStep[] = [
      {
        id: 'monitor',
        name: 'Transaction Monitor',
        description: 'Initial transaction screening and anomaly detection',
        icon: <Eye className="w-5 h-5" />,
        status: 'pending',
        details: ['Amount validation', 'Time pattern analysis', 'Frequency checking', 'Geographic validation']
      },
      {
        id: 'hybrid',
        name: 'Hybrid Analysis',
        description: 'ML model risk assessment and pattern recognition',
        icon: <Brain className="w-5 h-5" />,
        status: 'pending',
        details: ['Feature extraction', 'ML model prediction', 'Pattern matching', 'Behavioral analysis']
      },
      {
        id: 'ai_analysis',
        name: 'AI Deep Analysis',
        description: 'Advanced AI analysis using Gemini for complex patterns',
        icon: <Bot className="w-5 h-5" />,
        status: 'pending',
        details: ['Context understanding', 'Complex pattern detection', 'Risk factor identification', 'Confidence assessment']
      },
      {
        id: 'alert',
        name: 'Alert Generation',
        description: 'Risk evaluation and alert notifications',
        icon: <AlertTriangle className="w-5 h-5" />,
        status: 'pending',
        details: ['Risk threshold evaluation', 'Alert priority assignment', 'Notification routing', 'Case documentation']
      }
    ];
    setAgentSteps(initialSteps);

    // Simulate agent workflow steps
    const agentStepFlow = async () => {
      const stepDurations = [800, 1200, 1500, 600]; // ms for each step
      const stepNames = ['monitor', 'hybrid', 'ai_analysis', 'alert'];
      let finalRiskScore = 0;
      
      for (let i = 0; i < stepNames.length; i++) {
        const stepName = stepNames[i];
        setCurrentAgentStep(stepName);
        setProgress(25 * (i + 1));

        // Update step status to processing
        setAgentSteps(prev => prev.map(step => 
          step.id === stepName 
            ? { ...step, status: 'processing' as const }
            : step
        ));

        // Wait for step duration
        await new Promise(resolve => setTimeout(resolve, stepDurations[i]));

        // Complete the step with results
        const stepResults = getStepResults(stepName, data);
        
        // Store final risk score from alert step
        if (stepName === 'alert') {
          finalRiskScore = stepResults.riskScore || 0;
        }

        setAgentSteps(prev => prev.map(step => 
          step.id === stepName 
            ? { 
                ...step, 
                status: 'completed' as const,
                duration: stepDurations[i],
                ...stepResults
              }
            : step
        ));
      }
      
      return finalRiskScore;
    };

    try {
      const finalRiskScore = await agentStepFlow();
      const isFraud = finalRiskScore > 0.6;
      
      setProgress(100);
      setStatus('completed');
      setCurrentAgentStep('');
      
      setAnalysisResult({
        is_fraud: isFraud,
        risk_score: finalRiskScore,
        message: isFraud 
          ? 'Fraudulent transaction detected by agent analysis' 
          : 'Transaction verified as legitimate by agent analysis'
      });

      if (isFraud) {
        setAlert({
          show: true,
          message: 'Alert: Fraudulent transaction detected by security agents!',
          type: 'warning'
        });
      }

      // Reset status after a delay
      setTimeout(() => {
        setStatus('idle');
        setProgress(0);
        setCurrentAgentStep('');
      }, 5000);

    } catch (error) {
      setStatus('error');
      setProgress(0);
      setCurrentAgentStep('');
      setAlert({
        show: true,
        message: 'Error during agent analysis. Please try again.',
        type: 'error'
      });
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      
      <div className="flex-1 flex flex-col overflow-hidden md:ml-0">
        <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto">
            {/* Alert Banner */}
            <AlertBanner
              show={alert.show}
              message={alert.message}
              type={alert.type}
              onClose={() => setAlert({ ...alert, show: false })}
            />

            {/* Status Bar */}
            <StatusBar status={status} progress={progress} />

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
              {/* Left Column - Input Form */}
              <div className="space-y-6">
                <SimpleTransactionForm 
                  onSubmit={handleTransactionSubmit}
                  loading={status === 'in_progress'}
                />
                <AnalysisResultCard result={analysisResult} />
              </div>

              {/* Center Column - Agent Workflow */}
              <div className="space-y-6">
                <AgentWorkflowVisualization 
                  currentStep={currentAgentStep}
                  steps={agentSteps}
                />
              </div>

              {/* Right Column - Charts */}
              <div className="space-y-6">
                <TransactionsOverTimeChart />
                <FraudulentTransactionsChart />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default NewDashboard;