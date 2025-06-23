import json
import logging
import asyncio
from typing import Dict, Any, List
import os

# ADK imports
from google.adk.agents import Agent
from google.cloud import pubsub_v1

# Configure logging
logger = logging.getLogger(__name__)

# ML imports for local fraud detection
try:
    import numpy as np
    from tensorflow import keras
    ML_AVAILABLE = True
except ImportError:
    logger.warning("TensorFlow not available. Please install: pip install tensorflow")
    np = None
    keras = None
    ML_AVAILABLE = False

def monitor_transaction_stream(project_id: str, subscription_name: str = "transactions-sub") -> Dict[str, Any]:
    """
    Monitor incoming transaction stream from Pub/Sub.
    
    Args:
        project_id: Google Cloud project ID
        subscription_name: Pub/Sub subscription name
        
    Returns:
        Status of monitoring operation
    """
    try:
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(project_id, subscription_name)
        
        # Check if subscription exists
        try:
            subscriber.get_subscription(subscription=subscription_path)
            logger.info(f"✅ Subscription {subscription_name} is available")
            return {
                "status": "monitoring_active",
                "subscription_path": subscription_path,
                "project_id": project_id,
                "message": "Transaction monitoring is active"
            }
        except Exception as e:
            logger.warning(f"Subscription {subscription_name} not available: {e}")
            return {
                "status": "subscription_unavailable",
                "subscription_path": subscription_path,
                "project_id": project_id,
                "error": str(e),
                "message": "Subscription not available, using demo mode"
            }
            
    except Exception as e:
        logger.error(f"Error setting up transaction monitoring: {e}")
        return {
            "status": "monitoring_error",
            "error": str(e),
            "message": "Failed to initialize transaction monitoring"
        }

def flag_suspicious_transaction(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flag a transaction as suspicious based on initial screening.
    
    Args:
        transaction_data: Transaction data to evaluate
        
    Returns:
        Flagging result with risk indicators
    """
    try:
        amount = transaction_data.get("amount", 0)
        timestamp = transaction_data.get("timestamp", "")
        features = transaction_data.get("features", {})
        
        # Simple rule-based flagging
        risk_flags = []
        risk_score = 0.0
        
        # High amount flag
        if amount > 10000:
            risk_flags.append("High transaction amount")
            risk_score += 0.3
        elif amount > 5000:
            risk_flags.append("Elevated transaction amount")
            risk_score += 0.2
        
        # Time-based flags (simplified)
        if "night" in timestamp.lower() or any(hour in timestamp for hour in ["23:", "00:", "01:", "02:", "03:"]):
            risk_flags.append("Off-hours transaction")
            risk_score += 0.1
        
        # Feature-based flags (if available)
        if features:
            # Check for extreme feature values (simplified)
            extreme_features = 0
            for key, value in features.items():
                if isinstance(value, (int, float)) and abs(value) > 3:
                    extreme_features += 1
            
            if extreme_features > 5:
                risk_flags.append("Multiple extreme feature values")
                risk_score += 0.4
            elif extreme_features > 2:
                risk_flags.append("Some extreme feature values")
                risk_score += 0.2
        
        # ML-based flagging if available
        if ML_AVAILABLE:
            try:
                model_path = os.path.join(os.path.dirname(__file__), "..", "models", "fraud_detection_model.keras")
                if os.path.exists(model_path):
                    model = keras.models.load_model(model_path)
                    
                    # Prepare features for ML model
                    feature_vector = []
                    for i in range(1, 29):
                        feature_vector.append(features.get(f'V{i}', 0.0))
                    feature_vector.append(amount / 1000.0)  # Scaled amount
                    
                    # Ensure correct feature count
                    while len(feature_vector) < 29:
                        feature_vector.append(0.0)
                    
                    # Get ML prediction
                    feature_array = np.array([feature_vector])
                    ml_risk = float(model.predict(feature_array, verbose=0)[0][0])
                    
                    if ml_risk > 0.7:
                        risk_flags.append("ML model high risk prediction")
                        risk_score = max(risk_score, ml_risk)
                    elif ml_risk > 0.5:
                        risk_flags.append("ML model moderate risk prediction")
                        risk_score = max(risk_score, ml_risk * 0.8)
                        
            except Exception as e:
                logger.warning(f"ML flagging failed: {e}")
        
        # Determine if transaction should be flagged
        should_flag = risk_score >= 0.3 or len(risk_flags) >= 2
        
        return {
            "transaction_id": transaction_data.get("transaction_id", "unknown"),
            "flagged": should_flag,
            "risk_score": risk_score,
            "risk_flags": risk_flags,
            "flagging_method": "rule_based_ml" if ML_AVAILABLE else "rule_based",
            "amount": amount,
            "timestamp": timestamp,
            "recommendation": "Send for AI analysis" if should_flag else "Standard processing"
        }
        
    except Exception as e:
        logger.error(f"Error flagging transaction: {e}")
        return {
            "transaction_id": transaction_data.get("transaction_id", "unknown"),
            "flagged": True,  # Flag on error for safety
            "risk_score": 0.8,
            "risk_flags": [f"Flagging error: {str(e)}"],
            "flagging_method": "error_fallback",
            "error": str(e),
            "recommendation": "Manual review required"
        }

class MonitoringAgent:
    """
    Transaction monitoring agent for real-time fraud detection.
    
    This agent monitors incoming transaction streams and performs initial
    fraud screening to flag suspicious transactions for further analysis.
    """
    
    def __init__(self):
        """Initialize the MonitoringAgent."""
        # Create the ADK agent
        self.agent = Agent(
            name="fraud_monitoring_agent",
            model="gemini-2.5-pro-preview-05-06",
            instruction="""You are a fraud monitoring system responsible for real-time
            transaction surveillance. Your role is to:
            
            1. Monitor incoming transaction streams continuously
            2. Perform initial fraud screening using rules and ML models
            3. Flag suspicious transactions for detailed analysis
            4. Track monitoring statistics and performance metrics
            5. Ensure high availability and fault tolerance
            
            Always prioritize catching potential fraud while minimizing false positives.
            Focus on efficient processing and accurate initial screening.""",
            description="Real-time transaction monitoring for fraud detection",
        )
        
        # Initialize Pub/Sub components
        self._subscriber = pubsub_v1.SubscriberClient()
        self._publisher = pubsub_v1.PublisherClient()
        
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "fraud-detection-adkhackathon")
        self._project_id = project_id
        self._subscription_path = self._subscriber.subscription_path(project_id, "transactions-sub")
        self._flagged_topic_path = self._publisher.topic_path(project_id, "flagged-transactions")
        
        # Statistics
        self._processed_count = 0
        self._flagged_count = 0
        self._monitoring_active = False
        
        logger.info(f"MonitoringAgent initialized for project: {project_id}")
    
    async def start_monitoring(self) -> Dict[str, Any]:
        """
        Start transaction monitoring.
        
        Returns:
            Status of monitoring startup
        """
        try:
            # Check monitoring capabilities
            monitor_status = monitor_transaction_stream(self._project_id)
            
            self._monitoring_active = monitor_status.get("status") == "monitoring_active"
            
            if self._monitoring_active:
                logger.info("🔍 Transaction monitoring started successfully")
                return {
                    "status": "started",
                    "message": "Real-time transaction monitoring is active",
                    "subscription_path": self._subscription_path
                }
            else:
                logger.warning("⚠️ Monitoring started in demo mode")
                return {
                    "status": "demo_mode",
                    "message": "Monitoring started in demonstration mode",
                    "reason": monitor_status.get("message", "Subscription unavailable")
                }
                
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to start transaction monitoring"
            }
    
    async def process_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single transaction for fraud screening.
        
        Args:
            transaction_data: Transaction data to process
            
        Returns:
            Processing result with flagging information
        """
        try:
            self._processed_count += 1
            
            # Flag transaction if suspicious
            flagging_result = flag_suspicious_transaction(transaction_data)
            
            # Track flagged transactions
            if flagging_result.get("flagged", False):
                self._flagged_count += 1
                await self._publish_flagged_transaction(flagging_result)
            
            logger.info(f"Processed transaction {flagging_result['transaction_id']} - "
                       f"Flagged: {flagging_result['flagged']}, Risk: {flagging_result['risk_score']:.3f}")
            
            return flagging_result
            
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            return {
                "transaction_id": transaction_data.get("transaction_id", "unknown"),
                "flagged": True,
                "error": str(e),
                "risk_score": 0.8,
                "risk_flags": ["Processing error"],
                "recommendation": "Manual review required"
            }
    
    async def process_batch(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple transactions in batch.
        
        Args:
            transactions: List of transaction data to process
            
        Returns:
            List of processing results
        """
        results = []
        batch_size = 20  # Large batch size for monitoring
        
        for i in range(0, len(transactions), batch_size):
            batch = transactions[i:i + batch_size]
            
            # Process batch concurrently
            tasks = []
            for transaction in batch:
                task = self.process_transaction(transaction)
                tasks.append(task)
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error: {result}")
                    results.append({
                        "flagged": True,
                        "error": str(result),
                        "risk_score": 0.8
                    })
                else:
                    results.append(result)
            
            # Small delay between batches
            await asyncio.sleep(0.01)
        
        logger.info(f"Batch monitoring completed: {len(results)} transactions processed")
        return results
    
    async def _publish_flagged_transaction(self, flagging_result: Dict[str, Any]) -> None:
        """
        Publish flagged transaction to analysis pipeline.
        
        Args:
            flagging_result: Flagged transaction data
        """
        try:
            flagged_data = {
                "flag_type": "SUSPICIOUS_TRANSACTION",
                "transaction_id": flagging_result["transaction_id"],
                "risk_score": flagging_result["risk_score"],
                "risk_flags": flagging_result["risk_flags"],
                "flagging_method": flagging_result["flagging_method"],
                "amount": flagging_result["amount"],
                "timestamp": flagging_result["timestamp"],
                "recommendation": flagging_result["recommendation"]
            }
            
            message_data = json.dumps(flagged_data).encode('utf-8')
            self._publisher.publish(self._flagged_topic_path, data=message_data)
            
            logger.info(f"🚩 Published flagged transaction {flagging_result['transaction_id']}")
            
        except Exception as e:
            logger.error(f"Error publishing flagged transaction: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            "processed_transactions": self._processed_count,
            "flagged_transactions": self._flagged_count,
            "flagging_rate": (self._flagged_count / self._processed_count * 100) if self._processed_count > 0 else 0,
            "monitoring_active": self._monitoring_active
        }
    
    async def stop_monitoring(self) -> Dict[str, Any]:
        """Stop transaction monitoring."""
        self._monitoring_active = False
        logger.info("🛑 Transaction monitoring stopped")
        return {
            "status": "stopped",
            "final_stats": self.get_statistics()
        }

def main():
    """Main function for running the monitoring agent."""
    async def run_monitoring():
        agent = MonitoringAgent()
        
        # Start monitoring
        start_result = await agent.start_monitoring()
        logger.info(f"Monitoring startup: {start_result}")
        
        # Example transaction processing
        sample_transactions = [
            {
                "transaction_id": "tx_normal_001",
                "amount": 100.00,
                "timestamp": "2024-01-15T14:30:00Z",
                "features": {"V1": 0.5, "V2": 0.3}
            },
            {
                "transaction_id": "tx_suspicious_001",
                "amount": 15000.00,
                "timestamp": "2024-01-15T02:45:00Z",
                "features": {"V1": 4.2, "V2": -3.8, "V3": 5.1}
            }
        ]
        
        # Process transactions
        for transaction in sample_transactions:
            result = await agent.process_transaction(transaction)
            logger.info(f"Transaction result: {json.dumps(result, indent=2)}")
        
        # Print statistics
        stats = agent.get_statistics()
        logger.info(f"Monitoring statistics: {stats}")
        
        # Stop monitoring
        stop_result = await agent.stop_monitoring()
        logger.info(f"Monitoring stopped: {stop_result}")
    
    try:
        logger.info("Starting fraud monitoring agent...")
        asyncio.run(run_monitoring())
    except KeyboardInterrupt:
        logger.info("Shutting down monitoring agent...")
    except Exception as e:
        logger.error(f"Error running monitoring agent: {str(e)}")
        raise

if __name__ == "__main__":
    main()