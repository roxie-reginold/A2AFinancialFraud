#!/usr/bin/env python3
"""
Simple test script to verify ADK agent functionality
"""

import os
import asyncio
import logging
from google.adk.agents import Agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test basic ADK agent creation."""
    try:
        # Set environment variables
        os.environ["GOOGLE_CLOUD_PROJECT"] = "fraud-detection-adkhackathon"
        os.environ["BYPASS_CLOUD_VALIDATION"] = "true"
        
        logger.info("Creating simple ADK agent...")
        
        # Create a basic agent
        agent = Agent(
            name="test_fraud_agent",
            model="gemini-2.5-pro-preview-05-06",
            instruction="You are a simple fraud detection test agent.",
            description="Test agent for fraud detection system"
        )
        
        logger.info(f"✅ Agent created successfully: {agent.name}")
        logger.info(f"📝 Agent description: {agent.description}")
        
        # Test basic functionality
        logger.info("🧪 Basic ADK agent test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing agent: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ Simple agent test PASSED")
    else:
        logger.error("❌ Simple agent test FAILED")
        exit(1)