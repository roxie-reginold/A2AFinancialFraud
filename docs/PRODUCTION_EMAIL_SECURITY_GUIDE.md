# Production Email Security Guide for Fraud Detection System

## 🚨 Current Issue: Why You Don't See Emails

The current AlertAgent **only logs to console and sends Pub/Sub messages** - it doesn't actually send emails. Here's why and how to fix it securely for production.

## 📊 Current Email Status

### ❌ **What's Missing:**
- AlertAgent doesn't have email sending capability integrated
- Email configuration exists but isn't used by the alert system
- No email service in the main workflow

### ✅ **What Exists:**
- Email configuration framework (`config/settings.py`)
- Email testing scripts (`tests/test_email_config.py`)
- Email setup utilities (`config/setup_email.py`)

---

## 🔧 How to Enable Emails (Secure Implementation)

### Step 1: Create Secure Email Service

```python
# services/email_service.py
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
import os
from datetime import datetime

class SecureEmailService:
    """Production-safe email service for fraud alerts."""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_APP_PASSWORD")  # App password, not regular password
        self.recipients = os.getenv("ALERT_RECIPIENTS", "").split(",")
        self.enabled = os.getenv("EMAIL_ALERTS_ENABLED", "false").lower() == "true"
        
        # Rate limiting
        self.max_emails_per_hour = int(os.getenv("MAX_EMAILS_PER_HOUR", "50"))
        self.email_count = 0
        self.last_reset = datetime.now()
        
    def send_fraud_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Send fraud alert email with rate limiting and security."""
        if not self.enabled or not self._validate_config():
            return False
            
        if not self._check_rate_limit():
            logging.warning("Email rate limit exceeded")
            return False
            
        try:
            message = self._create_alert_email(alert_data)
            self._send_email(message)
            self.email_count += 1
            return True
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return False
    
    def _validate_config(self) -> bool:
        """Validate email configuration."""
        return all([
            self.sender_email,
            self.sender_password,
            self.recipients,
            self.smtp_server
        ])
    
    def _check_rate_limit(self) -> bool:
        """Check email rate limiting."""
        now = datetime.now()
        if (now - self.last_reset).seconds > 3600:  # Reset hourly
            self.email_count = 0
            self.last_reset = now
        return self.email_count < self.max_emails_per_hour
```

### Step 2: Update AlertAgent with Email Integration

```python
# In alert_agent.py, add:
from services.email_service import SecureEmailService

class AlertAgent:
    def __init__(self):
        # ... existing init code ...
        self.email_service = SecureEmailService()
    
    async def _send_high_priority_alert(self, alert_data: Dict[str, Any]) -> None:
        """Send high-priority alert notifications."""
        # Existing console/pubsub code...
        
        # Add email notification
        if alert_data.get('risk_score', 0) >= 0.8:  # High risk threshold
            email_sent = self.email_service.send_fraud_alert(alert_data)
            if email_sent:
                logger.info(f"📧 Email alert sent for {alert_data['alert_id']}")
            else:
                logger.warning(f"📧 Email alert failed for {alert_data['alert_id']}")
```

---

## 🔒 Production Security Best Practices

### 1. **Environment Variables (Never Hardcode Credentials)**

```bash
# .env.production (NEVER commit to Git)
EMAIL_ALERTS_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=fraud-alerts@yourcompany.com
SENDER_APP_PASSWORD=your-16-char-app-password
ALERT_RECIPIENTS=security-team@yourcompany.com,fraud-team@yourcompany.com
MAX_EMAILS_PER_HOUR=100
```

### 2. **Use App Passwords (Never Regular Passwords)**

#### Gmail Setup:
1. Enable 2-Factor Authentication
2. Go to: Google Account → Security → 2-Step Verification → App passwords
3. Generate password for "Mail" application
4. Use the 16-character app password

#### Corporate Email:
- Use OAuth2 instead of passwords when possible
- Implement service accounts for automated systems
- Use encrypted credential stores (Azure Key Vault, AWS Secrets Manager)

### 3. **Rate Limiting and Throttling**

```python
class EmailRateLimiter:
    """Prevent email spam and API abuse."""
    
    def __init__(self):
        self.max_per_minute = 10
        self.max_per_hour = 100
        self.max_per_day = 500
        self.cooldown_high_priority = 300  # 5 minutes between HIGH alerts
        
    def can_send_alert(self, priority: str, alert_id: str) -> bool:
        """Check if alert can be sent based on rate limits."""
        # Implement sophisticated rate limiting logic
        pass
```

### 4. **Email Content Security**

```python
def create_secure_alert_email(alert_data: Dict[str, Any]) -> MIMEMultipart:
    """Create secure email with proper formatting."""
    
    # Sanitize all inputs
    safe_data = {
        key: html.escape(str(value)) if isinstance(value, str) else value
        for key, value in alert_data.items()
    }
    
    # Use templates to prevent injection
    template = """
    🚨 FRAUD ALERT - {priority} Priority
    
    Alert ID: {alert_id}
    Transaction: {transaction_id}
    Risk Score: {risk_score:.3f}
    Amount: ${amount:,.2f}
    
    Time: {timestamp}
    
    FRAUD INDICATORS:
    {fraud_indicators}
    
    IMMEDIATE ACTIONS REQUIRED:
    {recommendations}
    
    ---
    Automated Fraud Detection System
    """
    
    return format_email_safely(template, safe_data)
```

### 5. **Monitoring and Alerting**

```python
class EmailMonitoring:
    """Monitor email delivery and health."""
    
    def track_email_metrics(self):
        """Track email delivery metrics."""
        metrics = {
            "emails_sent_today": self.get_daily_count(),
            "delivery_success_rate": self.get_success_rate(),
            "bounce_rate": self.get_bounce_rate(),
            "rate_limit_hits": self.get_rate_limit_violations()
        }
        return metrics
    
    def alert_on_delivery_failure(self):
        """Alert if email delivery is failing."""
        if self.get_success_rate() < 0.9:  # Less than 90% success
            # Send alert via alternative channel (Slack, SMS, etc.)
            pass
```

---

## 🏭 Production Deployment Architecture

### Option 1: Direct SMTP (Simple)
```
AlertAgent → SecureEmailService → SMTP Server → Recipients
```

**Pros:** Simple, direct control
**Cons:** Reliability concerns, rate limiting challenges

### Option 2: Email Service Provider (Recommended)
```
AlertAgent → SendGrid/AWS SES/Mailgun → Recipients
```

**Pros:** Better deliverability, built-in rate limiting, analytics
**Cons:** Additional service dependency, cost

### Option 3: Message Queue (Enterprise)
```
AlertAgent → Message Queue → Email Worker → Email Service → Recipients
```

**Pros:** Reliability, scalability, retry logic
**Cons:** More complex infrastructure

---

## ⚙️ Configuration Management

### Development Environment
```bash
# .env.development
EMAIL_ALERTS_ENABLED=false  # Disable in dev
EMAIL_DEBUG_MODE=true       # Log instead of send
```

### Staging Environment
```bash
# .env.staging
EMAIL_ALERTS_ENABLED=true
ALERT_RECIPIENTS=dev-team@company.com  # Internal recipients only
MAX_EMAILS_PER_HOUR=10                 # Lower limits
```

### Production Environment
```bash
# .env.production
EMAIL_ALERTS_ENABLED=true
ALERT_RECIPIENTS=security@company.com,fraud@company.com,soc@company.com
MAX_EMAILS_PER_HOUR=100
EMAIL_ENCRYPTION=true
EMAIL_SIGNING=true
```

---

## 🔍 Testing and Validation

### 1. Email Configuration Test
```bash
python config/setup_email.py          # Interactive setup
python tests/test_email_config.py     # Test configuration
```

### 2. Integration Test
```bash
python tests/test_alert_integration.py  # Test full alert → email flow
```

### 3. Load Testing
```bash
python tests/test_email_load.py       # Test rate limiting
```

---

## 🚨 Security Considerations

### 1. **Credential Security**
- ✅ Use app passwords, not account passwords
- ✅ Store credentials in secure environment variables
- ✅ Use credential rotation policies
- ❌ Never commit credentials to code repositories
- ❌ Never log credentials or email content

### 2. **Email Content Security**
- ✅ Sanitize all dynamic content
- ✅ Use email templates
- ✅ Implement content filtering
- ❌ Don't include sensitive customer data
- ❌ Don't use HTML from untrusted sources

### 3. **Access Control**
- ✅ Limit recipient lists to authorized personnel
- ✅ Implement role-based email routing
- ✅ Log all email sending activities
- ❌ Don't send alerts to external email addresses
- ❌ Don't allow user-controlled recipient lists

### 4. **Compliance**
- ✅ Follow data protection regulations (GDPR, CCPA)
- ✅ Implement email retention policies
- ✅ Ensure audit trail for all alerts
- ✅ Encrypt emails in transit and at rest

---

## 📋 Production Checklist

### Pre-Deployment
- [ ] Email service configured with app passwords
- [ ] Environment variables properly set
- [ ] Rate limiting configured
- [ ] Email templates tested
- [ ] Recipient lists validated
- [ ] Monitoring and alerting setup
- [ ] Security review completed

### Post-Deployment
- [ ] Send test alerts to verify delivery
- [ ] Monitor email delivery metrics
- [ ] Verify rate limiting is working
- [ ] Check spam folder delivery
- [ ] Validate alert content formatting
- [ ] Test emergency escalation procedures

### Ongoing Maintenance
- [ ] Regular credential rotation
- [ ] Monitor delivery success rates
- [ ] Review and update recipient lists
- [ ] Audit email content for sensitive data
- [ ] Update rate limits based on volume
- [ ] Test backup notification channels

---

## 🛠️ Quick Implementation Guide

### 1. Enable Emails in Current System
```bash
# Create the email service
touch services/email_service.py

# Set environment variables
export EMAIL_ALERTS_ENABLED=true
export SENDER_EMAIL=your-email@company.com
export SENDER_APP_PASSWORD=your-app-password
export ALERT_RECIPIENTS=security@company.com

# Test configuration
python tests/test_email_config.py

# Update alert agent to use email service
# (Add email integration to alert_agent.py)
```

### 2. Verify Email Flow
```bash
# Run a test transaction that should trigger alerts
python main.py

# Check logs for email delivery
tail -f logs/fraud_detection.log | grep "Email"

# Verify recipient inboxes
```

### 3. Monitor Production
```bash
# Check email metrics
curl http://localhost:8080/metrics | grep email

# View email delivery dashboard
# (Implement email dashboard in health service)
```

---

## 🎯 Summary

**Why you don't see emails:**
1. AlertAgent only logs and sends Pub/Sub messages
2. Email functionality exists but isn't integrated
3. Email service needs to be created and connected

**To enable secure production emails:**
1. Implement SecureEmailService with proper security
2. Integrate email service into AlertAgent  
3. Configure environment variables securely
4. Set up monitoring and rate limiting
5. Test thoroughly before production deployment

The fraud detection system is designed to be secure and production-ready, but the email component needs to be properly implemented and configured following the security guidelines above.