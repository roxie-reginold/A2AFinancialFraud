#!/usr/bin/env python3
"""
ADK Financial Fraud Detection System - Demo Version

Simplified demo that showcases the core fraud detection workflow.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any

# Import our agents
from agents.analysis_agent import AnalysisAgent
from agents.hybrid_analysis_agent import HybridAnalysisAgent
from agents.monitor_agent import MonitoringAgent
from agents.alert_agent import AlertAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_fraud_detection_system():
    """Demonstrate the complete fraud detection workflow."""
    
    logger.info("🚀 Starting ADK Financial Fraud Detection Demo")
    logger.info("=" * 60)
    
    try:
        # Initialize all agents
        logger.info("📋 Initializing agents...")
        monitor = MonitoringAgent()
        analyzer = AnalysisAgent()
        hybrid = HybridAnalysisAgent()
        alert_agent = AlertAgent()
        
        logger.info("✅ All agents initialized successfully!")
        
        # Demo transactions with different risk profiles
        demo_transactions = [
            {
                "transaction_id": "demo_low_001",
                "amount": 25.00,
                "timestamp": datetime.utcnow().isoformat(),
                "customer_id": "customer_001",
                "features": {"V1": 0.1, "V2": 0.2, "V3": 0.1}
            },
            {
                "transaction_id": "demo_medium_002",
                "amount": 1500.00,
                "timestamp": datetime.utcnow().isoformat(),
                "customer_id": "customer_002",
                "features": {"V1": 1.2, "V2": -0.8, "V3": 0.9}
            },
            {
                "transaction_id": "demo_high_003",
                "amount": 8500.00,
                "timestamp": datetime.utcnow().isoformat(),
                "customer_id": "customer_003",
                "features": {"V1": 3.2, "V2": -2.5, "V3": 4.1}
            }
        ]
        
        logger.info("\n🔄 Starting fraud detection workflow...")
        logger.info("-" * 40)
        
        for i, transaction in enumerate(demo_transactions, 1):
            logger.info(f"\n📍 Processing Transaction {i}/3: {transaction['transaction_id']}")
            logger.info(f"   Amount: ${transaction['amount']:,.2f}")
            logger.info(f"   Customer: {transaction['customer_id']}")
            
            # Step 1: Initial monitoring and flagging
            logger.info("🔍 Step 1: Transaction Monitoring...")
            monitor_result = await monitor.process_transaction(transaction)
            flagged = monitor_result.get('flagged', False)
            logger.info(f"   Result: {'🚩 FLAGGED' if flagged else '✅ PASSED'}")
            
            if flagged:
                # Step 2: Advanced analysis for flagged transactions
                logger.info("🧠 Step 2: AI/ML Analysis...")
                analysis_result = await hybrid.analyze_transaction(transaction)
                risk_score = analysis_result.get('risk_score', 0)
                method = analysis_result.get('analysis_method', 'unknown')
                logger.info(f"   Risk Score: {risk_score:.3f}")
                logger.info(f"   Method: {method}")
                
                # Step 3: Generate alerts for high-risk transactions
                if risk_score >= 0.8:
                    logger.info("🚨 Step 3: High-Risk Alert Generation...")
                    alert_data = {
                        **analysis_result,
                        "priority": "HIGH",
                        "customer_id": transaction["customer_id"],
                        "alert_timestamp": datetime.utcnow().isoformat()
                    }
                    
                    alert_result = await alert_agent.process_alert(alert_data)
                    logger.info(f"   Alert ID: {alert_result['alert_id']}")
                    logger.info(f"   Severity: {alert_result['severity']}")
                elif risk_score >= 0.5:
                    logger.info("⚠️  Step 3: Medium-Risk Alert...")
                    alert_data = {
                        **analysis_result,
                        "priority": "MEDIUM",
                        "customer_id": transaction["customer_id"],
                        "alert_timestamp": datetime.utcnow().isoformat()
                    }
                    alert_result = await alert_agent.process_alert(alert_data)
                    logger.info(f"   Alert ID: {alert_result['alert_id']}")
                else:
                    logger.info("ℹ️  Step 3: Low-risk, routine processing")
            else:
                logger.info("✅ Transaction passed initial screening - no further analysis needed")
            
            # Brief pause between transactions
            await asyncio.sleep(1)
        
        # Display system statistics
        logger.info("\n" + "=" * 60)
        logger.info("📊 SYSTEM STATISTICS")
        logger.info("=" * 60)
        
        monitor_stats = monitor.get_statistics()
        logger.info(f"🔍 Monitor Stats:")
        logger.info(f"   Total processed: {monitor_stats['processed_transactions']}")
        logger.info(f"   Flagged: {monitor_stats['flagged_transactions']}")
        logger.info(f"   Flag rate: {monitor_stats['flagging_rate']:.1f}%")
        
        analysis_stats = analyzer.get_statistics()
        logger.info(f"🧠 Analysis Stats:")
        logger.info(f"   Total analyzed: {analysis_stats['total_analyzed']}")
        logger.info(f"   High-risk found: {analysis_stats['high_risk_found']}")
        logger.info(f"   High-risk rate: {analysis_stats['high_risk_percentage']:.1f}%")
        
        hybrid_stats = hybrid.get_statistics()
        logger.info(f"🔄 Hybrid Stats:")
        logger.info(f"   Total analyzed: {hybrid_stats['total_analyzed']}")
        logger.info(f"   AI analyzed: {hybrid_stats['ai_analyzed']}")
        logger.info(f"   ML analyzed: {hybrid_stats['ml_analyzed']}")
        logger.info(f"   AI usage: {hybrid_stats['ai_usage_percentage']:.1f}%")
        
        alert_stats = alert_agent.get_statistics()
        logger.info(f"🚨 Alert Stats:")
        logger.info(f"   Total alerts: {alert_stats['total_alerts_processed']}")
        logger.info(f"   High priority: {alert_stats['high_risk_alerts']}")
        logger.info(f"   Medium priority: {alert_stats['medium_risk_alerts']}")
        logger.info(f"   Low priority: {alert_stats['low_risk_alerts']}")
        
        logger.info("\n🎉 Fraud Detection Demo Completed Successfully!")
        logger.info("   The system successfully demonstrated:")
        logger.info("   ✅ Real-time transaction monitoring")
        logger.info("   ✅ AI-powered fraud analysis")
        logger.info("   ✅ Hybrid ML/AI routing")
        logger.info("   ✅ Multi-level alert generation")
        logger.info("   ✅ Comprehensive system statistics")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}")
        return False

async def main():
    """Main demo function."""
    success = await demo_fraud_detection_system()
    
    if success:
        logger.info("\n🌟 Demo completed successfully! The ADK Financial Fraud Detection System is operational.")
    else:
        logger.error("\n💥 Demo failed. Please check the logs for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n🛑 Demo interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"\n💥 Demo crashed: {str(e)}")
        exit(1)