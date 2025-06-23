import json
import logging
import numpy as np
from typing import AsyncGenerator, Dict, Any, List
import asyncio
import os

# ADK imports
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# Google Cloud imports for downstream communication
from google.cloud import pubsub_v1

# TensorFlow/Keras for local model
try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("TensorFlow not available. Please install: pip install tensorflow")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalAnalysisAgent(BaseAgent):
    """
    Local ML-powered fraud analysis agent using a trained Keras model.
    
    This agent follows ADK best practices and provides:
    - Fast local fraud risk assessment using fraud_detection_model.keras
    - Feature-based transaction analysis with trained ML model
    - Risk scoring based on model predictions
    - Integration with downstream alert and reporting systems
    """
    
    def __init__(self, name: str, project_id: str, model_path: str = "fraud_detection_model.keras"):
        super().__init__(name=name)
        
        # Store configuration
        self._project_id = project_id
        self._model_path = model_path
        self._model = None
        
        # Load the local model
        self._load_local_model()
        
        # Initialize Pub/Sub for downstream communication
        self._publisher = pubsub_v1.PublisherClient()
        self._analysis_topic_path = self._publisher.topic_path(project_id, "analysis-results")
        
        # Analysis statistics
        self._analyzed_count = 0
        self._high_risk_count = 0
        
        logger.info(f"LocalAnalysisAgent initialized with model: {model_path}")
    
    def _load_local_model(self):
        """Load the local Keras fraud detection model."""
        try:
            if not TENSORFLOW_AVAILABLE:
                raise ImportError("TensorFlow is required for local model inference")
                
            if not os.path.exists(self._model_path):
                raise FileNotFoundError(f"Model file not found: {self._model_path}")
            
            # Load the Keras model
            self._model = keras.models.load_model(self._model_path)
            logger.info(f"✅ Local fraud detection model loaded successfully from {self._model_path}")
            
            # Log model information
            logger.info(f"📊 Model input shape: {self._model.input_shape}")
            logger.info(f"📊 Model output shape: {self._model.output_shape}")
            
        except Exception as e:
            logger.error(f"❌ Error loading local model: {str(e)}")
            self._model = None

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Main analysis workflow using local ML model following ADK best practices.
        Processes flagged transactions using the trained Keras model for fraud analysis.
        """
        logger.info(f"[{self.name}] Starting local ML-powered fraud analysis workflow...")
        
        # Step 1: Initialize analysis workflow
        yield Event(
            author=self.name,
            actions=EventActions(state_delta={
                "analysis_status": "initializing",
                "model_path": self._model_path,
                "model_available": self._model is not None,
                "analyzed_transactions": 0,
                "high_risk_transactions": 0
            }),
            content=types.Content(
                role='assistant',
                parts=[types.Part(text="🔬 Initializing local ML fraud analysis system...")]
            )
        )
        
        # Check if model is available
        if self._model is None:
            yield Event(
                author=self.name,
                actions=EventActions(state_delta={
                    "analysis_status": "model_unavailable"
                }),
                content=types.Content(
                    role='assistant',
                    parts=[types.Part(text="❌ Local ML model not available. Please check model file.")]
                ),
                is_final_response=True
            )
            return
        
        # Step 2: Collect flagged transactions from session state
        flagged_transactions = self._collect_flagged_transactions(ctx)
        
        if not flagged_transactions:
            yield Event(
                author=self.name,
                actions=EventActions(state_delta={
                    "analysis_status": "no_flagged_transactions"
                }),
                content=types.Content(
                    role='assistant',
                    parts=[types.Part(text="ℹ️  No flagged transactions found for local ML analysis.")]
                ),
                is_final_response=True
            )
            return
        
        yield Event(
            author=self.name,
            actions=EventActions(state_delta={
                "analysis_status": "processing",
                "total_flagged_transactions": len(flagged_transactions)
            }),
            content=types.Content(
                role='assistant',
                parts=[types.Part(text=f"🔍 Found {len(flagged_transactions)} flagged transactions for local ML analysis...")]
            )
        )
        
        # Step 3: Process each flagged transaction with local ML analysis
        try:
            async for analysis_result in self._analyze_transactions_batch(ctx, flagged_transactions):
                # Yield events for each analysis batch
                yield Event(
                    author=self.name,
                    actions=EventActions(state_delta=analysis_result["state_updates"]),
                    content=types.Content(
                        role='assistant',
                        parts=[types.Part(text=analysis_result["status_message"])]
                    )
                )
                
                # Publish high-risk transactions to alert system
                if analysis_result.get("high_risk_transactions"):
                    await self._publish_high_risk_alerts(analysis_result["high_risk_transactions"])
                    
        except Exception as e:
            logger.error(f"[{self.name}] Error in local ML analysis workflow: {str(e)}")
            yield Event(
                author=self.name,
                actions=EventActions(state_delta={
                    "analysis_status": "error",
                    "error_message": str(e)
                }),
                content=types.Content(
                    role='assistant',
                    parts=[types.Part(text=f"❌ Local ML analysis error: {str(e)}")]
                )
            )
        
        # Step 4: Finalize analysis workflow
        final_stats = ctx.session.state
        yield Event(
            author=self.name,
            actions=EventActions(state_delta={
                "analysis_status": "completed",
                "analysis_summary": {
                    "total_analyzed": final_stats.get('analyzed_transactions', 0),
                    "high_risk_found": final_stats.get('high_risk_transactions', 0),
                    "model_used": "Local Keras Model"
                }
            }),
            content=types.Content(
                role='assistant',
                parts=[types.Part(text=f"✅ Local ML Analysis completed! Analyzed: {final_stats.get('analyzed_transactions', 0)}, High Risk: {final_stats.get('high_risk_transactions', 0)}")]
            ),
            is_final_response=True
        )

    def _collect_flagged_transactions(self, ctx: InvocationContext) -> List[Dict[str, Any]]:
        """Collect flagged transactions from session state."""
        flagged_transactions = []
        
        # Look for flagged transactions in session state
        for key, value in ctx.session.state.items():
            if key.startswith("flagged_tx_") and isinstance(value, dict):
                flagged_transactions.append(value)
            elif key.startswith("flagged_") and isinstance(value, dict) and "transaction_id" in value:
                flagged_transactions.append(value)
        
        logger.info(f"[{self.name}] Collected {len(flagged_transactions)} flagged transactions")
        return flagged_transactions

    async def _analyze_transactions_batch(self, ctx: InvocationContext, transactions: List[Dict[str, Any]]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Analyze transactions in batches using local Keras model.
        """
        batch_size = 10  # Process 10 transactions at a time (faster than AI)
        analyzed_count = 0
        high_risk_count = 0
        
        for i in range(0, len(transactions), batch_size):
            batch = transactions[i:i + batch_size]
            batch_analyses = []
            batch_high_risk = []
            
            # Prepare features for batch prediction
            batch_features = []
            valid_transactions = []
            
            for transaction in batch:
                try:
                    features = self._prepare_features_for_model(transaction)
                    if features is not None:
                        batch_features.append(features)
                        valid_transactions.append(transaction)
                except Exception as e:
                    logger.error(f"[{self.name}] Error preparing features for {transaction.get('transaction_id')}: {str(e)}")
                    continue
            
            if batch_features:
                try:
                    # Batch prediction for efficiency
                    batch_features_array = np.array(batch_features)
                    predictions = await self._predict_batch(batch_features_array)
                    
                    # Process predictions
                    for j, (transaction, prediction) in enumerate(zip(valid_transactions, predictions)):
                        analysis_result = self._create_analysis_result(transaction, prediction)
                        batch_analyses.append(analysis_result)
                        analyzed_count += 1
                        
                        # Check if high risk
                        if analysis_result.get("risk_level") == "HIGH":
                            high_risk_count += 1
                            batch_high_risk.append(analysis_result)
                            
                        logger.info(f"🔬 [{self.name}] Analyzed transaction {transaction.get('transaction_id')}: {analysis_result.get('risk_level')} risk (score: {analysis_result.get('risk_score'):.3f})")
                        
                except Exception as e:
                    logger.error(f"[{self.name}] Error in batch prediction: {str(e)}")
                    continue
            
            # Create state updates for this batch
            state_updates = {
                "analyzed_transactions": analyzed_count,
                "high_risk_transactions": high_risk_count,
                "current_analysis_batch": i // batch_size + 1
            }
            
            # Store analysis results in session state
            for j, analysis in enumerate(batch_analyses):
                state_updates[f"local_analysis_result_{analyzed_count - len(batch_analyses) + j}"] = analysis
            
            # Yield batch results
            yield {
                "state_updates": state_updates,
                "status_message": f"🔬 Batch {i // batch_size + 1}: Analyzed {len(batch_analyses)} transactions, {len(batch_high_risk)} high risk",
                "high_risk_transactions": batch_high_risk
            }
            
            # Small delay for non-blocking behavior
            await asyncio.sleep(0.1)

    def _prepare_features_for_model(self, transaction: Dict[str, Any]) -> np.ndarray:
        """
        Prepare transaction features for the local Keras model.
        This should match the feature engineering used during model training.
        """
        try:
            # Get original transaction data
            original_data = transaction.get("original_data", {})
            features_dict = original_data.get("features", {})
            
            # The model expects 29 features (V1-V28 + Amount, excluding Time)
            # Based on the model input shape of (None, 29)
            feature_names = ['Amount'] + [f'V{i}' for i in range(1, 29)]
            
            # Extract features in the expected order
            features = []
            for feature_name in feature_names:
                if feature_name == 'Amount':
                    amount = transaction.get('amount', 0.0)
                    # Apply log transformation for amount normalization
                    features.append(np.log1p(float(amount)))
                else:
                    # V1-V28 features
                    val = features_dict.get(feature_name, 0.0)
                    features.append(float(val))
            
            # Convert to numpy array and reshape for model input
            features_array = np.array(features, dtype=np.float32).reshape(1, -1)
            
            return features_array[0]  # Return single feature vector
            
        except Exception as e:
            logger.error(f"[{self.name}] Error preparing features: {str(e)}")
            return None

    async def _predict_batch(self, batch_features: np.ndarray) -> List[float]:
        """
        Run batch prediction using the local Keras model.
        """
        try:
            # Run prediction in executor to avoid blocking
            predictions = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._model.predict(batch_features, verbose=0)
            )
            
            # Convert predictions to list of probabilities
            if predictions.ndim == 2 and predictions.shape[1] == 1:
                # Binary classification with single output
                return predictions.flatten().tolist()
            elif predictions.ndim == 1:
                # Already flattened
                return predictions.tolist()
            else:
                # Multi-class, take probability of fraud class
                return predictions[:, -1].tolist()
                
        except Exception as e:
            logger.error(f"[{self.name}] Error in model prediction: {str(e)}")
            # Return default predictions
            return [0.5] * len(batch_features)

    def _create_analysis_result(self, transaction: Dict[str, Any], prediction_score: float) -> Dict[str, Any]:
        """
        Create structured analysis result from model prediction.
        """
        # Convert prediction score to risk assessment
        if prediction_score >= 0.8:
            risk_level = "HIGH"
            risk_category = "Critical"
        elif prediction_score >= 0.6:
            risk_level = "MEDIUM"
            risk_category = "Moderate"
        else:
            risk_level = "LOW"
            risk_category = "Minimal"
        
        # Generate analysis summary based on prediction
        analysis_summary = f"Local ML model predicts {risk_category} fraud risk with confidence score of {prediction_score:.3f}"
        
        # Generate fraud indicators based on original flagging reasons
        fraud_indicators = transaction.get("reasons", [])
        if prediction_score >= 0.8:
            fraud_indicators.append(f"High ML model confidence ({prediction_score:.3f})")
        
        # Generate recommendations based on risk level
        recommendations = []
        if risk_level == "HIGH":
            recommendations = [
                "Immediate manual review required",
                "Consider blocking transaction",
                "Verify customer identity"
            ]
        elif risk_level == "MEDIUM":
            recommendations = [
                "Flag for additional monitoring",
                "Consider customer verification",
                "Review transaction patterns"
            ]
        else:
            recommendations = [
                "Standard processing acceptable",
                "Continue monitoring"
            ]
        
        return {
            "transaction_id": transaction.get("transaction_id"),
            "risk_level": risk_level,
            "risk_score": float(prediction_score),
            "analysis_summary": analysis_summary,
            "fraud_indicators": fraud_indicators,
            "recommendations": recommendations,
            "confidence": float(prediction_score),
            "timestamp": transaction.get("timestamp"),
            "amount": transaction.get("amount"), 
            "model_used": "Local Keras Model",
            "prediction_raw": float(prediction_score)
        }

    async def _publish_high_risk_alerts(self, high_risk_transactions: List[Dict[str, Any]]):
        """Publish high-risk transactions to alert system."""
        try:
            for transaction in high_risk_transactions:
                alert_data = {
                    "alert_type": "HIGH_RISK_FRAUD_LOCAL",
                    "transaction_id": transaction.get("transaction_id"),
                    "risk_score": transaction.get("risk_score"),
                    "analysis_summary": transaction.get("analysis_summary"),
                    "recommendations": transaction.get("recommendations"),
                    "timestamp": transaction.get("timestamp"),
                    "amount": transaction.get("amount"),
                    "model_type": "local_keras"
                }
                
                message_data = json.dumps(alert_data).encode('utf-8')
                future = self._publisher.publish(self._analysis_topic_path, data=message_data)
                # Don't wait for completion to avoid blocking
                
                logger.info(f"🚨 [{self.name}] Published local ML high-risk alert for transaction {transaction.get('transaction_id')}")
                
        except Exception as e:
            logger.error(f"[{self.name}] Error publishing high-risk alerts: {str(e)}")

def main():
    """
    Main function to set up and run the local analysis agent.
    """
    # Configuration
    project_id = "fraud-detection-adkhackathon"
    model_path = "fraud_detection_model.keras"
    
    # Create the local analysis agent
    local_analysis_agent = LocalAnalysisAgent(
        name="LocalFraudAnalysisAgent",
        project_id=project_id,
        model_path=model_path
    )
    
    # Set up session service
    session_service = InMemorySessionService()
    
    # Set up runner
    runner = Runner(
        agent=local_analysis_agent,
        app_name="fraud_detection",
        session_service=session_service
    )
    
    # Run the agent
    logger.info("🚀 Starting local ML-powered fraud analysis agent...")
    
    try:
        content = types.Content(
            role='user',
            parts=[types.Part(text="Start local ML fraud analysis of flagged transactions")]
        )
        
        events = runner.run(
            user_id="system",
            session_id="local_analysis_session_001",
            new_message=content
        )
        
        # Process events with detailed logging
        for event in events:
            if event.content and event.content.parts:
                logger.info(f"📢 Agent Event: {event.content.parts[0].text}")
                
            # Log state changes
            if event.actions and event.actions.state_delta:
                logger.info(f"🔄 State Updates: {list(event.actions.state_delta.keys())}")
                
            # Check for final response
            if event.is_final_response:
                logger.info("🏁 Local ML analysis workflow completed!")
                
    except KeyboardInterrupt:
        logger.info("⏹️  Local analysis stopped by user")
    except Exception as e:
        logger.error(f"❌ Error running local analysis agent: {str(e)}")

if __name__ == "__main__":
    main()
