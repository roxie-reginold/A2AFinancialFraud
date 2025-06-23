#!/usr/bin/env python3
"""
Simple test script to verify the monitoring agent works correctly.
"""

import asyncio
import json
import logging
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from monitor_agent import MonitoringAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_monitoring_agent():
    """Test the monitoring agent functionality."""
    
    # Configuration
    project_id = "fraud-detection-adkhackathon"
    subscription_name = "transactions-sub"
    flagged_topic = "flagged-transactions"
    
    # Create monitoring agent
    monitoring_agent = MonitoringAgent(
        name="TestMonitoringAgent",
        project_id=project_id,
        subscription_name=subscription_name,
        flagged_topic=flagged_topic
    )
    
    # Test fraud rules directly
    logger.info("Testing fraud detection rules...")
    
    # Test case 1: High amount transaction
    test_transaction_1 = {
        "transaction_id": "test_001",
        "amount": 500.0,
        "timestamp": "2024-01-01T12:00:00Z",
        "features": {}
    }
    
    is_flagged, reasons = monitoring_agent.apply_fraud_rules(test_transaction_1)
    logger.info(f"Test 1 - High Amount: Flagged={is_flagged}, Reasons={reasons}")
    
    # Test case 2: Normal transaction
    test_transaction_2 = {
        "transaction_id": "test_002", 
        "amount": 50.0,
        "timestamp": "2024-01-01T12:00:00Z",
        "features": {}
    }
    
    is_flagged, reasons = monitoring_agent.apply_fraud_rules(test_transaction_2)
    logger.info(f"Test 2 - Normal Amount: Flagged={is_flagged}, Reasons={reasons}")
    
    # Test case 3: Suspicious features
    test_transaction_3 = {
        "transaction_id": "test_003",
        "amount": 100.0,
        "timestamp": "2024-01-01T12:00:00Z",
        "features": {
            "V17": -3.0,  # Below threshold
            "V14": -3.0   # Below threshold
        }
    }
    
    is_flagged, reasons = monitoring_agent.apply_fraud_rules(test_transaction_3)
    logger.info(f"Test 3 - Suspicious Features: Flagged={is_flagged}, Reasons={reasons}")
    
    logger.info("✅ All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_monitoring_agent())
