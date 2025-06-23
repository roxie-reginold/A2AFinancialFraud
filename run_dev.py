#!/usr/bin/env python3
"""
Development runner for ADK Financial Fraud Detection System
Simplified startup for development and testing.
"""

import os
import asyncio
import logging
from datetime import datetime

# Set development environment
os.environ["ENVIRONMENT"] = "development"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fraud-detection-dev"

# Import our services
from api.health import HealthCheckService
from api.fraud_api import FraudDetectionAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_development_server():
    """Run the fraud detection system in development mode."""
    logger.info("🚀 Starting A2A Fraud Detection - Development Mode")
    
    # Get port from environment (Cloud Run sets PORT)
    port = int(os.getenv("PORT", "8080"))
    
    try:
        # Initialize FastAPI services
        health_service = HealthCheckService()
        fraud_api = FraudDetectionAPI()
        
        # Check if running on Cloud Run
        if os.getenv("PORT"):
            # Cloud Run deployment - single port with full API
            logger.info(f"🌟 Cloud Run deployment detected - running on port {port}")
            
            # Start fraud API service (includes health endpoints)
            api_server = await fraud_api.start_server(port=port, host="0.0.0.0")
            logger.info(f"✅ Full API service started on http://0.0.0.0:{port}")
            logger.info(f"📋 API Documentation: http://0.0.0.0:{port}/docs")
            
            await api_server.serve()
        else:
            # Local development - multiple ports
            logger.info("Environment: Development (no Google Cloud required)")
            
            # Start servers
            health_server = await health_service.start_server(port=8080)
            api_server = await fraud_api.start_server(port=8000)
            
            # Run servers concurrently
            await asyncio.gather(
                health_server.serve(),
                api_server.serve()
            )
        
    except KeyboardInterrupt:
        logger.info("👋 Shutting down development server...")
    except Exception as e:
        logger.error(f"❌ Error: {e}")

def main():
    """Main entry point for development server."""
    print("=" * 60)
    print("🔍 ADK Financial Fraud Detection System - Development")
    print("=" * 60)
    print("📱 Health API:     http://localhost:8080/docs")
    print("🔗 Fraud API:      http://localhost:8000/docs") 
    print("📊 Health Check:   http://localhost:8080/health")
    print("📈 Metrics:        http://localhost:8080/metrics")
    print("=" * 60)
    print("💡 Press Ctrl+C to stop")
    print()
    
    # Run the async server
    asyncio.run(run_development_server())

if __name__ == "__main__":
    main()