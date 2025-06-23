"""
Centralized configuration management for ADK Financial Fraud Detection System.
"""

import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

@dataclass
class PubSubConfig:
    """Pub/Sub configuration for real-time messaging."""
    project_id: str
    transaction_subscription: str = "transactions-sub"
    flagged_topic: str = "flagged-transactions"
    analysis_topic: str = "analysis-results"
    alert_topic: str = "fraud-alerts"
    reporting_topic: str = "reporting-requests"

@dataclass
class BigQueryConfig:
    """BigQuery configuration for data warehousing."""
    project_id: str
    dataset_id: str = "fraud_detection"
    transactions_table: str = "transactions"
    analysis_results_table: str = "analysis_results"
    alerts_table: str = "alerts"
    reports_table: str = "reports"

@dataclass
class ModelConfig:
    """ML model configuration."""
    project_id: str
    gemini_model: str = "gemini-2.5-pro-preview-05-06"
    local_model_path: str = "models/fraud_detection_model.keras"
    vertex_ai_region: str = "us-central1"

@dataclass
class EmailConfig:
    """Email notification configuration."""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = ""
    sender_password: str = ""
    recipient_emails: List[str] = None
    
    def __post_init__(self):
        if self.recipient_emails is None:
            self.recipient_emails = []

@dataclass
class AlertConfig:
    """Alert configuration and thresholds."""
    high_risk_threshold: float = 0.8
    medium_risk_threshold: float = 0.5
    alert_cooldown_minutes: int = 5
    max_alerts_per_hour: int = 100
    enable_email_alerts: bool = True
    enable_slack_alerts: bool = False
    slack_webhook_url: str = ""

@dataclass
class MonitoringConfig:
    """System monitoring configuration."""
    health_check_interval: int = 30  # seconds
    metrics_port: int = 8080
    log_level: str = "INFO"
    enable_detailed_logging: bool = False

class Settings:
    """Central configuration management for the fraud detection system."""
    
    def __init__(self):
        # Core project configuration
        self.PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "fraud-detection-adkhackathon")
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        
        # Initialize configuration objects
        self.pubsub = PubSubConfig(project_id=self.PROJECT_ID)
        self.bigquery = BigQueryConfig(project_id=self.PROJECT_ID)
        self.model = ModelConfig(project_id=self.PROJECT_ID)
        self.monitoring = MonitoringConfig()
        
        # Email configuration from environment
        self.email = EmailConfig(
            sender_email=os.getenv("EMAIL_SENDER", ""),
            sender_password=os.getenv("EMAIL_PASSWORD", ""),
            recipient_emails=os.getenv("EMAIL_RECIPIENTS", "").split(",") if os.getenv("EMAIL_RECIPIENTS") else []
        )
        
        # Alert configuration
        self.alerts = AlertConfig(
            high_risk_threshold=float(os.getenv("HIGH_RISK_THRESHOLD", "0.8")),
            medium_risk_threshold=float(os.getenv("MEDIUM_RISK_THRESHOLD", "0.5")),
            enable_email_alerts=os.getenv("ENABLE_EMAIL_ALERTS", "true").lower() == "true",
            enable_slack_alerts=os.getenv("ENABLE_SLACK_ALERTS", "false").lower() == "true",
            slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL", "")
        )
        
        # Validate required settings
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate that required settings are configured."""
        # Only validate in production environment
        if self.ENVIRONMENT == "production":
            required_env_vars = [
                "GOOGLE_CLOUD_PROJECT",
                "GOOGLE_API_KEY"
            ]
            
            missing_vars = []
            for var in required_env_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        else:
            # In development/testing, just warn about missing variables
            if not os.getenv("GOOGLE_CLOUD_PROJECT"):
                logger.warning("GOOGLE_CLOUD_PROJECT not set, using default")
            if not os.getenv("GOOGLE_API_KEY"):
                logger.warning("GOOGLE_API_KEY not set, some features may not work")
    
    def get_agent_config(self, agent_type: str) -> Dict:
        """Get configuration specific to an agent type."""
        base_config = {
            "project_id": self.PROJECT_ID,
            "environment": self.ENVIRONMENT
        }
        
        if agent_type == "monitor":
            return {
                **base_config,
                "subscription_name": self.pubsub.transaction_subscription,
                "flagged_topic": self.pubsub.flagged_topic
            }
        
        elif agent_type == "analysis":
            return {
                **base_config,
                "model_name": self.model.gemini_model,
                "analysis_topic": self.pubsub.analysis_topic
            }
        
        elif agent_type == "alert":
            return {
                **base_config,
                "alert_subscriptions": [self.pubsub.flagged_topic, self.pubsub.analysis_topic],
                "notification_config": {
                    "email": self.email,
                    "alerts": self.alerts
                }
            }
        
        elif agent_type == "reporting":
            return {
                **base_config,
                "bigquery_config": {
                    "project_id": self.bigquery.project_id,
                    "dataset_id": self.bigquery.dataset_id,
                    "transactions_table": self.bigquery.transactions_table,
                    "analysis_results_table": self.bigquery.analysis_results_table,
                    "alerts_table": self.bigquery.alerts_table,
                    "reports_table": self.bigquery.reports_table
                },
                "reporting_topic": self.pubsub.reporting_topic
            }
        
        return base_config
    
    def get_health_check_config(self) -> Dict:
        """Get health check configuration."""
        return {
            "interval": self.monitoring.health_check_interval,
            "port": self.monitoring.metrics_port,
            "endpoints": {
                "monitor": "/health/monitor",
                "analysis": "/health/analysis", 
                "alert": "/health/alert",
                "reporting": "/health/reporting"
            }
        }

# Global settings instance
settings = Settings()