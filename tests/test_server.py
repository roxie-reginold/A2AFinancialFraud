#!/usr/bin/env python3
"""
Simple test server for the React frontend
"""
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime
import random

app = FastAPI(
    title="Fraud Detection Test API",
    description="Test API for fraud detection",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models matching frontend expectations
class Transaction(BaseModel):
    Time: float
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float

class AnalysisResult(BaseModel):
    transaction_id: str
    risk_score: float
    is_fraud: bool
    analysis_method: str
    model_confidence: float
    risk_factors: List[str]
    timestamp: str

class Alert(BaseModel):
    id: str
    transaction_id: str
    risk_score: float
    message: str
    timestamp: str
    status: str

# In-memory storage for demo
alerts_storage = []

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/analyze", response_model=AnalysisResult)
async def analyze_transaction(transaction: Transaction):
    # Simple risk scoring based on amount and some V features
    risk_score = min(1.0, (transaction.Amount / 1000.0) + abs(transaction.V1) * 0.1 + abs(transaction.V2) * 0.1)
    is_fraud = risk_score > 0.5
    
    risk_factors = []
    if transaction.Amount > 500:
        risk_factors.append("High transaction amount")
    if abs(transaction.V1) > 2:
        risk_factors.append("Unusual V1 pattern")
    if abs(transaction.V2) > 2:
        risk_factors.append("Unusual V2 pattern")
    
    return AnalysisResult(
        transaction_id=str(uuid.uuid4()),
        risk_score=risk_score,
        is_fraud=is_fraud,
        analysis_method="hybrid_ml_model",
        model_confidence=random.uniform(0.7, 0.95),
        risk_factors=risk_factors,
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/v1/alerts", response_model=Alert)
async def create_alert(alert_data: dict):
    alert = Alert(
        id=str(uuid.uuid4()),
        transaction_id=alert_data["transaction_id"],
        risk_score=alert_data["risk_score"],
        message=alert_data["message"],
        timestamp=datetime.now().isoformat(),
        status=alert_data.get("status", "pending")
    )
    alerts_storage.append(alert)
    return alert

@app.get("/api/v1/alerts", response_model=List[Alert])
async def get_alerts():
    return alerts_storage

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)