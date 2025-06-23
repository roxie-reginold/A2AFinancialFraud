#!/usr/bin/env python3
"""
ADK Financial Fraud Detection System - Main Orchestrator

This is the main entry point for the fraud detection system that coordinates
all agents using the proper ADK framework structure.
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, List, Optional
from datetime import datetime
import json
import os

# Import configuration
from config.settings import settings

# Import our ADK-based agents
from agents.analysis_agent import AnalysisAgent
from agents.hybrid_analysis_agent import HybridAnalysisAgent
from agents.monitor_agent import MonitoringAgent
from agents.alert_agent import AlertAgent

# Import FastAPI services
from api.health import HealthCheckService
from api.fraud_api import FraudDetectionAPI

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.monitoring.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FraudDetectionOrchestrator:
    """
    Main orchestrator for the fraud detection system using ADK agents.
    
    Manages the lifecycle of all agents and provides:
    - Agent initialization and coordination
    - Health monitoring and management
    - Graceful shutdown handling
    - System status reporting
    """
    
    def __init__(self):
        """Initialize the orchestrator with all agents."""
        self.agents = {}
        self.running = False
        self.health_service = None
        self.api_service = None
        self._agent_health = {}
        
        # Initialize agents
        self._initialize_agents()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("FraudDetectionOrchestrator initialized")
    
    def _initialize_agents(self):
        """Initialize all fraud detection agents."""
        try:
            # Initialize monitoring agent
            self.agents['monitor'] = MonitoringAgent()
            self._agent_health['monitor'] = True
            logger.info("✅ MonitoringAgent initialized")
            
            # Initialize analysis agents
            self.agents['analysis'] = AnalysisAgent()
            self._agent_health['analysis'] = True
            logger.info("✅ AnalysisAgent initialized")
            
            self.agents['hybrid'] = HybridAnalysisAgent()
            self._agent_health['hybrid'] = True
            logger.info("✅ HybridAnalysisAgent initialized")
            
            # Initialize alert agent
            self.agents['alert'] = AlertAgent()
            self._agent_health['alert'] = True
            logger.info("✅ AlertAgent initialized")
            
            logger.info(f"🎯 All {len(self.agents)} agents initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing agents: {str(e)}")
            raise
    
    async def start_system(self):
        """Start the complete fraud detection system."""
        try:
            logger.info("🚀 Starting ADK Financial Fraud Detection System...")
            self.running = True
            
            # Start health check service
            self.health_service = HealthCheckService(orchestrator=self)
            self.health_server = await self.health_service.start_server(port=8080)
            # Start the server in background
            asyncio.create_task(self.health_server.serve())
            logger.info("✅ Health check service started")
            
            # Start API service
            self.api_service = FraudDetectionAPI(orchestrator=self)
            self.api_server = await self.api_service.start_server(port=8001)
            # Start the server in background
            asyncio.create_task(self.api_server.serve())
            logger.info("✅ API service started")
            
            # Start monitoring
            await self.agents['monitor'].start_monitoring()
            logger.info("✅ Transaction monitoring started")
            
            logger.info("🎉 Fraud Detection System fully operational!")
            
            # Run main loop
            await self._run_main_loop()
            
        except Exception as e:
            logger.error(f"❌ Error starting system: {str(e)}")
            await self.shutdown_system()
            raise
    
    async def _run_main_loop(self):
        """Main system loop for processing transactions."""
        try:
            logger.info("🔄 Starting main processing loop...")
            
            # Demo transaction processing
            sample_transactions = [
                {
                    "transaction_id": "demo_tx_001",
                    "amount": 150.00,
                    "timestamp": datetime.utcnow().isoformat(),
                    "features": {"V1": 0.2, "V2": 0.5, "V3": -0.1}
                },
                {
                    "transaction_id": "demo_tx_002",
                    "amount": 8500.00,
                    "timestamp": datetime.utcnow().isoformat(),
                    "features": {"V1": 3.2, "V2": -2.8, "V3": 4.1}
                }
            ]
            
            for transaction in sample_transactions:
                if not self.running:
                    break
                
                logger.info(f"🔍 Processing transaction: {transaction['transaction_id']}")
                
                # Step 1: Monitor and flag transaction
                monitor_result = await self.agents['monitor'].process_transaction(transaction)
                logger.info(f"Monitor result: Flagged={monitor_result.get('flagged', False)}")
                
                # Step 2: Analyze if flagged
                if monitor_result.get('flagged', False):
                    # Use hybrid analysis for flagged transactions
                    analysis_result = await self.agents['hybrid'].analyze_transaction(transaction)
                    logger.info(f"Hybrid analysis: Risk={analysis_result.get('risk_score', 0):.3f}")
                    
                    # Step 3: Generate alerts for high-risk transactions
                    risk_score = analysis_result.get('risk_score', 0)
                    if risk_score >= 0.8:
                        # Create alert event for the alert agent
                        alert_data = {
                            "alert_id": analysis_result.get("alert_id"),
                            "transaction_id": analysis_result.get("transaction_id"),
                            "risk_score": analysis_result.get("risk_score"),
                            "priority": "HIGH",
                            "analysis_summary": analysis_result.get("analysis_summary"),
                            "recommendations": analysis_result.get("recommendations", []),
                            "fraud_indicators": analysis_result.get("fraud_indicators", []),
                            "amount": transaction["amount"],
                            "alert_timestamp": datetime.utcnow().isoformat()
                        }
                        
                        # Process through alert agent
                        await self.agents['alert'].process_alert(alert_data)
                
                # Small delay between transactions
                await asyncio.sleep(2)
            
            # Keep system running
            logger.info("📊 Demo transactions processed. System running in monitoring mode...")
            
            while self.running:
                # System health check
                system_stats = await self._get_system_stats()
                logger.info(f"📈 System stats: {system_stats}")
                
                # Wait before next health check
                await asyncio.sleep(30)
                
        except asyncio.CancelledError:
            logger.info("🛑 Main loop cancelled")
        except Exception as e:
            logger.error(f"❌ Error in main loop: {str(e)}")
            raise
    
    async def _get_system_stats(self) -> Dict[str, any]:
        """Get system-wide statistics."""
        try:
            stats = {
                "timestamp": datetime.utcnow().isoformat(),
                "system_status": "running" if self.running else "stopped",
                "agents_active": len(self.agents),
                "monitor_stats": self.agents['monitor'].get_statistics(),
                "analysis_stats": self.agents['analysis'].get_statistics(),
                "hybrid_stats": self.agents['hybrid'].get_statistics()
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {"error": str(e)}
    
    async def system_status(self) -> Dict[str, any]:
        """Get complete system status for health service."""
        try:
            agents_info = {}
            for agent_name, agent in self.agents.items():
                agents_info[agent_name] = {
                    "type": type(agent).__name__,
                    "healthy": self._agent_health.get(agent_name, False),
                    "status": "running" if self._agent_health.get(agent_name, False) else "failed"
                }
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "environment": settings.ENVIRONMENT,
                "project_id": settings.PROJECT_ID,
                "agents": agents_info,
                "system_health": "healthy" if all(self._agent_health.values()) else "degraded"
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "environment": "unknown",
                "project_id": "unknown",
                "agents": {},
                "system_health": "error"
            }
    
    async def shutdown_system(self):
        """Gracefully shutdown the fraud detection system."""
        try:
            logger.info("🛑 Shutting down Fraud Detection System...")
            self.running = False
            
            # Stop monitoring
            if 'monitor' in self.agents:
                await self.agents['monitor'].stop_monitoring()
                logger.info("✅ Monitoring stopped")
            
            # Stop services
            if hasattr(self, 'api_server') and self.api_server:
                self.api_server.should_exit = True
                logger.info("✅ API service stopped")
            
            if hasattr(self, 'health_server') and self.health_server:
                self.health_server.should_exit = True
                logger.info("✅ Health service stopped")
            
            # Final statistics
            final_stats = await self._get_system_stats()
            logger.info(f"📊 Final system statistics: {json.dumps(final_stats, indent=2)}")
            
            logger.info("✅ Fraud Detection System shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {str(e)}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"🔔 Received signal {signum}, initiating shutdown...")
        self.running = False

async def main():
    """Main function to run the fraud detection system."""
    try:
        # Create and start the orchestrator
        orchestrator = FraudDetectionOrchestrator()
        await orchestrator.start_system()
        
    except KeyboardInterrupt:
        logger.info("🔔 Received keyboard interrupt")
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        sys.exit(1)
    finally:
        if 'orchestrator' in locals():
            await orchestrator.shutdown_system()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Goodbye!")
    except Exception as e:
        logger.error(f"💥 System crashed: {str(e)}")
        sys.exit(1)