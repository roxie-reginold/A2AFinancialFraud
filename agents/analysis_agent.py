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

# Vertex AI imports
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, GenerationConfig
    VERTEX_AI_AVAILABLE = True
except ImportError:
    logger.warning("Vertex AI not available. Please install: pip install google-cloud-aiplatform")
    vertexai = None
    GenerativeModel = None
    GenerationConfig = None
    VERTEX_AI_AVAILABLE = False

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
        if not VERTEX_AI_AVAILABLE:
            return {
                "risk_score": 0.5,
                "analysis_method": "fallback",
                "fraud_indicators": ["Vertex AI not available"],
                "recommendations": ["Install google-cloud-aiplatform"],
                "analysis_summary": "Fallback analysis - Vertex AI unavailable"
            }
        
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

class AnalysisAgent:
    """
    AI-powered fraud analysis agent using Gemini via Vertex AI.
    
    This agent provides advanced fraud analysis capabilities using Google's
    Gemini LLM for pattern recognition and risk assessment.
    """
    
    def __init__(self):
        """Initialize the AnalysisAgent."""
        # Create the ADK agent without tools for now (simplified approach)
        self.agent = Agent(
            name="fraud_analysis_agent",
            model="gemini-2.5-pro-preview-05-06",
            instruction="""You are an expert fraud detection analyst. Your role is to:
            
            1. Analyze financial transactions for fraud indicators
            2. Provide detailed risk assessments with scores from 0.0 to 1.0
            3. Identify specific fraud patterns and suspicious behaviors
            4. Generate actionable recommendations for each transaction
            5. Explain your reasoning clearly and concisely
            
            Always be thorough in your analysis and provide specific, actionable insights.
            Focus on identifying unusual patterns, anomalous amounts, timing irregularities,
            and other fraud indicators based on the transaction data provided.""",
            description="AI-powered fraud analysis using Gemini for advanced pattern recognition"
        )
        
        # Initialize Pub/Sub for communication
        self._publisher = pubsub_v1.PublisherClient()
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "fraud-detection-adkhackathon")
        self._analysis_topic_path = self._publisher.topic_path(project_id, "analysis-results")
        
        # Statistics
        self._analyzed_count = 0
        self._high_risk_count = 0
        
        logger.info("AnalysisAgent initialized with Gemini AI capabilities")
    
    async def analyze_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single transaction for fraud risk.
        
        Args:
            transaction_data: Transaction data to analyze
            
        Returns:
            Analysis result with risk assessment
        """
        try:
            self._analyzed_count += 1
            
            # Use the ADK tool for analysis
            analysis_result = analyze_transaction_risk(transaction_data)
            
            # Add metadata
            analysis_result.update({
                "transaction_id": transaction_data.get("transaction_id", f"tx_{self._analyzed_count}"),
                "alert_id": f"alert_{self._analyzed_count}",
                "alert_timestamp": transaction_data.get("timestamp", "unknown"),
                "amount": transaction_data.get("amount", 0)
            })
            
            # Track high-risk transactions
            if analysis_result.get("risk_score", 0) >= 0.8:
                self._high_risk_count += 1
                await self._publish_high_risk_alert(analysis_result)
            
            logger.info(f"Analyzed transaction {analysis_result['transaction_id']} - Risk: {analysis_result['risk_score']:.3f}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing transaction: {str(e)}")
            return {
                "transaction_id": transaction_data.get("transaction_id", "unknown"),
                "risk_score": 0.5,
                "analysis_method": "error",
                "error": str(e),
                "fraud_indicators": ["Analysis error occurred"],
                "recommendations": ["Manual review required"],
                "analysis_summary": f"Analysis failed: {str(e)}"
            }
    
    async def analyze_batch(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple transactions in batch.
        
        Args:
            transactions: List of transaction data to analyze
            
        Returns:
            List of analysis results
        """
        results = []
        batch_size = 5  # Process in smaller batches
        
        for i in range(0, len(transactions), batch_size):
            batch = transactions[i:i + batch_size]
            batch_results = []
            
            for transaction in batch:
                result = await self.analyze_transaction(transaction)
                batch_results.append(result)
            
            results.extend(batch_results)
            
            # Small delay between batches to avoid rate limiting
            await asyncio.sleep(0.1)
        
        logger.info(f"Batch analysis completed: {len(results)} transactions analyzed")
        return results
    
    async def _publish_high_risk_alert(self, analysis_result: Dict[str, Any]) -> None:
        """
        Publish high-risk transaction alert to Pub/Sub.
        
        Args:
            analysis_result: Analysis result for high-risk transaction
        """
        try:
            alert_data = {
                "alert_type": "HIGH_RISK_TRANSACTION",
                "alert_id": analysis_result["alert_id"],
                "transaction_id": analysis_result["transaction_id"],
                "risk_score": analysis_result["risk_score"],
                "analysis_method": analysis_result["analysis_method"],
                "fraud_indicators": analysis_result["fraud_indicators"],
                "recommendations": analysis_result["recommendations"],
                "analysis_summary": analysis_result["analysis_summary"],
                "timestamp": analysis_result.get("alert_timestamp"),
                "amount": analysis_result.get("amount")
            }
            
            message_data = json.dumps(alert_data).encode('utf-8')
            self._publisher.publish(self._analysis_topic_path, data=message_data)
            
            logger.info(f"🚨 Published high-risk alert for transaction {analysis_result['transaction_id']}")
            
        except Exception as e:
            logger.error(f"Error publishing high-risk alert: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics."""
        return {
            "total_analyzed": self._analyzed_count,
            "high_risk_found": self._high_risk_count,
            "high_risk_percentage": (self._high_risk_count / self._analyzed_count * 100) if self._analyzed_count > 0 else 0
        }

def main():
    """Main function for running the analysis agent."""
    async def run_analysis():
        agent = AnalysisAgent()
        
        # Example usage
        sample_transaction = {
            "transaction_id": "tx_001",
            "amount": 5000.00,
            "timestamp": "2024-01-15T10:30:00Z",
            "features": {
                "V1": -1.359807,
                "V2": -0.072781,
                "V3": 2.536347,
                "V4": 1.378155,
                "V5": -0.338321,
                # ... more features
            }
        }
        
        result = await agent.analyze_transaction(sample_transaction)
        logger.info(f"Analysis result: {json.dumps(result, indent=2)}")
        
        # Print statistics
        stats = agent.get_statistics()
        logger.info(f"Analysis statistics: {stats}")
    
    try:
        logger.info("Starting fraud analysis agent...")
        asyncio.run(run_analysis())
    except KeyboardInterrupt:
        logger.info("Shutting down analysis agent...")
    except Exception as e:
        logger.error(f"Error running analysis agent: {str(e)}")
        raise

if __name__ == "__main__":
    main()