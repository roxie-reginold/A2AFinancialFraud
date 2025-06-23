#!/usr/bin/env python3
"""
Demo script for ADK Financial Fraud Detection System
Shows UI and GCP integration workflows
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_banner():
    """Print demo banner."""
    print("=" * 80)
    print("🔍 ADK Financial Fraud Detection System - UI & GCP Demo")
    print("=" * 80)
    print()

def print_section(title: str):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")

async def demo_api_endpoints():
    """Demo API endpoint functionality."""
    print_section("API Endpoints Demo")
    
    try:
        import requests
        
        # Health check
        print("🔍 Testing Health Check...")
        health_response = requests.get("http://localhost:8080/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Health check successful")
            health_data = health_response.json()
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Healthy Agents: {health_data.get('healthy_agents', 0)}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
        
        # Detailed health
        print("\n🔍 Testing Detailed Health...")
        detailed_response = requests.get("http://localhost:8080/health/detailed", timeout=5)
        if detailed_response.status_code == 200:
            print("✅ Detailed health check successful")
            detailed_data = detailed_response.json()
            print(f"   System Health: {detailed_data.get('system', {}).get('status', 'unknown')}")
        else:
            print(f"❌ Detailed health check failed: {detailed_response.status_code}")
        
        # Metrics
        print("\n🔍 Testing Metrics Endpoint...")
        metrics_response = requests.get("http://localhost:8080/metrics", timeout=5)
        if metrics_response.status_code == 200:
            print("✅ Metrics endpoint successful")
            print("   Sample metrics:")
            metrics_lines = metrics_response.text.split('\n')[:5]
            for line in metrics_lines:
                if line.strip():
                    print(f"   {line}")
        else:
            print(f"❌ Metrics endpoint failed: {metrics_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API connection failed: {e}")
        print("💡 Make sure the system is running: python main.py")
    except ImportError:
        print("❌ requests library not available")
        print("💡 Install with: pip install requests")

def demo_gcp_config():
    """Demo GCP configuration checking."""
    print_section("GCP Configuration Demo")
    
    # Check environment variables
    gcp_vars = [
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_API_KEY", 
        "GOOGLE_APPLICATION_CREDENTIALS"
    ]
    
    print("🔍 Checking GCP Environment Variables...")
    for var in gcp_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            display_value = value if var == "GOOGLE_CLOUD_PROJECT" else f"{value[:10]}..." if len(value) > 10 else "***"
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set")
    
    # Check bypass mode
    bypass = os.getenv("BYPASS_CLOUD_VALIDATION", "false").lower() == "true"
    if bypass:
        print("⚠️  BYPASS_CLOUD_VALIDATION is enabled (development mode)")
    else:
        print("🔒 BYPASS_CLOUD_VALIDATION is disabled (production mode)")

def demo_pubsub_simulation():
    """Simulate Pub/Sub message flow."""
    print_section("Pub/Sub Message Flow Simulation")
    
    # Simulate message flow
    topics = [
        "transactions-topic",
        "flagged-transactions",
        "analysis-results", 
        "fraud-alerts"
    ]
    
    print("📡 Simulating Pub/Sub message flow:")
    
    for i, topic in enumerate(topics, 1):
        print(f"   {i}. Publishing to {topic}...")
        time.sleep(0.5)  # Simulate processing time
        print(f"      ✅ Message published and processed")
    
    print("\n📊 Message Flow Summary:")
    print("   1. Transaction received → transactions-topic")
    print("   2. Risk analysis flags transaction → flagged-transactions") 
    print("   3. ML/AI analysis completes → analysis-results")
    print("   4. High risk detected → fraud-alerts")
    print("   5. Alert notifications sent to admins")

def demo_bigquery_simulation():
    """Simulate BigQuery data operations."""
    print_section("BigQuery Data Operations Simulation")
    
    tables = [
        ("fraud_transactions", "Transaction records"),
        ("fraud_analysis", "Analysis results"),
        ("fraud_alerts", "Alert records"),
        ("fraud_reports", "Generated reports")
    ]
    
    print("🗄️  Simulating BigQuery operations:")
    
    for table, description in tables:
        print(f"   📝 Inserting data into {table}")
        print(f"      Description: {description}")
        time.sleep(0.3)
        print(f"      ✅ Data inserted successfully")
    
    # Simulate query
    print("\n📊 Simulating analytical queries:")
    queries = [
        "Fraud detection rate by hour",
        "Top risk factors analysis", 
        "Geographic fraud patterns",
        "Model performance metrics"
    ]
    
    for query in queries:
        print(f"   🔍 Running: {query}")
        time.sleep(0.4)
        print(f"      ✅ Query completed")

def demo_transaction_flow():
    """Demo a complete transaction analysis flow."""
    print_section("Complete Transaction Analysis Flow")
    
    # Sample transaction
    transaction = {
        "transaction_id": "demo_tx_12345",
        "amount": 2750.00,
        "description": "ATM withdrawal midnight",
        "account": "ACC789012",
        "timestamp": datetime.now().isoformat()
    }
    
    print("💳 Sample Transaction:")
    for key, value in transaction.items():
        print(f"   {key}: {value}")
    
    print("\n🔄 Processing Flow:")
    
    steps = [
        ("1. Transaction Ingestion", "Transaction received via API"),
        ("2. Initial Monitoring", "MonitoringAgent flags suspicious amount/time"),
        ("3. Risk Analysis", "HybridAnalysisAgent runs ML + AI analysis"),
        ("4. Risk Scoring", f"Risk score calculated: 0.85 (HIGH RISK)"),
        ("5. Alert Generation", "AlertAgent creates fraud alert"),
        ("6. Data Storage", "Results stored in BigQuery"),
        ("7. Notification", "Email/Slack alerts sent to security team")
    ]
    
    for step, description in steps:
        print(f"   {step}: {description}")
        time.sleep(0.8)
        print(f"      ✅ Completed")
    
    print("\n🚨 FRAUD ALERT GENERATED!")
    print("   Risk Score: 0.85")
    print("   Risk Factors: High amount, Off-hours transaction, ATM withdrawal")
    print("   Recommendation: Manual review required")

def print_ui_instructions():
    """Print UI usage instructions."""
    print_section("UI Usage Instructions")
    
    print("🖥️  Web Dashboard Usage:")
    print("   1. Start the system:")
    print("      python main.py  # Full system")
    print("      python run_dev.py  # Development mode")
    print()
    print("   2. Start the frontend:")
    print("      cd frontend")
    print("      npm install")
    print("      npm run dev")
    print()
    print("   3. Open browser to:")
    print("      Frontend: http://localhost:5173")
    print("      Health API: http://localhost:8080/docs")
    print("      Fraud API: http://localhost:8001/docs")
    print()
    print("   4. Test transaction:")
    print("      - Enter account number: ACC123456")
    print("      - Enter amount: 1500.00")
    print("      - Enter description: Online purchase")
    print("      - Click 'Analyze Transaction'")
    print("      - Watch progress bar and results")

def print_gcp_instructions():
    """Print GCP monitoring instructions."""
    print_section("GCP Monitoring Instructions")
    
    print("☁️  Google Cloud Platform Setup:")
    print("   1. Setup GCP resources:")
    print("      python scripts/setup_gcp_resources.py")
    print()
    print("   2. Monitor Pub/Sub:")
    print("      gcloud pubsub topics list")
    print("      gcloud pubsub subscriptions pull transactions-sub --limit=5")
    print()
    print("   3. Query BigQuery data:")
    print("      # Recent transactions")
    print("      SELECT * FROM fraud_detection.fraud_transactions")
    print("      ORDER BY created_at DESC LIMIT 10;")
    print()
    print("   4. Check system health:")
    print("      curl http://localhost:8080/health")
    print("      curl http://localhost:8080/metrics")

async def main():
    """Main demo function."""
    print_banner()
    
    # Run demo sections
    await demo_api_endpoints()
    await asyncio.sleep(1)
    
    demo_gcp_config()
    await asyncio.sleep(1)
    
    demo_pubsub_simulation()
    await asyncio.sleep(1)
    
    demo_bigquery_simulation()
    await asyncio.sleep(1)
    
    demo_transaction_flow()
    await asyncio.sleep(1)
    
    print_ui_instructions()
    print_gcp_instructions()
    
    print_section("Demo Complete")
    print("🎉 Demo completed successfully!")
    print()
    print("📖 For detailed instructions, see:")
    print("   docs/UI_AND_GCP_FLOW_GUIDE.md")
    print()
    print("🚀 Ready to start the system:")
    print("   python main.py")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())