#!/usr/bin/env python3
"""
Simplified Analysis Agent for testing and basic functionality
"""

import json
import logging
import asyncio
import os
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Vertex AI imports
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, GenerationConfig
    VERTEX_AI_AVAILABLE = True
except ImportError:
    logger.warning("Vertex AI not available. Using fallback analysis.")
    vertexai = None
    GenerativeModel = None
    GenerationConfig = None
    VERTEX_AI_AVAILABLE = False

class SimpleAnalysisAgent:
    """
    Simplified fraud analysis agent for testing purposes.
    
    Uses direct Gemini API calls without complex ADK patterns.
    """
    
    def __init__(self):
        """Initialize the analysis agent."""
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "fraud-detection-adkhackathon")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-pro-preview-05-06")
        self._analyzed_count = 0
        self._high_risk_count = 0
        
        logger.info("SimpleAnalysisAgent initialized")
    
    async def analyze_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a transaction for fraud risk.
        
        Args:
            transaction_data: Transaction data to analyze
            
        Returns:
            Analysis result with risk assessment
        """
        try:
            self._analyzed_count += 1
            
            if VERTEX_AI_AVAILABLE and os.getenv("BYPASS_CLOUD_VALIDATION", "false").lower() != "true":
                # Use real Gemini analysis
                result = await self._analyze_with_gemini(transaction_data)
            else:
                # Use fallback analysis
                result = self._analyze_with_fallback(transaction_data)
            
            # Add metadata
            result.update({
                "transaction_id": transaction_data.get("transaction_id", f"tx_{self._analyzed_count}"),
                "alert_id": f"alert_{self._analyzed_count}",
                "alert_timestamp": transaction_data.get("timestamp", "unknown"),
                "amount": transaction_data.get("amount", 0)
            })
            
            # Track high-risk transactions
            if result.get("risk_score", 0) >= 0.8:
                self._high_risk_count += 1
            
            logger.info(f"Analyzed transaction {result['transaction_id']} - Risk: {result['risk_score']:.3f}")
            
            return result
            
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
    
    async def _analyze_with_gemini(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze using Gemini AI."""
        try:
            # Initialize Vertex AI
            vertexai.init(project=self.project_id, location="us-central1")
            
            # Create Gemini model
            model = GenerativeModel(self.model_name)
            
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
                analysis["model_used"] = self.model_name
                return analysis
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "risk_score": 0.7,
                    "analysis_method": "gemini_ai_fallback",
                    "fraud_indicators": ["AI analysis completed but format error"],
                    "recommendations": ["Manual review recommended"],
                    "analysis_summary": response.text[:200] + "..." if len(response.text) > 200 else response.text,
                    "model_used": self.model_name
                }
                
        except Exception as e:
            logger.error(f"Error in Gemini analysis: {str(e)}")
            return self._analyze_with_fallback(transaction_data)
    
    def _analyze_with_fallback(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis using simple rules."""
        amount = transaction_data.get("amount", 0)
        features = transaction_data.get("features", {})
        
        # Simple rule-based analysis
        risk_score = 0.0
        fraud_indicators = []
        recommendations = []
        
        # High amount check
        if amount > 10000:
            risk_score += 0.4
            fraud_indicators.append("High transaction amount")
            recommendations.append("Verify transaction with customer")
        elif amount > 5000:
            risk_score += 0.2
            fraud_indicators.append("Elevated transaction amount")
        
        # Feature analysis
        if features:
            extreme_count = sum(1 for v in features.values() if isinstance(v, (int, float)) and abs(v) > 3)
            if extreme_count > 2:
                risk_score += 0.3
                fraud_indicators.append("Multiple extreme feature values")
                recommendations.append("Detailed feature analysis required")
        
        # Final risk assessment
        if risk_score < 0.3:
            risk_score = 0.1
            fraud_indicators = fraud_indicators or ["Transaction appears normal"]
            recommendations = recommendations or ["Standard processing"]
        elif risk_score > 1.0:
            risk_score = 0.95
        
        return {
            "risk_score": risk_score,
            "analysis_method": "fallback_rules",
            "fraud_indicators": fraud_indicators,
            "recommendations": recommendations,
            "analysis_summary": f"Rule-based analysis: {risk_score:.3f} risk score"
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics."""
        return {
            "total_analyzed": self._analyzed_count,
            "high_risk_found": self._high_risk_count,
            "high_risk_percentage": (self._high_risk_count / self._analyzed_count * 100) if self._analyzed_count > 0 else 0
        }

async def main():
    """Test the simple analysis agent."""
    agent = SimpleAnalysisAgent()
    
    # Test transaction
    sample_transaction = {
        "transaction_id": "test_001",
        "amount": 1500.00,
        "timestamp": "2024-01-15T10:30:00Z",
        "features": {"V1": 1.2, "V2": -0.5, "V3": 0.8}
    }
    
    result = await agent.analyze_transaction(sample_transaction)
    logger.info(f"Analysis result: {json.dumps(result, indent=2)}")
    
    # Print statistics
    stats = agent.get_statistics()
    logger.info(f"Analysis statistics: {stats}")

if __name__ == "__main__":
    asyncio.run(main())