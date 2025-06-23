#!/usr/bin/env python3
"""
Alert Agent for ADK Financial Fraud Detection System

This agent handles real-time alerting for fraud detection notifications.
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ADK imports
from google.adk.agents import Agent
from google.cloud import pubsub_v1

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertAgent:
    """
    Real-time alert agent for fraud detection notifications.
    
    This agent provides:
    - Real-time notifications for high-risk transactions
    - Multiple notification channels (console, Pub/Sub)
    - Alert severity classification and routing
    - Alert tracking and statistics
    """
    
    def __init__(self):
        """Initialize the AlertAgent."""
        # Create ADK agent
        self.agent = Agent(
            name="fraud_alert_agent",
            model="gemini-2.5-pro-preview-05-06",
            instruction="""You are a fraud detection alert system. Your role is to:
            
            1. Process high-risk transaction alerts
            2. Classify alert severity and urgency
            3. Route alerts to appropriate channels
            4. Track alert acknowledgments and responses
            5. Escalate unacknowledged critical alerts
            
            Always prioritize immediate notification for high-risk fraud cases.""",
            description="Real-time alerting system for fraud detection"
        )
        
        # Initialize Pub/Sub
        self._publisher = pubsub_v1.PublisherClient()
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "fraud-detection-adkhackathon")
        self._alert_topic_path = self._publisher.topic_path(project_id, "fraud-alerts")
        
        # Email configuration
        self._email_enabled = os.getenv("ENABLE_EMAIL_ALERTS", "false").lower() == "true"
        self._email_sender = os.getenv("ALERT_EMAIL_SENDER")
        self._email_password = os.getenv("ALERT_EMAIL_PASSWORD")
        self._email_recipients = os.getenv("ALERT_EMAIL_RECIPIENTS", "").split(",")
        self._smtp_server = os.getenv("ALERT_SMTP_SERVER", "smtp.gmail.com")
        self._smtp_port = int(os.getenv("ALERT_SMTP_PORT", "587"))
        
        # Alert statistics
        self._processed_alerts = 0
        self._high_risk_alerts = 0
        self._medium_risk_alerts = 0
        self._low_risk_alerts = 0
        
        logger.info("AlertAgent initialized")
    
    async def process_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a fraud detection alert.
        
        Args:
            alert_data: Alert data containing transaction and risk information
            
        Returns:
            Alert processing result
        """
        try:
            self._processed_alerts += 1
            
            # Determine alert severity
            severity = self._determine_alert_severity(alert_data)
            
            # Add alert metadata
            alert_data.update({
                "alert_severity": severity,
                "alert_timestamp": datetime.utcnow().isoformat(),
                "alert_id": alert_data.get("alert_id", f"alert_{self._processed_alerts}"),
                "processed_by": "AlertAgent"
            })
            
            # Send notifications based on severity
            if severity == "HIGH":
                self._high_risk_alerts += 1
                await self._send_high_priority_alert(alert_data)
            elif severity == "MEDIUM":
                self._medium_risk_alerts += 1
                await self._send_medium_priority_alert(alert_data)
            else:
                self._low_risk_alerts += 1
                await self._send_low_priority_alert(alert_data)
            
            logger.info(f"🚨 Processed {severity} severity alert: {alert_data['alert_id']}")
            
            return {
                "status": "alert_processed",
                "alert_id": alert_data["alert_id"],
                "severity": severity,
                "notifications_sent": True,
                "timestamp": alert_data["alert_timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error processing alert: {str(e)}")
            return {
                "status": "alert_error",
                "error": str(e),
                "alert_id": alert_data.get("alert_id", "unknown")
            }
    
    def _determine_alert_severity(self, alert_data: Dict[str, Any]) -> str:
        """Determine alert severity based on risk score and amount."""
        risk_score = alert_data.get("risk_score", 0)
        amount = alert_data.get("amount", 0)
        
        if risk_score >= 0.9 or amount >= 10000:
            return "HIGH"
        elif risk_score >= 0.7 or amount >= 1000:
            return "MEDIUM"
        return "LOW"
    
    async def _send_high_priority_alert(self, alert_data: Dict[str, Any]) -> None:
        """Send high-priority alert notifications."""
        # Console notification
        logger.critical(f"🔴 HIGH PRIORITY FRAUD ALERT: {alert_data['alert_id']}")
        logger.critical(f"   Transaction: {alert_data.get('transaction_id', 'unknown')}")
        logger.critical(f"   Risk Score: {alert_data.get('risk_score', 0):.3f}")
        logger.critical(f"   Amount: ${alert_data.get('amount', 0):,.2f}")
        logger.critical(f"   Summary: {alert_data.get('analysis_summary', 'No summary available')}")
        
        # Email notification
        if self._email_enabled:
            await self._send_email_alert(alert_data, "HIGH")
        
        # Pub/Sub notification
        await self._send_pubsub_notification(alert_data, "HIGH")
        
        logger.info(f"✅ High priority notifications sent for {alert_data['alert_id']}")
    
    async def _send_medium_priority_alert(self, alert_data: Dict[str, Any]) -> None:
        """Send medium-priority alert notifications."""
        # Console notification
        logger.warning(f"🟡 MEDIUM PRIORITY FRAUD ALERT: {alert_data['alert_id']}")
        logger.warning(f"   Transaction: {alert_data.get('transaction_id', 'unknown')}")
        logger.warning(f"   Risk Score: {alert_data.get('risk_score', 0):.3f}")
        logger.warning(f"   Amount: ${alert_data.get('amount', 0):,.2f}")
        
        # Email notification
        if self._email_enabled:
            await self._send_email_alert(alert_data, "MEDIUM")
        
        # Pub/Sub notification
        await self._send_pubsub_notification(alert_data, "MEDIUM")
        
        logger.info(f"✅ Medium priority notifications sent for {alert_data['alert_id']}")
    
    async def _send_low_priority_alert(self, alert_data: Dict[str, Any]) -> None:
        """Send low-priority alert notifications."""
        # Console notification
        logger.info(f"🟢 LOW PRIORITY FRAUD ALERT: {alert_data['alert_id']}")
        logger.info(f"   Transaction: {alert_data.get('transaction_id', 'unknown')}")
        logger.info(f"   Risk Score: {alert_data.get('risk_score', 0):.3f}")
        
        # Pub/Sub notification (optional for low priority)
        await self._send_pubsub_notification(alert_data, "LOW")
        
        logger.info(f"✅ Low priority notifications sent for {alert_data['alert_id']}")
    
    async def _send_pubsub_notification(self, alert_data: Dict[str, Any], priority: str) -> None:
        """Send alert notification to Pub/Sub topic."""
        try:
            notification_data = {
                "alert_type": "FRAUD_DETECTION_ALERT",
                "priority": priority,
                "alert_id": alert_data["alert_id"],
                "transaction_id": alert_data.get("transaction_id"),
                "risk_score": alert_data.get("risk_score"),
                "amount": alert_data.get("amount"),
                "fraud_indicators": alert_data.get("fraud_indicators", []),
                "recommendations": alert_data.get("recommendations", []),
                "analysis_summary": alert_data.get("analysis_summary"),
                "timestamp": alert_data["alert_timestamp"],
                "analysis_method": alert_data.get("analysis_method", "unknown")
            }
            
            message_data = json.dumps(notification_data).encode('utf-8')
            self._publisher.publish(self._alert_topic_path, data=message_data)
            
            logger.debug(f"📡 Published {priority} alert to Pub/Sub: {alert_data['alert_id']}")
            
        except Exception as e:
            logger.error(f"Error publishing alert to Pub/Sub: {str(e)}")
    
    async def _send_email_alert(self, alert_data: Dict[str, Any], priority: str) -> None:
        """Send email alert notification using exact same logic as working test."""
        if not self._email_enabled or not self._email_sender or not self._email_password:
            logger.warning("Email alerts not configured properly")
            return
            
        try:
            # Use the exact same logic as the working test_email_config.py
            sender_email = self._email_sender
            sender_password = self._email_password
            recipients = [r.strip() for r in self._email_recipients if r.strip()]
            smtp_server = self._smtp_server
            smtp_port = self._smtp_port
            
            # Create email message (exact same as test)
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = f"🚨 FRAUD ALERT - {priority} Priority - Transaction {alert_data.get('transaction_id', 'unknown')}"
            
            # Clean, professional email body
            body = f"""FRAUD DETECTION ALERT

⚠️  {priority} PRIORITY TRANSACTION DETECTED

TRANSACTION DETAILS:
• Alert ID: {alert_data.get('alert_id', 'unknown')}
• Transaction ID: {alert_data.get('transaction_id', 'unknown')}
• Amount: ${alert_data.get('amount', 0):,.2f}
• Risk Score: {alert_data.get('risk_score', 0):.1%}
• Timestamp: {alert_data.get('alert_timestamp', 'unknown')}

ANALYSIS SUMMARY:
{alert_data.get('analysis_summary', 'Suspicious transaction detected requiring immediate attention.')}

FRAUD INDICATORS:
{chr(10).join(f"• {indicator}" for indicator in alert_data.get('fraud_indicators', ['High risk transaction']))}

RECOMMENDED ACTIONS:
{chr(10).join(f"• {rec}" for rec in alert_data.get('recommendations', ['Review transaction immediately']))}

This is an automated alert from the Financial Fraud Detection System.
Please review this transaction immediately and take appropriate action.

---
Automated Alert System
Time: {alert_data.get('alert_timestamp', 'unknown')}
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, recipients, text)
            server.quit()
            
            logger.info(f"📧 Email alert sent for {alert_data.get('alert_id', 'unknown')} to {len(recipients)} recipients")
            
        except Exception as e:
            logger.error(f"Error sending email alert: {str(e)}")
            logger.error(f"Email config - Sender: {self._email_sender}, Recipients: {self._email_recipients}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get alert processing statistics."""
        return {
            "total_alerts_processed": self._processed_alerts,
            "high_risk_alerts": self._high_risk_alerts,
            "medium_risk_alerts": self._medium_risk_alerts,
            "low_risk_alerts": self._low_risk_alerts,
            "high_risk_percentage": (self._high_risk_alerts / self._processed_alerts * 100) if self._processed_alerts > 0 else 0,
            "alert_distribution": {
                "HIGH": self._high_risk_alerts,
                "MEDIUM": self._medium_risk_alerts,
                "LOW": self._low_risk_alerts
            }
        }

async def main():
    """Test the alert agent."""
    alert_agent = AlertAgent()
    
    # Test alerts with different severities
    test_alerts = [
        {
            "alert_id": "test_high_001",
            "transaction_id": "tx_high_001",
            "risk_score": 0.95,
            "amount": 15000.00,
            "analysis_summary": "Multiple fraud indicators detected",
            "fraud_indicators": ["Unusual amount", "Suspicious timing", "Location anomaly"],
            "recommendations": ["Block transaction", "Contact customer immediately"]
        },
        {
            "alert_id": "test_medium_001",
            "transaction_id": "tx_medium_001",
            "risk_score": 0.75,
            "amount": 2500.00,
            "analysis_summary": "Moderate risk patterns identified",
            "fraud_indicators": ["Elevated amount"],
            "recommendations": ["Additional verification recommended"]
        },
        {
            "alert_id": "test_low_001",
            "transaction_id": "tx_low_001",
            "risk_score": 0.3,
            "amount": 150.00,
            "analysis_summary": "Low risk transaction",
            "fraud_indicators": ["Standard patterns"],
            "recommendations": ["Normal processing"]
        }
    ]
    
    # Process test alerts
    for alert in test_alerts:
        result = await alert_agent.process_alert(alert)
        logger.info(f"Alert processing result: {result}")
    
    # Print statistics
    stats = alert_agent.get_statistics()
    logger.info(f"Alert statistics: {json.dumps(stats, indent=2)}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Alert agent test interrupted")
    except Exception as e:
        logger.error(f"Error running alert agent test: {str(e)}")
        raise