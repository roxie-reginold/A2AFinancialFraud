#!/usr/bin/env python3
"""
Unified Development and Production Runner for ADK Financial Fraud Detection System v2
"""

import asyncio
import os
import logging
import signal
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point that determines run mode based on environment."""
    
    # Determine if we're in development or production
    environment = os.getenv('ENVIRONMENT', 'development')
    port = int(os.getenv('PORT', '8080'))
    
    logger.info(f"🚀 Starting ADK Financial Fraud Detection System v2 in {environment} mode")
    logger.info(f"🌐 Server will run on port {port}")
    
    if environment == 'production' or os.getenv('PORT'):
        # Production mode: Run unified API server with frontend
        await run_production_server(port)
    else:
        # Development mode: Run development servers
        await run_development_servers()

async def run_production_server(port: int):
    """Run production server with unified backend + frontend."""
    try:
        # Import after environment is set
        from api.fraud_api import FraudDetectionAPI
        
        logger.info("🏭 Starting production server...")
        
        # Initialize the API service
        api_service = FraudDetectionAPI()
        
        # Start the server
        import uvicorn
        config = uvicorn.Config(
            app=api_service.app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True,
            reload=False,
            workers=1
        )
        
        server = uvicorn.Server(config)
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            logger.info("🛑 Received shutdown signal, stopping server...")
            server.should_exit = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info(f"✅ Production server running on http://0.0.0.0:{port}")
        logger.info(f"📱 Frontend: http://0.0.0.0:{port}/")
        logger.info(f"🔌 API: http://0.0.0.0:{port}/api/v1")
        logger.info(f"📖 Docs: http://0.0.0.0:{port}/docs")
        logger.info(f"❤️  Health: http://0.0.0.0:{port}/health")
        
        await server.serve()
        
    except Exception as e:
        logger.error(f"❌ Error starting production server: {str(e)}")
        raise

async def run_development_servers():
    """Run development mode with separate backend and frontend."""
    try:
        logger.info("🛠️  Starting development servers...")
        
        # Start main orchestrator system
        from main import main as start_orchestrator
        
        # Run in background
        orchestrator_task = asyncio.create_task(start_orchestrator())
        
        logger.info("✅ Development servers started")
        logger.info("🔌 Backend API: http://localhost:8001")
        logger.info("❤️  Health Check: http://localhost:8080") 
        logger.info("📱 Frontend: Start separately with 'cd frontend && npm run dev'")
        
        # Keep running
        await orchestrator_task
        
    except Exception as e:
        logger.error(f"❌ Error starting development servers: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Application stopped by user")
    except Exception as e:
        logger.error(f"❌ Application failed: {str(e)}")
        exit(1)