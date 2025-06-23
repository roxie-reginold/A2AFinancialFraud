#!/usr/bin/env python3
"""
FastAPI Production API for ADK Financial Fraud Detection System

Main API service providing fraud detection endpoints for external integrations.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Request, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import uvicorn

from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Pydantic models for API
class TransactionInput(BaseModel):
    """Transaction input for fraud analysis."""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    amount: float = Field(..., gt=0, description="Transaction amount")
    merchant: Optional[str] = Field(None, description="Merchant name")
    location: Optional[str] = Field(None, description="Transaction location")
    card_type: Optional[str] = Field(None, description="Card type")
    timestamp: Optional[str] = Field(None, description="Transaction timestamp")
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class FraudAnalysisResult(BaseModel):
    """Fraud analysis result."""
    analysis_id: str = Field(..., description="Analysis identifier")
    transaction_id: str = Field(..., description="Transaction identifier")
    risk_score: float = Field(..., ge=0, le=1, description="Risk score (0-1)")
    risk_level: str = Field(..., description="Risk level (LOW/MEDIUM/HIGH)")
    fraud_indicators: List[str] = Field(default=[], description="Fraud indicators found")
    recommendations: List[str] = Field(default=[], description="Recommended actions")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Analysis confidence")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    analyzed_at: str = Field(..., description="Analysis timestamp")

class AlertResponse(BaseModel):
    """Alert creation response."""
    alert_id: str = Field(..., description="Alert identifier")
    transaction_id: str = Field(..., description="Transaction identifier")
    priority: str = Field(..., description="Alert priority")
    status: str = Field(..., description="Alert status")
    created_at: str = Field(..., description="Alert creation timestamp")

class BulkTransactionInput(BaseModel):
    """Bulk transaction input."""
    transactions: List[TransactionInput] = Field(..., description="List of transactions")
    
    @validator('transactions')
    def transactions_not_empty(cls, v):
        if not v:
            raise ValueError('Transactions list cannot be empty')
        if len(v) > 100:
            raise ValueError('Maximum 100 transactions per bulk request')
        return v

class BulkAnalysisResult(BaseModel):
    """Bulk analysis result."""
    batch_id: str = Field(..., description="Batch identifier")
    total_transactions: int = Field(..., description="Total transactions processed")
    results: List[FraudAnalysisResult] = Field(..., description="Analysis results")
    processing_summary: Dict[str, Any] = Field(..., description="Processing summary")

class FraudDetectionAPI:
    """
    Production FastAPI service for fraud detection.
    
    Provides:
    - Real-time fraud analysis endpoints
    - Bulk transaction processing
    - Alert management
    - Integration with fraud detection agents
    - Production security and monitoring
    """
    
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
        
        # Create FastAPI app
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            logger.info("Starting Fraud Detection API...")
            yield
            # Shutdown
            logger.info("Shutting down Fraud Detection API...")
        
        self.app = FastAPI(
            title="A2A Fraud Detection API",
            description="Production API for real-time fraud detection and analysis",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
            lifespan=lifespan
        )
        
        self._setup_middleware()
        self._setup_routes()
    
    def _setup_middleware(self):
        """Configure production middleware."""
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"] if settings.ENVIRONMENT == "development" else ["https://your-domain.com"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )
        
        # Trusted host middleware for security
        if settings.ENVIRONMENT == "production":
            self.app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=["your-domain.com", "*.your-domain.com"]
            )
        
        # Gzip compression
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Mount static files for React frontend
        if os.path.exists("/app/static"):
            self.app.mount("/static", StaticFiles(directory="/app/static"), name="static")
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.post(
            "/api/v1/analyze",
            response_model=FraudAnalysisResult,
            summary="Analyze Single Transaction",
            description="Analyze a single transaction for fraud indicators"
        )
        async def analyze_transaction(
            transaction: TransactionInput,
            background_tasks: BackgroundTasks,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Analyze a single transaction for fraud."""
            try:
                # Validate authentication (implement your auth logic)
                await self._validate_auth(credentials)
                
                # Process transaction through fraud detection
                result = await self._process_transaction(transaction)
                
                # Add background task for logging/alerts
                background_tasks.add_task(
                    self._handle_analysis_result, 
                    transaction.transaction_id, 
                    result
                )
                
                return result
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Analysis error for transaction {transaction.transaction_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Analysis failed: {str(e)}"
                )
        
        @self.app.post(
            "/api/v1/analyze/bulk",
            response_model=BulkAnalysisResult,
            summary="Analyze Multiple Transactions",
            description="Analyze multiple transactions in batch"
        )
        async def analyze_bulk_transactions(
            bulk_input: BulkTransactionInput,
            background_tasks: BackgroundTasks,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Analyze multiple transactions in batch."""
            try:
                # Validate authentication
                await self._validate_auth(credentials)
                
                # Process transactions
                batch_id = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                results = []
                
                for transaction in bulk_input.transactions:
                    try:
                        result = await self._process_transaction(transaction)
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Error processing transaction {transaction.transaction_id}: {e}")
                        # Continue with other transactions
                
                # Generate summary
                processing_summary = {
                    "total_processed": len(results),
                    "total_requested": len(bulk_input.transactions),
                    "high_risk_count": sum(1 for r in results if r.risk_level == "HIGH"),
                    "medium_risk_count": sum(1 for r in results if r.risk_level == "MEDIUM"),
                    "low_risk_count": sum(1 for r in results if r.risk_level == "LOW"),
                }
                
                bulk_result = BulkAnalysisResult(
                    batch_id=batch_id,
                    total_transactions=len(results),
                    results=results,
                    processing_summary=processing_summary
                )
                
                # Add background task for bulk processing alerts
                background_tasks.add_task(
                    self._handle_bulk_analysis_result,
                    batch_id,
                    bulk_result
                )
                
                return bulk_result
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Bulk analysis error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Bulk analysis failed: {str(e)}"
                )
        
        @self.app.post(
            "/api/v1/alerts",
            response_model=AlertResponse,
            summary="Create Fraud Alert",
            description="Create a fraud alert for a transaction"
        )
        async def create_alert(
            transaction_id: str,
            priority: str = "HIGH",
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Create a fraud alert."""
            try:
                # Validate authentication
                await self._validate_auth(credentials)
                
                # Create alert
                alert_id = f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{transaction_id}"
                
                alert_response = AlertResponse(
                    alert_id=alert_id,
                    transaction_id=transaction_id,
                    priority=priority,
                    status="ACTIVE",
                    created_at=datetime.utcnow().isoformat()
                )
                
                # Trigger alert through alert agent
                if self.orchestrator and "alert" in self.orchestrator.agents:
                    # Send alert to alert agent (implement actual integration)
                    pass
                
                return alert_response
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Alert creation error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Alert creation failed: {str(e)}"
                )
        
        @self.app.get(
            "/api/v1/transactions/{transaction_id}/analysis",
            response_model=FraudAnalysisResult,
            summary="Get Transaction Analysis",
            description="Retrieve analysis results for a specific transaction"
        )
        async def get_transaction_analysis(
            transaction_id: str,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Get analysis results for a transaction."""
            try:
                # Validate authentication
                await self._validate_auth(credentials)
                
                # Retrieve analysis from storage (implement actual retrieval)
                # This is a placeholder - implement actual data retrieval
                analysis = await self._get_stored_analysis(transaction_id)
                
                if not analysis:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Analysis not found for transaction {transaction_id}"
                    )
                
                return analysis
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Analysis retrieval error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Analysis retrieval failed: {str(e)}"
                )
        
        # Add request logging middleware
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            """Log all incoming requests."""
            start_time = datetime.utcnow()
            
            response = await call_next(request)
            
            process_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            return response
        
        # Catch-all route for React app (must be last!)
        if os.path.exists("/app/static"):
            @self.app.get("/{full_path:path}")
            async def serve_react_app(full_path: str):
                # Don't serve React for API routes
                if (full_path.startswith("api/") or full_path.startswith("docs") or 
                    full_path.startswith("redoc") or full_path.startswith("openapi.json") or 
                    full_path.startswith("health") or full_path.startswith("metrics")):
                    raise HTTPException(status_code=404, detail="API endpoint not found")
                
                # Serve React index.html for all other routes (client-side routing)
                return FileResponse("/app/static/index.html")
    
    async def _validate_auth(self, credentials: HTTPAuthorizationCredentials):
        """Validate API authentication."""
        # Implement your authentication logic here
        # This is a placeholder - use proper authentication
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def _process_transaction(self, transaction: TransactionInput) -> FraudAnalysisResult:
        """Process a transaction through fraud detection using real agents."""
        start_time = datetime.utcnow()
        
        try:
            # Convert TransactionInput to transaction dict for agents
            transaction_dict = {
                "transaction_id": transaction.transaction_id,
                "user_id": f"user_{transaction.transaction_id}",  # Generate user_id from transaction_id
                "amount": transaction.amount,
                "currency": "USD",
                "timestamp": transaction.timestamp or datetime.utcnow().isoformat(),
                "merchant": transaction.merchant or "Unknown",
                "location": transaction.location or "Unknown",
                "payment_method": transaction.card_type or "unknown"
            }
            
            # Use real agents if orchestrator is available
            if self.orchestrator and hasattr(self.orchestrator, 'agents'):
                # Step 1: Monitor transaction
                monitor_result = await self.orchestrator.agents['monitor'].process_transaction(transaction_dict)
                
                # Step 2: Analyze if flagged
                if monitor_result.get('flagged', False):
                    analysis_result = await self.orchestrator.agents['hybrid'].analyze_transaction(transaction_dict)
                    risk_score = analysis_result.get('risk_score', 0)
                    
                    # Step 3: Generate alerts for high-risk transactions
                    if risk_score >= 0.8:
                        alert_data = {
                            "alert_id": f"ALERT_{transaction.transaction_id}_{int(datetime.utcnow().timestamp())}",
                            "transaction_id": transaction.transaction_id,
                            "risk_score": risk_score,
                            "priority": "HIGH",
                            "analysis_summary": analysis_result.get("analysis_summary", "High-risk transaction detected"),
                            "recommendations": analysis_result.get("recommendations", ["Review immediately", "Block transaction"]),
                            "fraud_indicators": analysis_result.get("fraud_indicators", ["High risk score"]),
                            "amount": transaction.amount,
                            "alert_timestamp": datetime.utcnow().isoformat(),
                            "analysis_method": "api_hybrid"
                        }
                        
                        # Process through alert agent
                        logger.info(f"🚨 High-risk transaction detected: {transaction.transaction_id}")
                        await self.orchestrator.agents['alert'].process_alert(alert_data)
                    
                    # Use real analysis results
                    risk_level = "HIGH" if risk_score >= 0.7 else "MEDIUM" if risk_score >= 0.3 else "LOW"
                    fraud_indicators = analysis_result.get("fraud_indicators", [])
                    recommendations = analysis_result.get("recommendations", [])
                    
                else:
                    # Not flagged by monitor
                    risk_score = 0.1
                    risk_level = "LOW"
                    fraud_indicators = []
                    recommendations = []
                    
            else:
                # Fallback to mock data if no orchestrator
                logger.warning("⚠️ No orchestrator available, using mock analysis")
                risk_score = 0.9 if transaction.amount > 10000 else 0.5  # High risk for large amounts
                risk_level = "HIGH" if risk_score >= 0.7 else "MEDIUM" if risk_score >= 0.3 else "LOW"
                fraud_indicators = ["large_amount"] if transaction.amount > 10000 else ["medium_amount"]
                recommendations = ["block_transaction"] if risk_score >= 0.8 else ["review_manually"]
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return FraudAnalysisResult(
                analysis_id=f"analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{transaction.transaction_id}",
                transaction_id=transaction.transaction_id,
                risk_score=risk_score,
                risk_level=risk_level,
                fraud_indicators=fraud_indicators,
                recommendations=recommendations,
                confidence_score=0.95,
                processing_time_ms=int(processing_time),
                analyzed_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"❌ Error processing transaction {transaction.transaction_id}: {str(e)}")
            # Return safe fallback result
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            return FraudAnalysisResult(
                analysis_id=f"error_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{transaction.transaction_id}",
                transaction_id=transaction.transaction_id,
                risk_score=0.0,
                risk_level="ERROR",
                fraud_indicators=["processing_error"],
                recommendations=["retry_analysis"],
                confidence_score=0.0,
                processing_time_ms=int(processing_time),
                analyzed_at=datetime.utcnow().isoformat()
            )
    
    async def _handle_analysis_result(self, transaction_id: str, result: FraudAnalysisResult):
        """Handle analysis result in background."""
        # Implement logging, alerting, etc.
        logger.info(f"Processed transaction {transaction_id} with risk score {result.risk_score}")
        
        # Send to reporting agent if high risk
        if result.risk_level == "HIGH":
            logger.warning(f"High risk transaction detected: {transaction_id}")
    
    async def _handle_bulk_analysis_result(self, batch_id: str, result: BulkAnalysisResult):
        """Handle bulk analysis result in background."""
        logger.info(f"Processed batch {batch_id} with {result.total_transactions} transactions")
        
        high_risk_count = result.processing_summary.get("high_risk_count", 0)
        if high_risk_count > 0:
            logger.warning(f"Batch {batch_id} contains {high_risk_count} high-risk transactions")
    
    async def _get_stored_analysis(self, transaction_id: str) -> Optional[FraudAnalysisResult]:
        """Retrieve stored analysis results."""
        # Implement actual data retrieval from your storage system
        # This is a placeholder
        return None
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the FastAPI server."""
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            reload=settings.ENVIRONMENT == "development"
        )
        
        server = uvicorn.Server(config)
        
        logger.info(f"Fraud Detection API starting on {host}:{port}")
        logger.info(f"OpenAPI docs: http://{host}:{port}/docs")
        logger.info(f"API endpoints: http://{host}:{port}/api/v1/")
        
        return server

async def main():
    """Run API service standalone for testing."""
    api_service = FraudDetectionAPI()
    server = await api_service.start_server()
    
    try:
        logger.info("Fraud Detection API running. Press Ctrl+C to stop.")
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Shutting down API service...")

if __name__ == "__main__":
    asyncio.run(main())