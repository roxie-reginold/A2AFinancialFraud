#!/usr/bin/env python3
"""
Demo Script: Agent Workflow UI Demonstration
Shows the new agent-based fraud detection UI with step-by-step visualization
"""

import asyncio
import json
import logging
import webbrowser
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_banner():
    """Print demo banner."""
    print("=" * 80)
    print("🤖 ADK Financial Fraud Detection - Agent Workflow UI Demo")
    print("=" * 80)
    print("🔍 This demo showcases the new step-by-step agent visualization")
    print("👥 Watch as each agent processes the transaction sequentially")
    print("📊 See real-time risk scoring and decision making")
    print("=" * 80)
    print()

def print_agent_overview():
    """Print overview of agents in the system."""
    print("🤖 FRAUD DETECTION AGENT OVERVIEW")
    print("=" * 50)
    
    agents = [
        {
            "name": "Transaction Monitor 👁️",
            "role": "Initial Screening",
            "description": "Validates amounts, checks patterns, flags anomalies",
            "checks": ["Amount validation", "Time pattern analysis", "Frequency checking", "Geographic validation"]
        },
        {
            "name": "Hybrid Analysis Agent 🧠", 
            "role": "ML Analysis",
            "description": "Machine learning model assessment and pattern recognition",
            "checks": ["Feature extraction", "ML model prediction", "Pattern matching", "Behavioral analysis"]
        },
        {
            "name": "AI Deep Analysis 🤖",
            "role": "Advanced AI",
            "description": "Gemini AI for complex pattern detection and context understanding",
            "checks": ["Context understanding", "Complex pattern detection", "Risk factor identification", "Confidence assessment"]
        },
        {
            "name": "Alert Generation ⚠️",
            "role": "Decision & Alert",
            "description": "Final risk evaluation and alert notification management",
            "checks": ["Risk threshold evaluation", "Alert priority assignment", "Notification routing", "Case documentation"]
        }
    ]
    
    for i, agent in enumerate(agents, 1):
        print(f"\n{i}. {agent['name']}")
        print(f"   Role: {agent['role']}")
        print(f"   Description: {agent['description']}")
        print(f"   Capabilities:")
        for check in agent['checks']:
            print(f"     • {check}")
    
    print("\n" + "=" * 50)

def print_workflow_steps():
    """Print the workflow process."""
    print("\n🔄 AGENT WORKFLOW PROCESS")
    print("=" * 50)
    
    steps = [
        ("1. Transaction Received", "User submits transaction via web interface"),
        ("2. Monitor Agent Activates", "Initial screening begins - amount, time, frequency checks"),
        ("3. Risk Flags Generated", "Monitor identifies potential risk factors"),
        ("4. Hybrid Agent Analysis", "ML models analyze transaction features and patterns"),
        ("5. AI Deep Analysis", "Gemini AI performs contextual analysis"),
        ("6. Risk Score Calculation", "Combined risk assessment from all agents"),
        ("7. Alert Decision", "Alert agent determines final verdict and notifications"),
        ("8. Results Display", "User sees final verdict with complete agent workflow")
    ]
    
    for step, description in steps:
        print(f"{step}: {description}")
        time.sleep(0.3)
    
    print("=" * 50)

def print_demo_scenarios():
    """Print demo scenarios to try."""
    print("\n🎯 DEMO SCENARIOS TO TRY")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "🟢 LOW RISK TRANSACTION",
            "amount": "$25.00",
            "description": "Coffee shop purchase",
            "expected": "All agents show LOW risk, transaction approved"
        },
        {
            "name": "🟡 MEDIUM RISK TRANSACTION", 
            "amount": "$850.00",
            "description": "Online electronics purchase",
            "expected": "Monitor flags amount, Hybrid shows medium risk, AI confirms patterns"
        },
        {
            "name": "🔴 HIGH RISK TRANSACTION",
            "amount": "$3,500.00", 
            "description": "ATM cash withdrawal midnight",
            "expected": "All agents flag issues, high risk score, fraud alert generated"
        },
        {
            "name": "🚨 SUSPICIOUS TRANSACTION",
            "amount": "$5,000.00",
            "description": "Multiple cash withdrawals",
            "expected": "Immediate flags, AI detects complex patterns, priority alert"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}")
        print(f"   Amount: {scenario['amount']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Expected: {scenario['expected']}")
    
    print("=" * 50)

def print_ui_features():
    """Print UI feature highlights."""
    print("\n✨ NEW UI FEATURES")
    print("=" * 50)
    
    features = [
        "🔄 Real-time Agent Progression",
        "📊 Individual Agent Risk Scores", 
        "⏱️ Processing Time Tracking",
        "📝 Detailed Step Results",
        "🎯 Visual Status Indicators",
        "🔗 Agent Flow Connections",
        "📈 Risk Score Evolution",
        "⚠️ Alert Priority Visualization",
        "📋 Complete Analysis Summary",
        "🔍 Expandable Detail Views"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("=" * 50)

def print_getting_started():
    """Print getting started instructions."""
    print("\n🚀 GETTING STARTED")
    print("=" * 50)
    
    print("1. Start the Backend System:")
    print("   python main.py")
    print("   (System will run on ports 8001 for API, 8080 for health)")
    print()
    
    print("2. Start the Frontend Dashboard:")
    print("   cd frontend")
    print("   npm install")
    print("   npm run dev")
    print("   (Frontend will run on http://localhost:5173)")
    print()
    
    print("3. Open Your Browser:")
    print("   🖥️  Dashboard: http://localhost:5173")
    print("   📊 Health API: http://localhost:8080/docs")
    print("   🔗 Fraud API: http://localhost:8001/docs")
    print()
    
    print("4. Test Transaction Analysis:")
    print("   • Enter account number (e.g., ACC123456)")
    print("   • Enter transaction amount")
    print("   • Enter description")
    print("   • Click 'Analyze Transaction'")
    print("   • Watch the agent workflow in the center column!")
    print()
    
    print("=" * 50)

def simulate_agent_analysis():
    """Simulate the agent analysis process."""
    print("\n🔄 SIMULATING AGENT ANALYSIS")
    print("=" * 50)
    
    # Sample transaction
    transaction = {
        "account": "ACC789012",
        "amount": 2750.00,
        "description": "ATM withdrawal midnight",
        "timestamp": datetime.now().isoformat()
    }
    
    print("💳 Sample Transaction:")
    for key, value in transaction.items():
        print(f"   {key}: {value}")
    
    print("\n🤖 Agent Analysis Simulation:")
    
    # Agent steps with realistic timings and results
    agent_steps = [
        {
            "agent": "👁️ Transaction Monitor",
            "duration": 0.8,
            "checks": ["Amount: $2,750 (HIGH)", "Time: 23:45 (SUSPICIOUS)", "Location: ATM (FLAGGED)"],
            "result": "FLAGGED for further analysis",
            "risk_score": 0.6
        },
        {
            "agent": "🧠 Hybrid Analysis",
            "duration": 1.2, 
            "checks": ["ML Model: HIGH RISK", "Pattern: Unusual amount", "Behavior: Off-hours activity"],
            "result": "ML model detected suspicious patterns",
            "risk_score": 0.75
        },
        {
            "agent": "🤖 AI Deep Analysis",
            "duration": 1.5,
            "checks": ["Context: Midnight withdrawal", "Pattern: Large cash amount", "Risk factors: 5 identified"],
            "result": "AI detected high-risk transaction patterns",
            "risk_score": 0.85
        },
        {
            "agent": "⚠️ Alert Generation",
            "duration": 0.6,
            "checks": ["Risk threshold: EXCEEDED", "Alert priority: HIGH", "Notifications: SENT"],
            "result": "HIGH PRIORITY: Fraud alert generated", 
            "risk_score": 0.87
        }
    ]
    
    total_time = 0
    for i, step in enumerate(agent_steps, 1):
        print(f"\n  Step {i}: {step['agent']}")
        print(f"    Processing...")
        time.sleep(min(step['duration'], 1.0))  # Simulate processing time
        total_time += step['duration']
        
        print(f"    ✅ Completed in {step['duration']}s")
        print(f"    Risk Score: {step['risk_score']:.2f}")
        print(f"    Result: {step['result']}")
        print(f"    Checks performed:")
        for check in step['checks']:
            print(f"      • {check}")
    
    print(f"\n🏁 FINAL ANALYSIS RESULT:")
    print(f"   Total Processing Time: {total_time:.1f}s")
    print(f"   Final Risk Score: 0.87")
    print(f"   Classification: FRAUDULENT TRANSACTION")
    print(f"   Action: HIGH PRIORITY ALERT GENERATED")
    print(f"   Recommendation: MANUAL REVIEW REQUIRED")
    
    print("=" * 50)

async def main():
    """Main demo function."""
    print_banner()
    
    print_agent_overview()
    await asyncio.sleep(1)
    
    print_workflow_steps()
    await asyncio.sleep(1)
    
    print_demo_scenarios()
    await asyncio.sleep(1)
    
    print_ui_features()
    await asyncio.sleep(1)
    
    simulate_agent_analysis()
    await asyncio.sleep(1)
    
    print_getting_started()
    
    # Ask if user wants to open browser
    try:
        response = input("\n🌐 Would you like to open the dashboard in your browser? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("🚀 Opening dashboard...")
            webbrowser.open('http://localhost:5173')
            webbrowser.open('http://localhost:8080/docs')
            print("✅ Browser tabs opened!")
        else:
            print("💡 You can manually open:")
            print("   Dashboard: http://localhost:5173")
            print("   Health API: http://localhost:8080/docs")
    except KeyboardInterrupt:
        print("\n👋 Demo completed!")
    
    print("\n" + "=" * 80)
    print("🎉 Agent Workflow UI Demo Complete!")
    print("📖 For detailed documentation, see: docs/UI_AND_GCP_FLOW_GUIDE.md")
    print("🚀 Ready to start exploring the agent-based fraud detection!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())