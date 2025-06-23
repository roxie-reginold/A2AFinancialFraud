import json
import logging
import asyncio
from typing import Dict, Any, List
import os

# ADK imports
from google.adk.agents import Agent
from google.cloud import pubsub_v1

# Import the analysis agent tool (will implement locally for now)
# from .analysis_agent import analyze_transaction_risk

# Configure logging
logger = logging.getLogger(__name__)

# Local ML imports
try:
    import numpy as np
    from tensorflow import keras
    LOCAL_ML_AVAILABLE = True
except ImportError:
    logger.warning("TensorFlow not available. Please install: pip install tensorflow")
    np = None
    keras = None
    LOCAL_ML_AVAILABLE = False

def analyze_transaction_risk(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a transaction for fraud risk using Gemini AI.
    
    Args:
        transaction_data: Dictionary containing transaction details
        
    Returns:
        Analysis result with risk score and recommendations
    """
    try:
        # Initialize Vertex AI if available
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel, GenerationConfig
            
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "fraud-detection-adkhackathon")
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-pro-preview-05-06")
            
            # Initialize Vertex AI
            vertexai.init(project=project_id, location="us-central1")
            
            # Create Gemini model
            model = GenerativeModel(model_name)
            
            # Create analysis prompt
            prompt = f"""
            Analyze this financial transaction for fraud indicators:
            
            Transaction Details:
            - Amount: ${transaction_data.get('amount', 0):.2f}
            - Time: {transaction_data.get('timestamp', 'unknown')}
            - Features: {json.dumps(transaction_data.get('features', {}), indent=2)}
            
            Provide a structured fraud analysis with:
            1. Risk score (0.0 = safe, 1.0 = definitely fraud)
            2. Key fraud indicators found
            3. Specific recommendations
            4. Brief summary
            
            Format as JSON with keys: risk_score, fraud_indicators, recommendations, analysis_summary
            """
            
            # Generate analysis
            response = model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=1000
                )
            )
            
            # Parse response
            try:
                analysis = json.loads(response.text)
                analysis["analysis_method"] = "gemini_ai"
                analysis["model_used"] = model_name
                return analysis
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "risk_score": 0.7,
                    "analysis_method": "gemini_ai_fallback",
                    "fraud_indicators": ["AI analysis completed but format error"],
                    "recommendations": ["Manual review recommended"],
                    "analysis_summary": response.text[:200] + "..." if len(response.text) > 200 else response.text,
                    "model_used": model_name
                }
                
        except ImportError:
            logger.warning("Vertex AI not available. Using fallback analysis.")
            return {
                "risk_score": 0.5,
                "analysis_method": "fallback",
                "fraud_indicators": ["Vertex AI not available"],
                "recommendations": ["Install google-cloud-aiplatform"],
                "analysis_summary": "Fallback analysis - Vertex AI unavailable"
            }
            
    except Exception as e:
        logger.error(f"Error in Gemini analysis: {str(e)}")
        return {
            "risk_score": 0.6,
            "analysis_method": "error_fallback",
            "fraud_indicators": [f"Analysis error: {str(e)}"],
            "recommendations": ["Manual review required due to analysis error"],
            "analysis_summary": f"Analysis failed: {str(e)}",
            "error": str(e)
        }

def analyze_transaction_local(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a transaction using local ML model.
    
    Args:
        transaction_data: Dictionary containing transaction details
        
    Returns:
        Analysis result with risk score and recommendations
    """
    try:
        if not LOCAL_ML_AVAILABLE:
            return {
                "risk_score": 0.5,
                "analysis_method": "fallback",
                "fraud_indicators": ["Local ML not available"],
                "recommendations": ["Install tensorflow"],
                "analysis_summary": "Fallback analysis - TensorFlow unavailable"
            }
        
        # Load the local model
        model_path = os.path.join(os.path.dirname(__file__), "..", "models", "fraud_detection_model.keras")
        
        if not os.path.exists(model_path):
            return {
                "risk_score": 0.5,
                "analysis_method": "model_missing",
                "fraud_indicators": ["Local model file not found"],
                "recommendations": ["Train and save the local model"],
                "analysis_summary": "Local model not available"
            }
        
        # Load model
        model = keras.models.load_model(model_path)
        
        # Extract features (assuming V1-V28 feature format)
        features = transaction_data.get('features', {})
        feature_vector = []
        
        # Create feature vector from V1-V28
        for i in range(1, 29):
            feature_vector.append(features.get(f'V{i}', 0.0))
        
        # Add amount (scaled)
        amount = transaction_data.get('amount', 0)
        feature_vector.append(amount / 1000.0)  # Simple scaling
        
        # Ensure we have the right number of features
        while len(feature_vector) < 29:
            feature_vector.append(0.0)
        
        # Make prediction
        feature_array = np.array([feature_vector])
        prediction = model.predict(feature_array, verbose=0)[0][0]
        
        # Convert to risk score
        risk_score = float(prediction)
        
        # Generate analysis based on risk score
        if risk_score >= 0.8:
            fraud_indicators = ["High anomaly score", "Pattern matches known fraud cases"]
            recommendations = ["Immediate review required", "Consider blocking transaction"]
        elif risk_score >= 0.5:
            fraud_indicators = ["Moderate anomaly detected", "Some suspicious patterns"]
            recommendations = ["Additional verification recommended", "Monitor account activity"]
        else:
            fraud_indicators = ["Low risk patterns", "Normal transaction behavior"]
            recommendations = ["Transaction appears normal", "Standard processing"]
        
        return {
            "risk_score": risk_score,
            "analysis_method": "local_ml",
            "fraud_indicators": fraud_indicators,
            "recommendations": recommendations,
            "analysis_summary": f"Local ML analysis: {risk_score:.3f} risk score",
            "model_type": "tensorflow_keras"
        }
        
    except Exception as e:
        logger.error(f"Error in local ML analysis: {str(e)}")
        return {
            "risk_score": 0.6,
            "analysis_method": "local_error",
            "fraud_indicators": [f"Local analysis error: {str(e)}"],
            "recommendations": ["Manual review required due to analysis error"],
            "analysis_summary": f"Local analysis failed: {str(e)}",
            "error": str(e)
        }

def hybrid_risk_analysis(transaction_data: Dict[str, Any], use_ai_threshold: float = 0.7) -> Dict[str, Any]:
    """
    Perform hybrid analysis using both AI and local ML based on risk assessment.
    
    Args:
        transaction_data: Transaction data to analyze
        use_ai_threshold: Threshold above which to use AI analysis
        
    Returns:
        Combined analysis result
    """
    try:
        # First, do a quick local analysis
        local_result = analyze_transaction_local(transaction_data)
        local_risk = local_result.get("risk_score", 0.5)
        
        # Determine if we should use AI analysis
        amount = transaction_data.get("amount", 0)
        use_ai = (local_risk >= use_ai_threshold) or (amount >= 5000)
        
        if use_ai:
            # Use AI analysis for high-risk or high-value transactions
            ai_result = analyze_transaction_risk(transaction_data)
            
            # Combine results (weighted average)
            combined_risk = (local_risk * 0.3) + (ai_result.get("risk_score", 0.5) * 0.7)
            
            return {
                "risk_score": combined_risk,
                "analysis_method": "hybrid_ai_ml",
                "fraud_indicators": ai_result.get("fraud_indicators", []) + local_result.get("fraud_indicators", []),
                "recommendations": ai_result.get("recommendations", []),
                "analysis_summary": f"Hybrid analysis: AI({ai_result.get('risk_score', 0):.3f}) + ML({local_risk:.3f}) = {combined_risk:.3f}",
                "local_risk": local_risk,
                "ai_risk": ai_result.get("risk_score", 0),
                "ai_model_used": ai_result.get("model_used", "unknown"),
                "routing_reason": f"High risk ({local_risk:.3f}) or high value (${amount})"
            }
        else:
            # Use only local ML for standard transactions
            local_result["analysis_method"] = "hybrid_ml_only"
            local_result["routing_reason"] = f"Standard risk ({local_risk:.3f}) and value (${amount})"
            return local_result
            
    except Exception as e:
        logger.error(f"Error in hybrid analysis: {str(e)}")
        return {
            "risk_score": 0.6,
            "analysis_method": "hybrid_error",
            "fraud_indicators": [f"Hybrid analysis error: {str(e)}"],
            "recommendations": ["Manual review required due to analysis error"],
            "analysis_summary": f"Hybrid analysis failed: {str(e)}",
            "error": str(e)
        }

class HybridAnalysisAgent:
    """
    Hybrid fraud analysis agent combining AI and local ML.
    
    This agent intelligently routes transactions between AI-powered analysis
    (Gemini) and local ML models based on risk assessment and transaction value.
    """
    
    def __init__(self, ai_threshold: float = 0.7):
        """
        Initialize the HybridAnalysisAgent.
        
        Args:
            ai_threshold: Risk threshold above which to use AI analysis
        """
        self.ai_threshold = ai_threshold
        
        # Create the ADK agent without tools for now (simplified approach)
        self.agent = Agent(
            name="hybrid_fraud_analysis_agent",
            model="gemini-2.5-pro-preview-05-06",
            instruction="""You are a hybrid fraud detection system that intelligently combines
            AI-powered analysis with local machine learning models. Your role is to:
            
            1. Efficiently route transactions to appropriate analysis methods
            2. Use AI analysis for high-risk or complex cases
            3. Use local ML for standard transactions to optimize costs
            4. Provide comprehensive risk assessments combining multiple approaches
            5. Explain your routing decisions and analysis methodology
            
            Always optimize for both accuracy and efficiency, using the most appropriate
            analysis method for each transaction type.""",
            description="Hybrid fraud analysis combining AI and ML for optimal performance"
        )
        
        # Initialize Pub/Sub for communication
        self._publisher = pubsub_v1.PublisherClient()
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "fraud-detection-adkhackathon")
        self._analysis_topic_path = self._publisher.topic_path(project_id, "hybrid-analysis-results")
        
        # Statistics
        self._total_analyzed = 0
        self._ai_analyzed = 0
        self._ml_analyzed = 0
        self._high_risk_found = 0
        
        logger.info(f"HybridAnalysisAgent initialized with AI threshold: {ai_threshold}")
    
    async def analyze_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single transaction using hybrid approach.
        
        Args:
            transaction_data: Transaction data to analyze
            
        Returns:
            Analysis result with risk assessment and routing information
        """
        try:
            self._total_analyzed += 1
            
            # Use the hybrid analysis tool
            analysis_result = hybrid_risk_analysis(transaction_data, self.ai_threshold)
            
            # Track which method was used
            if "ai" in analysis_result.get("analysis_method", ""):
                self._ai_analyzed += 1
            else:
                self._ml_analyzed += 1
            
            # Add metadata
            analysis_result.update({
                "transaction_id": transaction_data.get("transaction_id", f"tx_{self._total_analyzed}"),
                "alert_id": f"hybrid_alert_{self._total_analyzed}",
                "alert_timestamp": transaction_data.get("timestamp", "unknown"),
                "amount": transaction_data.get("amount", 0)
            })
            
            # Track high-risk transactions
            if analysis_result.get("risk_score", 0) >= 0.8:
                self._high_risk_found += 1
                await self._publish_high_risk_alert(analysis_result)
            
            logger.info(f"Hybrid analyzed transaction {analysis_result['transaction_id']} - "
                       f"Risk: {analysis_result['risk_score']:.3f}, Method: {analysis_result['analysis_method']}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in hybrid analysis: {str(e)}")
            return {
                "transaction_id": transaction_data.get("transaction_id", "unknown"),
                "risk_score": 0.5,
                "analysis_method": "hybrid_error",
                "error": str(e),
                "fraud_indicators": ["Hybrid analysis error occurred"],
                "recommendations": ["Manual review required"],
                "analysis_summary": f"Hybrid analysis failed: {str(e)}"
            }
    
    async def analyze_batch(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple transactions using hybrid approach.
        
        Args:
            transactions: List of transaction data to analyze
            
        Returns:
            List of analysis results
        """
        results = []
        batch_size = 10  # Larger batch size for hybrid processing
        
        for i in range(0, len(transactions), batch_size):
            batch = transactions[i:i + batch_size]
            batch_results = []
            
            # Process batch concurrently where possible
            tasks = []
            for transaction in batch:
                task = self.analyze_transaction(transaction)
                tasks.append(task)
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and convert to proper results
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch analysis error: {result}")
                    results.append({
                        "risk_score": 0.5,
                        "analysis_method": "batch_error",
                        "error": str(result)
                    })
                else:
                    results.append(result)
            
            # Small delay between batches
            await asyncio.sleep(0.05)
        
        logger.info(f"Hybrid batch analysis completed: {len(results)} transactions")
        return results
    
    async def _publish_high_risk_alert(self, analysis_result: Dict[str, Any]) -> None:
        """
        Publish high-risk transaction alert to Pub/Sub.
        
        Args:
            analysis_result: Analysis result for high-risk transaction
        """
        try:
            alert_data = {
                "alert_type": "HYBRID_HIGH_RISK_TRANSACTION",
                "alert_id": analysis_result["alert_id"],
                "transaction_id": analysis_result["transaction_id"],
                "risk_score": analysis_result["risk_score"],
                "analysis_method": analysis_result["analysis_method"],
                "fraud_indicators": analysis_result["fraud_indicators"],
                "recommendations": analysis_result["recommendations"],
                "analysis_summary": analysis_result["analysis_summary"],
                "routing_reason": analysis_result.get("routing_reason", "unknown"),
                "timestamp": analysis_result.get("alert_timestamp"),
                "amount": analysis_result.get("amount")
            }
            
            message_data = json.dumps(alert_data).encode('utf-8')
            self._publisher.publish(self._analysis_topic_path, data=message_data)
            
            logger.info(f"🔄 Published hybrid high-risk alert for transaction {analysis_result['transaction_id']}")
            
        except Exception as e:
            logger.error(f"Error publishing hybrid high-risk alert: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get hybrid analysis statistics."""
        return {
            "total_analyzed": self._total_analyzed,
            "ai_analyzed": self._ai_analyzed,
            "ml_analyzed": self._ml_analyzed,
            "high_risk_found": self._high_risk_found,
            "ai_usage_percentage": (self._ai_analyzed / self._total_analyzed * 100) if self._total_analyzed > 0 else 0,
            "ml_usage_percentage": (self._ml_analyzed / self._total_analyzed * 100) if self._total_analyzed > 0 else 0,
            "high_risk_percentage": (self._high_risk_found / self._total_analyzed * 100) if self._total_analyzed > 0 else 0
        }

def main():
    """Main function for running the hybrid analysis agent."""
    async def run_hybrid_analysis():
        agent = HybridAnalysisAgent(ai_threshold=0.7)
        
        # Example transactions with different risk levels
        sample_transactions = [
            {
                "transaction_id": "tx_low_001",
                "amount": 50.00,
                "timestamp": "2024-01-15T10:30:00Z",
                "features": {"V1": 0.1, "V2": 0.2}  # Low risk features
            },
            {
                "transaction_id": "tx_high_001", 
                "amount": 5000.00,
                "timestamp": "2024-01-15T15:45:00Z",
                "features": {"V1": 2.5, "V2": -3.1}  # High risk features
            }
        ]
        
        # Analyze transactions
        for transaction in sample_transactions:
            result = await agent.analyze_transaction(transaction)
            logger.info(f"Hybrid analysis result: {json.dumps(result, indent=2)}")
        
        # Print statistics
        stats = agent.get_statistics()
        logger.info(f"Hybrid analysis statistics: {stats}")
    
    try:
        logger.info("Starting hybrid fraud analysis agent...")
        asyncio.run(run_hybrid_analysis())
    except KeyboardInterrupt:
        logger.info("Shutting down hybrid analysis agent...")
    except Exception as e:
        logger.error(f"Error running hybrid analysis agent: {str(e)}")
        raise

if __name__ == "__main__":
    main()