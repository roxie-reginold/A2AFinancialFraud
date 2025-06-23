#!/usr/bin/env python3
"""
FastAPI Health Check Service for ADK Financial Fraud Detection System

Production-grade health monitoring API with comprehensive endpoints.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
import uvicorn

from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API responses
class HealthStatus(BaseModel):
    """Health status response model."""
    status: str = Field(..., description="Overall system health status")
    message: str = Field(..., description="Human-readable status message") 
    healthy_agents: int = Field(..., description="Number of healthy agents")
    total_agents: int = Field(..., description="Total number of agents")
    timestamp: str = Field(..., description="ISO timestamp of health check")

class AgentHealth(BaseModel):
    """Individual agent health model."""
    healthy: bool = Field(..., description="Whether the agent is healthy")
    type: str = Field(..., description="Agent class name")
    status: str = Field(..., description="Agent status (running/failed/starting)")
    last_seen: Optional[str] = Field(None, description="Last seen timestamp")

class AgentsHealthResponse(BaseModel):
    """Agents health response model."""
    status: str = Field(..., description="Overall agent health status")
    agents: Dict[str, AgentHealth] = Field(..., description="Individual agent statuses")
    total_agents: int = Field(..., description="Total number of agents")
    healthy_agents: int = Field(..., description="Number of healthy agents")
    timestamp: str = Field(..., description="ISO timestamp")

class SystemStatus(BaseModel):
    """Complete system status model."""
    timestamp: str
    environment: str
    project_id: str
    agents: Dict[str, Dict[str, Any]]
    system_health: str
    health_service: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None
    uptime_seconds: Optional[float] = None

class ReadinessResponse(BaseModel):
    """Kubernetes readiness probe response."""
    ready: bool = Field(..., description="Whether system is ready to receive traffic")
    healthy_agents: int = Field(..., description="Number of healthy agents")
    total_agents: int = Field(..., description="Total number of agents")
    reason: Optional[str] = Field(None, description="Reason if not ready")

class LivenessResponse(BaseModel):
    """Kubernetes liveness probe response."""
    alive: bool = Field(..., description="Whether service is alive")
    timestamp: str = Field(..., description="Current timestamp")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")

class PerformanceMetrics(BaseModel):
    """System performance metrics."""
    cpu_percent: float
    memory_percent: float
    disk_percent: float

class InfrastructureHealth(BaseModel):
    """External infrastructure health."""
    google_cloud: str
    pubsub: str
    bigquery: str

class DetailedHealthResponse(BaseModel):
    """Comprehensive health check response."""
    system: HealthStatus
    agents: Dict[str, AgentHealth]
    infrastructure: InfrastructureHealth
    performance: PerformanceMetrics
    history: List[Dict[str, Any]]
    uptime_seconds: float

class HealthCheckService:
    """
    FastAPI-based health check service for production fraud detection system.
    
    Provides comprehensive monitoring endpoints with:
    - RESTful API design with OpenAPI documentation
    - Pydantic models for type safety and validation
    - Production middleware (CORS, compression, security)
    - Structured logging and error handling
    - Prometheus metrics integration
    - Kubernetes probe endpoints
    """
    
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
        self.startup_time = datetime.utcnow()
        self.last_health_check = None
        self.health_history = []
        
        # Create FastAPI app with lifespan management
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            logger.info("Starting FastAPI health check service...")
            yield
            # Shutdown
            logger.info("Shutting down FastAPI health check service...")
        
        self.app = FastAPI(
            title="A2A Fraud Detection Health Service",
            description="Production health monitoring API for the fraud detection system",
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
    
    def _setup_routes(self):
        """Setup API routes."""
        
        # Root health check for Cloud Run
        @self.app.get("/", include_in_schema=False)
        async def root():
            return {"status": "ok", "service": "fraud-detection-backend"}
            
        # Simple health check
        @self.app.get("/health", include_in_schema=False)
        async def health():
            return {"status": "healthy"}
            
        @self.app.get(
            "/health",
            response_model=HealthStatus,
            summary="Basic Health Check",
            description="Returns overall system health status"
        )
        async def health_check():
            """Basic health check endpoint."""
            try:
                health_status = await self._get_system_health()
                self.last_health_check = datetime.utcnow()
                self._update_health_history(health_status)
                
                return HealthStatus(**health_status)
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Health check failed: {str(e)}"
                )
        
        @self.app.get(
            "/health/agents",
            response_model=AgentsHealthResponse,
            summary="Agent Health Status",
            description="Returns detailed health status for all agents"
        )
        async def agents_health():
            """Detailed agent health status."""
            try:
                if not self.orchestrator:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Orchestrator not available"
                    )
                
                agent_status = {}
                for agent_name, agent in self.orchestrator.agents.items():
                    agent_status[agent_name] = AgentHealth(
                        healthy=self.orchestrator._agent_health.get(agent_name, False),
                        type=type(agent).__name__,
                        status="running" if self.orchestrator._agent_health.get(agent_name, False) else "failed",
                        last_seen=datetime.utcnow().isoformat()
                    )
                
                overall_healthy = all(
                    agent.healthy for agent in agent_status.values()
                )
                
                return AgentsHealthResponse(
                    status="healthy" if overall_healthy else "degraded",
                    agents=agent_status,
                    total_agents=len(agent_status),
                    healthy_agents=sum(1 for a in agent_status.values() if a.healthy),
                    timestamp=datetime.utcnow().isoformat()
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Agent health check error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e)
                )
        
        @self.app.get(
            "/health/detailed",
            response_model=DetailedHealthResponse,
            summary="Comprehensive Health Check",
            description="Returns comprehensive system health information"
        )
        async def detailed_health():
            """Comprehensive health check with detailed information."""
            try:
                system_health = await self._get_system_health()
                agent_health = await self._get_agent_health_detailed()
                infrastructure = await self._get_infrastructure_health()
                performance = await self._get_performance_metrics()
                
                return DetailedHealthResponse(
                    system=HealthStatus(**system_health),
                    agents={k: AgentHealth(**v) for k, v in agent_health.items()},
                    infrastructure=InfrastructureHealth(**infrastructure),
                    performance=PerformanceMetrics(**performance),
                    history=self.health_history[-10:],
                    uptime_seconds=(datetime.utcnow() - self.startup_time).total_seconds()
                )
                
            except Exception as e:
                logger.error(f"Detailed health check error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e)
                )
        
        @self.app.get(
            "/metrics",
            response_class=PlainTextResponse,
            summary="Prometheus Metrics",
            description="Returns Prometheus-compatible metrics"
        )
        async def metrics():
            """Prometheus-compatible metrics endpoint."""
            try:
                metrics_data = await self._generate_prometheus_metrics()
                return PlainTextResponse(
                    content=metrics_data,
                    media_type="text/plain; version=0.0.4; charset=utf-8"
                )
                
            except Exception as e:
                logger.error(f"Metrics endpoint error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Metrics generation failed: {str(e)}"
                )
        
        @self.app.get(
            "/status",
            response_model=SystemStatus,
            summary="System Status",
            description="Returns complete system status and configuration"
        )
        async def system_status():
            """System status endpoint with configuration info."""
            try:
                if self.orchestrator:
                    status_data = await self.orchestrator.system_status()
                else:
                    status_data = {
                        'timestamp': datetime.utcnow().isoformat(),
                        'environment': settings.ENVIRONMENT,
                        'project_id': settings.PROJECT_ID,
                        'agents': {},
                        'system_health': 'unknown'
                    }
                
                # Add additional system information
                status_data.update({
                    'health_service': {
                        'startup_time': self.startup_time.isoformat(),
                        'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
                        'health_checks_performed': len(self.health_history)
                    },
                    'configuration': {
                        'environment': settings.ENVIRONMENT,
                        'log_level': settings.monitoring.log_level,
                        'health_check_interval': settings.monitoring.health_check_interval
                    },
                    'uptime_seconds': (datetime.utcnow() - self.startup_time).total_seconds()
                })
                
                return SystemStatus(**status_data)
                
            except Exception as e:
                logger.error(f"System status error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e)
                )
        
        @self.app.get(
            "/ready",
            response_model=ReadinessResponse,
            summary="Readiness Probe",
            description="Kubernetes readiness probe endpoint"
        )
        async def readiness_check():
            """Kubernetes readiness probe."""
            try:
                if not self.orchestrator:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Orchestrator not initialized"
                    )
                
                healthy_agents = sum(
                    1 for health in self.orchestrator._agent_health.values() if health
                )
                total_agents = len(self.orchestrator._agent_health)
                ready = healthy_agents > 0
                
                if not ready:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="No healthy agents available"
                    )
                
                return ReadinessResponse(
                    ready=ready,
                    healthy_agents=healthy_agents,
                    total_agents=total_agents
                )
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=str(e)
                )
        
        @self.app.get(
            "/live",
            response_model=LivenessResponse,
            summary="Liveness Probe", 
            description="Kubernetes liveness probe endpoint"
        )
        async def liveness_check():
            """Kubernetes liveness probe."""
            try:
                return LivenessResponse(
                    alive=True,
                    timestamp=datetime.utcnow().isoformat(),
                    uptime_seconds=(datetime.utcnow() - self.startup_time).total_seconds()
                )
                
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e)
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
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        if not self.orchestrator:
            return {
                'status': 'starting',
                'message': 'System initializing',
                'healthy_agents': 0,
                'total_agents': 0,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        healthy_agents = sum(
            1 for health in self.orchestrator._agent_health.values() if health
        )
        total_agents = len(self.orchestrator._agent_health)
        
        if healthy_agents == total_agents and total_agents > 0:
            status = 'healthy'
            message = 'All systems operational'
        elif healthy_agents > 0:
            status = 'degraded'
            message = f'{healthy_agents}/{total_agents} agents healthy'
        else:
            status = 'unhealthy'
            message = 'No healthy agents'
        
        return {
            'status': status,
            'message': message,
            'healthy_agents': healthy_agents,
            'total_agents': total_agents,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _get_agent_health_detailed(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed agent health information."""
        if not self.orchestrator:
            return {}
        
        return {
            agent_name: {
                'healthy': self.orchestrator._agent_health.get(agent_name, False),
                'type': type(agent).__name__,
                'status': 'running' if self.orchestrator._agent_health.get(agent_name, False) else 'failed',
                'last_seen': datetime.utcnow().isoformat()
            }
            for agent_name, agent in self.orchestrator.agents.items()
        }
    
    async def _get_infrastructure_health(self) -> Dict[str, str]:
        """Check health of external infrastructure."""
        # TODO: Implement actual infrastructure health checks
        return {
            'google_cloud': 'healthy',
            'pubsub': 'healthy', 
            'bigquery': 'healthy'
        }
    
    async def _get_performance_metrics(self) -> Dict[str, float]:
        """Get basic performance metrics."""
        import psutil
        
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
        }
    
    async def _generate_prometheus_metrics(self) -> str:
        """Generate Prometheus-compatible metrics."""
        metrics = []
        
        if self.orchestrator:
            healthy_agents = sum(
                1 for health in self.orchestrator._agent_health.values() if health
            )
            total_agents = len(self.orchestrator._agent_health)
            
            metrics.extend([
                f'fraud_detection_agents_total {total_agents}',
                f'fraud_detection_agents_healthy {healthy_agents}',
                f'fraud_detection_uptime_seconds {(datetime.utcnow() - self.startup_time).total_seconds()}',
                f'fraud_detection_health_checks_total {len(self.health_history)}'
            ])
            
            # Individual agent metrics
            for agent_name, healthy in self.orchestrator._agent_health.items():
                metrics.append(
                    f'fraud_detection_agent_healthy{{agent="{agent_name}"}} {1 if healthy else 0}'
                )
        
        return '\n'.join(metrics) + '\n'
    
    def _update_health_history(self, health_status: Dict[str, Any]):
        """Update health check history."""
        self.health_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'status': health_status['status'],
            'healthy_agents': health_status.get('healthy_agents', 0),
            'total_agents': health_status.get('total_agents', 0)
        })
        
        # Keep only last 100 entries
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8080):
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
        
        logger.info(f"FastAPI health service starting on {host}:{port}")
        logger.info(f"OpenAPI docs: http://{host}:{port}/docs")
        logger.info(f"Health endpoint: http://{host}:{port}/health")
        logger.info(f"Metrics endpoint: http://{host}:{port}/metrics")
        
        # Return the server object for manual control
        return server

async def main():
    """Run health check service standalone for testing."""
    health_service = HealthCheckService()
    server = await health_service.start_server()
    
    try:
        logger.info("FastAPI health service running. Press Ctrl+C to stop.")
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Shutting down health service...")

if __name__ == "__main__":
    asyncio.run(main())