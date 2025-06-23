#!/usr/bin/env python3
"""
Test script for the Agent Workflow UI
Starts both backend and instructions for frontend testing
"""

import asyncio
import subprocess
import time
import webbrowser
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_banner():
    """Print test banner."""
    print("=" * 80)
    print("🧪 Agent Workflow UI Test Script")
    print("=" * 80)
    print("🔍 This script helps you test the new agent workflow visualization")
    print("📱 Frontend: http://localhost:5173")
    print("🔗 API: http://localhost:8001/docs")
    print("📊 Health: http://localhost:8080/docs")
    print("=" * 80)
    print()

def check_backend_running():
    """Check if backend is already running."""
    import requests
    try:
        response = requests.get("http://localhost:8080/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def check_frontend_running():
    """Check if frontend is already running."""
    import requests
    try:
        response = requests.get("http://localhost:5173", timeout=2)
        return response.status_code == 200
    except:
        return False

async def start_backend():
    """Start the backend system."""
    if check_backend_running():
        print("✅ Backend already running")
        return None
    
    print("🚀 Starting backend system...")
    try:
        # Start the backend process
        process = subprocess.Popen(
            ["python", "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for startup
        await asyncio.sleep(3)
        
        # Check if it's running
        if check_backend_running():
            print("✅ Backend started successfully")
            return process
        else:
            print("❌ Backend failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def print_frontend_instructions():
    """Print instructions for starting frontend."""
    print("\n📱 FRONTEND SETUP INSTRUCTIONS")
    print("=" * 50)
    
    if check_frontend_running():
        print("✅ Frontend already running at http://localhost:5173")
    else:
        print("To start the frontend:")
        print("1. Open a new terminal")
        print("2. Navigate to the frontend directory:")
        print("   cd frontend")
        print("3. Install dependencies (if not done already):")
        print("   npm install")
        print("4. Start the development server:")
        print("   npm run dev")
        print("5. Frontend will be available at: http://localhost:5173")
    
    print("=" * 50)

def print_test_scenarios():
    """Print test scenarios."""
    print("\n🎯 TEST SCENARIOS")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "🟢 Normal Transaction",
            "account": "ACC123456",
            "amount": "50.00",
            "description": "Coffee shop purchase",
            "expected": "Low risk through all agents"
        },
        {
            "name": "🟡 Medium Risk",
            "account": "ACC789012", 
            "amount": "1200.00",
            "description": "Online purchase",
            "expected": "Monitor flags amount, moderate ML risk"
        },
        {
            "name": "🔴 High Risk",
            "account": "ACC555999",
            "amount": "3500.00", 
            "description": "ATM cash withdrawal",
            "expected": "All agents flag issues, high risk score"
        },
        {
            "name": "🚨 Suspicious Pattern",
            "account": "ACC666777",
            "amount": "5000.00",
            "description": "Cash withdrawal midnight", 
            "expected": "Immediate high-risk flags, fraud alert"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   Account: {scenario['account']}")
        print(f"   Amount: ${scenario['amount']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Expected: {scenario['expected']}")
    
    print("=" * 50)

def print_what_to_watch():
    """Print what to watch for in the UI."""
    print("\n👀 WHAT TO WATCH FOR IN THE UI")
    print("=" * 50)
    
    checkpoints = [
        "🔄 Agent steps appear in center column when you submit",
        "👁️ Transaction Monitor shows as 'processing' first",
        "🧠 Hybrid Analysis agent activates second",
        "🤖 AI Deep Analysis runs third with context understanding",
        "⚠️ Alert Generation makes final decision",
        "📊 Each agent shows individual risk scores",
        "⏱️ Processing times are displayed for each step",
        "💬 Result messages explain what each agent found",
        "🎯 Final verdict appears in Analysis Result card",
        "🚨 High-risk transactions trigger alert banner"
    ]
    
    for checkpoint in checkpoints:
        print(f"  {checkpoint}")
    
    print("=" * 50)

def print_troubleshooting():
    """Print troubleshooting tips."""
    print("\n🔧 TROUBLESHOOTING")
    print("=" * 50)
    
    issues = [
        {
            "issue": "Agents not showing",
            "solution": "Check browser console for errors, refresh page"
        },
        {
            "issue": "Processing stuck",
            "solution": "Check backend logs, restart backend if needed"
        },
        {
            "issue": "No risk scores",
            "solution": "Verify agent workflow logic in NewDashboard.tsx"
        },
        {
            "issue": "API errors",
            "solution": "Check http://localhost:8080/health for backend status"
        }
    ]
    
    for issue_info in issues:
        print(f"• Issue: {issue_info['issue']}")
        print(f"  Solution: {issue_info['solution']}")
    
    print("=" * 50)

async def main():
    """Main test function."""
    print_banner()
    
    # Check Python requests library
    try:
        import requests
    except ImportError:
        print("❌ requests library not found. Install with: pip install requests")
        return
    
    # Start backend
    backend_process = await start_backend()
    
    # Give backend time to fully start
    if backend_process:
        print("⏳ Waiting for backend to fully initialize...")
        await asyncio.sleep(5)
    
    # Print frontend instructions
    print_frontend_instructions()
    
    # Print test scenarios
    print_test_scenarios()
    
    # Print what to watch for
    print_what_to_watch()
    
    # Print troubleshooting
    print_troubleshooting()
    
    # Ask if user wants to open browser
    try:
        print("\n🌐 BROWSER SETUP")
        print("=" * 50)
        
        response = input("Open dashboard in browser? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            if check_frontend_running():
                print("🚀 Opening dashboard...")
                webbrowser.open('http://localhost:5173')
            else:
                print("⚠️ Frontend not running yet. Start it first, then visit:")
                print("   http://localhost:5173")
            
            # Also open API docs
            webbrowser.open('http://localhost:8080/docs')
            print("✅ Browser tabs opened!")
        
        print("\n📖 QUICK START:")
        print("1. Make sure frontend is running (npm run dev)")
        print("2. Go to http://localhost:5173")
        print("3. Fill in transaction form")
        print("4. Click 'Analyze Transaction'")
        print("5. Watch the agent workflow in the center column!")
        
        input("\nPress Enter to continue or Ctrl+C to exit...")
        
        # Keep backend running
        if backend_process:
            print("\n🔄 Backend running... Press Ctrl+C to stop")
            try:
                backend_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping backend...")
                backend_process.terminate()
                await asyncio.sleep(2)
                print("✅ Backend stopped")
        
    except KeyboardInterrupt:
        print("\n👋 Test session ended!")
        if backend_process:
            backend_process.terminate()

if __name__ == "__main__":
    asyncio.run(main())