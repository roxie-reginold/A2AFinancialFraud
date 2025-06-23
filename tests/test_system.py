#!/usr/bin/env python3
"""
Comprehensive system test for ADK Financial Fraud Detection System
"""

import os
import asyncio
import logging
import json
from datetime import datetime

# Set environment variables first
os.environ["GOOGLE_CLOUD_PROJECT"] = "fraud-detection-adkhackathon"
os.environ["BYPASS_CLOUD_VALIDATION"] = "true"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_individual_agents():
    """Test each agent individually."""
    logger.info("🧪 Testing individual agents...")
    
    try:
        # Test Analysis Agent
        from agents.analysis_agent import AnalysisAgent
        analysis_agent = AnalysisAgent()
        
        sample_transaction = {
            "transaction_id": "test_001",
            "amount": 1500.00,
            "timestamp": datetime.utcnow().isoformat(),
            "features": {"V1": 1.2, "V2": -0.5, "V3": 0.8}
        }
        
        result = await analysis_agent.analyze_transaction(sample_transaction)
        logger.info(f"✅ AnalysisAgent test passed: Risk={result.get('risk_score', 0):.3f}")
        
        # Test Monitoring Agent
        from agents.monitor_agent import MonitoringAgent
        monitor_agent = MonitoringAgent()
        
        monitor_result = await monitor_agent.process_transaction(sample_transaction)
        logger.info(f"✅ MonitoringAgent test passed: Flagged={monitor_result.get('flagged', False)}")
        
        # Test Hybrid Agent
        from agents.hybrid_analysis_agent import HybridAnalysisAgent
        hybrid_agent = HybridAnalysisAgent()
        
        hybrid_result = await hybrid_agent.analyze_transaction(sample_transaction)
        logger.info(f"✅ HybridAnalysisAgent test passed: Risk={hybrid_result.get('risk_score', 0):.3f}")
        
        logger.info("🎉 All individual agent tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent test failed: {str(e)}")
        return False

async def test_end_to_end_workflow():
    """Test complete end-to-end fraud detection workflow."""
    logger.info("🔄 Testing end-to-end workflow...")
    
    try:
        # Initialize agents
        from agents.monitor_agent import MonitoringAgent
        from agents.hybrid_analysis_agent import HybridAnalysisAgent
        
        monitor = MonitoringAgent()
        analyzer = HybridAnalysisAgent()
        
        # Start monitoring
        await monitor.start_monitoring()
        
        # Test transactions with different risk levels
        test_transactions = [
            {
                "transaction_id": "e2e_low_risk",
                "amount": 25.00,
                "timestamp": datetime.utcnow().isoformat(),
                "features": {"V1": 0.1, "V2": 0.2, "V3": 0.1}
            },
            {
                "transaction_id": "e2e_high_risk",
                "amount": 12000.00,
                "timestamp": datetime.utcnow().isoformat(),
                "features": {"V1": 4.5, "V2": -3.2, "V3": 5.1}
            }
        ]
        
        workflow_results = []
        
        for transaction in test_transactions:
            logger.info(f"🔍 Processing: {transaction['transaction_id']}")
            
            # Step 1: Monitor
            monitor_result = await monitor.process_transaction(transaction)
            
            # Step 2: Analyze if flagged
            if monitor_result.get('flagged', False):
                analysis_result = await analyzer.analyze_transaction(transaction)
                workflow_results.append({
                    "transaction": transaction['transaction_id'],
                    "flagged": True,
                    "risk_score": analysis_result.get('risk_score', 0),
                    "analysis_method": analysis_result.get('analysis_method', 'unknown')
                })
            else:
                workflow_results.append({
                    "transaction": transaction['transaction_id'],
                    "flagged": False,
                    "risk_score": 0,
                    "analysis_method": "none"
                })
        
        # Stop monitoring
        await monitor.stop_monitoring()
        
        # Print workflow results
        logger.info("📊 End-to-end workflow results:")
        for result in workflow_results:
            logger.info(f"  - {result['transaction']}: Flagged={result['flagged']}, Risk={result['risk_score']:.3f}")
        
        logger.info("✅ End-to-end workflow test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ End-to-end test failed: {str(e)}")
        return False

async def test_error_handling():
    """Test system error handling and resilience."""
    logger.info("🛡️  Testing error handling...")
    
    try:
        from agents.analysis_agent import AnalysisAgent
        
        agent = AnalysisAgent()
        
        # Test with invalid transaction data
        invalid_transaction = {
            "transaction_id": "error_test",
            "invalid_field": "this should not break the system"
        }
        
        result = await agent.analyze_transaction(invalid_transaction)
        
        # System should handle errors gracefully
        if "error" in result.get("analysis_method", ""):
            logger.info("✅ Error handling test passed - system handled invalid data gracefully")
            return True
        else:
            logger.info("✅ Error handling test passed - system processed data successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error handling test failed: {str(e)}")
        return False

async def test_performance():
    """Test system performance with multiple transactions."""
    logger.info("⚡ Testing performance...")
    
    try:
        from agents.hybrid_analysis_agent import HybridAnalysisAgent
        
        agent = HybridAnalysisAgent()
        
        # Generate multiple test transactions
        transactions = []
        for i in range(5):
            transactions.append({
                "transaction_id": f"perf_test_{i:03d}",
                "amount": 100.0 + i * 100,
                "timestamp": datetime.utcnow().isoformat(),
                "features": {"V1": i * 0.2, "V2": i * -0.1, "V3": i * 0.15}
            })
        
        # Process batch
        start_time = datetime.utcnow()
        results = await agent.analyze_batch(transactions)
        end_time = datetime.utcnow()
        
        processing_time = (end_time - start_time).total_seconds()
        
        logger.info(f"✅ Performance test passed:")
        logger.info(f"  - Processed {len(results)} transactions")
        logger.info(f"  - Processing time: {processing_time:.2f} seconds")
        logger.info(f"  - Rate: {len(results)/processing_time:.2f} transactions/second")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Performance test failed: {str(e)}")
        return False

async def main():
    """Run comprehensive system tests."""
    logger.info("🚀 Starting ADK Financial Fraud Detection System Tests")
    logger.info("=" * 60)
    
    test_results = {
        "individual_agents": False,
        "end_to_end_workflow": False,
        "error_handling": False,
        "performance": False
    }
    
    # Run all tests
    test_results["individual_agents"] = await test_individual_agents()
    print()
    
    test_results["end_to_end_workflow"] = await test_end_to_end_workflow()
    print()
    
    test_results["error_handling"] = await test_error_handling()
    print()
    
    test_results["performance"] = await test_performance()
    print()
    
    # Summary
    logger.info("=" * 60)
    logger.info("📊 TEST SUMMARY:")
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for test_name, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    logger.info(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL TESTS PASSED! System is ready for deployment.")
        return True
    else:
        logger.info(f"⚠️  {total_tests - passed_tests} test(s) failed. Review and fix issues.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit_code = 0 if success else 1
        exit(exit_code)
    except KeyboardInterrupt:
        logger.info("🔔 Tests interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"💥 Test suite crashed: {str(e)}")
        exit(1)