#!/usr/bin/env python3
"""
ADK Financial Fraud Detection System - High-Risk Demo

Demo with transactions designed to trigger the full analysis workflow.
"""

import asyncio
import logging
from datetime import datetime

from agents.analysis_agent import AnalysisAgent
from agents.hybrid_analysis_agent import HybridAnalysisAgent
from agents.monitor_agent import MonitoringAgent
from agents.alert_agent import AlertAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def demo_high_risk_transactions():
    """Demo with high-risk transactions that will trigger analysis."""
    
    logger.info("🚨 High-Risk Fraud Detection Demo")
    logger.info("=" * 50)
    
    # Initialize agents
    monitor = MonitoringAgent()
    hybrid = HybridAnalysisAgent()
    alert_agent = AlertAgent()
    
    # High-risk transactions designed to trigger flagging
    high_risk_transactions = [
        {
            "transaction_id": "suspicious_001",
            "amount": 15000.00,  # Very high amount
            "timestamp": datetime.utcnow().isoformat(),
            "customer_id": "customer_suspicious_001",
            "features": {"V1": 5.2, "V2": -4.8, "V3": 6.1, "V4": -3.5}  # Extreme values
        },
        {
            "transaction_id": "suspicious_002", 
            "amount": 25000.00,  # Extremely high amount
            "timestamp": datetime.utcnow().isoformat(),
            "customer_id": "customer_suspicious_002",
            "features": {"V1": 4.1, "V2": -5.2, "V3": 3.8, "V4": 4.5}  # Very suspicious patterns
        }
    ]
    
    for i, transaction in enumerate(high_risk_transactions, 1):
        logger.info(f"\n🎯 Processing High-Risk Transaction {i}: {transaction['transaction_id']}")
        logger.info(f"   Amount: ${transaction['amount']:,.2f}")
        
        # Step 1: Monitor (should flag these)
        monitor_result = await monitor.process_transaction(transaction)
        flagged = monitor_result.get('flagged', False)
        logger.info(f"🔍 Monitoring: {'🚩 FLAGGED' if flagged else '✅ PASSED'}")
        
        if flagged:
            # Step 2: Hybrid analysis
            logger.info("🧠 Running AI/ML analysis...")
            analysis_result = await hybrid.analyze_transaction(transaction)
            risk_score = analysis_result.get('risk_score', 0)
            method = analysis_result.get('analysis_method', 'unknown')
            logger.info(f"   Risk Score: {risk_score:.3f}")
            logger.info(f"   Method: {method}")
            
            # Step 3: Generate alert
            logger.info("🚨 Generating alert...")
            alert_data = {
                **analysis_result,
                "customer_id": transaction["customer_id"],
                "alert_timestamp": datetime.utcnow().isoformat()
            }
            
            alert_result = await alert_agent.process_alert(alert_data)
            logger.info(f"   Alert: {alert_result['severity']} - {alert_result['alert_id']}")
        else:
            # Force analysis anyway for demo
            logger.info("🧠 Forcing analysis for demo...")
            analysis_result = await hybrid.analyze_transaction(transaction)
            risk_score = analysis_result.get('risk_score', 0)
            logger.info(f"   Risk Score: {risk_score:.3f}")
            
            if risk_score >= 0.5:
                alert_data = {
                    **analysis_result,
                    "customer_id": transaction["customer_id"],
                    "alert_timestamp": datetime.utcnow().isoformat()
                }
                alert_result = await alert_agent.process_alert(alert_data)
                logger.info(f"🚨 Alert: {alert_result['severity']} - {alert_result['alert_id']}")
    
    # Show final statistics
    logger.info("\n" + "=" * 50)
    logger.info("📊 FINAL STATISTICS")
    
    monitor_stats = monitor.get_statistics()
    logger.info(f"🔍 Monitor: {monitor_stats['flagged_transactions']}/{monitor_stats['processed_transactions']} flagged")
    
    hybrid_stats = hybrid.get_statistics()
    logger.info(f"🧠 Analysis: {hybrid_stats['total_analyzed']} analyzed, {hybrid_stats['ai_usage_percentage']:.1f}% AI usage")
    
    alert_stats = alert_agent.get_statistics()
    logger.info(f"🚨 Alerts: {alert_stats['total_alerts_processed']} total, {alert_stats['high_risk_alerts']} high-risk")
    
    logger.info("\n🎉 High-risk demo completed!")

if __name__ == "__main__":
    asyncio.run(demo_high_risk_transactions())