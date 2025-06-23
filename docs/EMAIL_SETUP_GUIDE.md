# Email Notifications Setup Guide

This guide will help you configure email notifications for the Alert Agent in your fraud detection system.

## 📧 **Email Configuration Options**

### **Option 1: Gmail (Recommended for Testing)**

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail" application
   - Copy the 16-character password

3. **Set Environment Variables**:
```bash
export ALERT_EMAIL_SENDER="your-email@gmail.com"
export ALERT_EMAIL_PASSWORD="your-16-char-app-password"
```

### **Option 2: Outlook/Hotmail**

```bash
export ALERT_EMAIL_SENDER="your-email@outlook.com"
export ALERT_EMAIL_PASSWORD="your-password"
# SMTP settings are automatically configured for Outlook
```

### **Option 3: Custom SMTP Server**

```bash
export ALERT_EMAIL_SENDER="your-email@company.com"
export ALERT_EMAIL_PASSWORD="your-password"
export ALERT_SMTP_SERVER="mail.company.com"
export ALERT_SMTP_PORT="587"
```

## 🔧 **Quick Setup Steps**

### **Step 1: Create Environment File**

Create a `.env` file in your project directory:

```bash
# Email Configuration
ALERT_EMAIL_SENDER=your-email@gmail.com
ALERT_EMAIL_PASSWORD=your-app-password
ALERT_EMAIL_RECIPIENTS=fraud-team@company.com,security@company.com

# Optional: Custom SMTP (if not using Gmail)
ALERT_SMTP_SERVER=smtp.gmail.com
ALERT_SMTP_PORT=587
```

### **Step 2: Load Environment Variables**

```bash
# In your terminal, load the environment file:
source .env

# Or export manually:
export ALERT_EMAIL_SENDER="your-email@gmail.com"
export ALERT_EMAIL_PASSWORD="your-app-password"
```

### **Step 3: Test Email Configuration**

Run the email test script:
```bash
source venv312/bin/activate
python test_email_config.py
```

## 📋 **Email Recipients Configuration**

You can configure multiple recipients in several ways:

### **Method 1: Environment Variable**
```bash
export ALERT_EMAIL_RECIPIENTS="fraud-team@company.com,security@company.com,manager@company.com"
```

### **Method 2: Configuration File**
Create `email_config.json`:
```json
{
  "recipients": {
    "high_priority": [
      "fraud-team@company.com",
      "security-manager@company.com"
    ],
    "medium_priority": [
      "fraud-team@company.com"
    ],
    "low_priority": [
      "fraud-alerts@company.com"
    ]
  }
}
```

## 🔒 **Security Best Practices**

1. **Never commit credentials to Git**:
   - Add `.env` to `.gitignore`
   - Use environment variables only

2. **Use App Passwords** (not your main password):
   - Gmail: Generate app-specific password
   - Outlook: Use app password if 2FA enabled

3. **Restrict Email Access**:
   - Use dedicated email account for alerts
   - Limit SMTP access to specific IPs if possible

## 🧪 **Testing Email Setup**

### **Test 1: Basic SMTP Connection**
```python
import smtplib
from email.mime.text import MIMEText

# Test connection
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
print("✅ SMTP connection successful!")
server.quit()
```

### **Test 2: Send Test Alert**
```bash
python test_email_config.py
```

## 🚨 **Alert Email Template**

The system sends detailed fraud alerts with:

```
Subject: 🚨 FRAUD ALERT - HIGH Priority - Transaction TXN_12345

FRAUD DETECTION ALERT

Alert ID: ALERT_TXN_12345_1234567890
Transaction ID: TXN_12345
Priority: HIGH (IMMEDIATE)
Risk Score: 0.950
Amount: $5,000.00
Analysis Method: hybrid
Timestamp: 2024-01-01T12:00:00Z

ANALYSIS SUMMARY:
Critical fraud risk detected with multiple indicators

FRAUD INDICATORS:
• Unusually high transaction amount
• Suspicious technical features
• Geographic anomaly detected

RECOMMENDATIONS:
• Block transaction immediately
• Contact customer for verification
• Conduct manual review

Please investigate this transaction immediately.

---
Fraud Detection System
```

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **"Authentication failed"**:
   - Check if 2FA is enabled and app password is used
   - Verify email/password are correct

2. **"Connection refused"**:
   - Check SMTP server and port
   - Verify firewall/network settings

3. **"Less secure app access"**:
   - Enable app passwords instead
   - Don't use "less secure apps" option

### **Debug Mode:**
Set debug logging to see detailed SMTP communication:
```bash
export ALERT_EMAIL_DEBUG=true
```

## 📊 **Email Notification Triggers**

| Priority | Risk Score | Amount | Channels |
|----------|------------|--------|----------|
| HIGH | ≥0.9 | ≥$5,000 | Email + Console + Pub/Sub + Slack |
| MEDIUM | ≥0.7 | ≥$1,000 | Email + Console + Pub/Sub |
| LOW | <0.7 | <$1,000 | Console only |

## 🚀 **Production Recommendations**

1. **Use dedicated email service**:
   - SendGrid, AWS SES, or Mailgun for high volume
   - Better deliverability and monitoring

2. **Set up email templates**:
   - HTML templates for better formatting
   - Different templates for different priorities

3. **Monitor email delivery**:
   - Track bounce rates and delivery status
   - Set up email delivery webhooks

4. **Rate limiting**:
   - Prevent email spam from too many alerts
   - Batch alerts or use digest emails

---

*Need help with setup? Check the test scripts or contact the development team.*
