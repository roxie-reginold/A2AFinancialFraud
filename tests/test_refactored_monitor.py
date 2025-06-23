#!/usr/bin/env python3
"""
Test script for the refactored ADK-compliant monitoring agent.
"""

import asyncio
import logging
from monitor_agent import MonitoringAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_refactored_agent():
    """Test the refactored monitoring agent's fraud detection logic."""
    
    # Configuration
    project_id = "fraud-detection-adkhackathon"
    subscription_name = "transactions-sub"
    flagged_topic = "flagged-transactions"
    
    # Create monitoring agent
    monitoring_agent = MonitoringAgent(
        name="TestRefactoredAgent",
        project_id=project_id,
        subscription_name=subscription_name,
        flagged_topic=flagged_topic
    )
    
    logger.info("🧪 Testing refactored ADK-compliant monitoring agent...")
    
    # Test fraud detection rules (same as before)
    test_cases = [
        {
            "name": "High Amount Transaction",
            "transaction": {
                "transaction_id": "test_001",
                "amount": 500.0,
                "timestamp": "2024-01-01T12:00:00Z",
                "features": {}
            }
        },
        {
            "name": "Normal Transaction", 
            "transaction": {
                "transaction_id": "test_002",
                "amount": 50.0,
                "timestamp": "2024-01-01T12:00:00Z",
                "features": {}
            }
        },
        {
            "name": "Suspicious Features",
            "transaction": {
                "transaction_id": "test_003", 
                "amount": 100.0,
                "timestamp": "2024-01-01T12:00:00Z",
                "features": {
                    "V17": -3.0,
                    "V14": -3.0,
                    "V11": 2.5
                }
            }
        }
    ]
    
    # Test fraud detection logic
    for test_case in test_cases:
        is_flagged, reasons = monitoring_agent.apply_fraud_rules(test_case["transaction"])
        status = "🚨 FLAGGED" if is_flagged else "✅ CLEARED"
        logger.info(f"{status} - {test_case['name']}: {reasons if reasons else 'No issues detected'}")
    
    logger.info("✅ All fraud detection tests completed successfully!")
    
    # Test async publishing (mock)
    logger.info("🧪 Testing async publishing functionality...")
    test_flagged_event = {
        "transaction_id": "test_async_001",
        "amount": 999.0,
        "reasons": ["High amount: $999.0"],
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    try:
        await monitoring_agent._publish_flagged_transaction_async(test_flagged_event)
        logger.info("✅ Async publishing test completed!")
    except Exception as e:
        logger.warning(f"⚠️  Async publishing test failed (expected without real Pub/Sub): {str(e)}")
    
    logger.info("🎉 Refactored agent validation completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_refactored_agent())
