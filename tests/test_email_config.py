#!/usr/bin/env python3
"""
Email configuration test script for the Alert Agent.
"""

import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email_configuration():
    """Test email configuration and send a test alert."""
    
    logger.info("🧪 Testing Email Configuration for Alert Agent...")
    
    # Step 1: Check environment variables
    logger.info("📋 Checking environment variables...")
    
    sender_email = os.getenv("ALERT_EMAIL_SENDER")
    sender_password = os.getenv("ALERT_EMAIL_PASSWORD")
    recipients = os.getenv("ALERT_EMAIL_RECIPIENTS", "").split(",")
    smtp_server = os.getenv("ALERT_SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("ALERT_SMTP_PORT", "587"))
    
    if not sender_email:
        logger.error("❌ ALERT_EMAIL_SENDER not set. Please set your email address.")
        logger.info("   Example: export ALERT_EMAIL_SENDER='your-email@gmail.com'")
        return False
    
    if not sender_password:
        logger.error("❌ ALERT_EMAIL_PASSWORD not set. Please set your app password.")
        logger.info("   Example: export ALERT_EMAIL_PASSWORD='your-16-char-app-password'")
        return False
    
    if not recipients or recipients == [""]:
        logger.warning("⚠️  ALERT_EMAIL_RECIPIENTS not set. Using sender email as recipient.")
        recipients = [sender_email]
    
    logger.info(f"✅ Sender: {sender_email}")
    logger.info(f"✅ Recipients: {recipients}")
    logger.info(f"✅ SMTP Server: {smtp_server}:{smtp_port}")
    
    # Step 2: Test SMTP connection
    logger.info("🔌 Testing SMTP connection...")
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        logger.info("✅ SMTP connection successful!")
        server.quit()
    except Exception as e:
        logger.error(f"❌ SMTP connection failed: {str(e)}")
        logger.info("💡 Troubleshooting tips:")
        logger.info("   - Check if 2FA is enabled and you're using an app password")
        logger.info("   - Verify email and password are correct")
        logger.info("   - Check SMTP server and port settings")
        return False
    
    # Step 3: Send test email
    logger.info("📧 Sending test fraud alert email...")
    
    try:
        # Create test alert data
        test_alert = {
            "alert_id": f"TEST_ALERT_{int(datetime.now().timestamp())}",
            "transaction_id": "TEST_TXN_001",
            "priority": "HIGH",
            "urgency": "IMMEDIATE",
            "risk_score": 0.95,
            "amount": 5000.0,
            "analysis_method": "test",
            "alert_timestamp": datetime.now().isoformat(),
            "fraud_indicators": [
                "This is a test alert",
                "Email configuration verification",
                "System integration test"
            ],
            "recommendations": [
                "Verify email notifications are working",
                "Check alert formatting",
                "Confirm recipient delivery"
            ],
            "analysis_summary": "Test alert to verify email notification system is working correctly"
        }
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = f"🧪 TEST FRAUD ALERT - {test_alert['priority']} Priority - Transaction {test_alert['transaction_id']}"
        
        # Email body
        body = f"""
🧪 FRAUD DETECTION SYSTEM - TEST ALERT 🧪

This is a test email to verify your fraud alert notifications are working correctly.

ALERT DETAILS:
Alert ID: {test_alert['alert_id']}
Transaction ID: {test_alert['transaction_id']}
Priority: {test_alert['priority']} ({test_alert['urgency']})
Risk Score: {test_alert['risk_score']:.3f}
Amount: ${test_alert['amount']:.2f}
Analysis Method: {test_alert['analysis_method']}
Timestamp: {test_alert['alert_timestamp']}

ANALYSIS SUMMARY:
{test_alert['analysis_summary']}

FRAUD INDICATORS:
{chr(10).join(f"• {indicator}" for indicator in test_alert['fraud_indicators'])}

RECOMMENDATIONS:
{chr(10).join(f"• {rec}" for rec in test_alert['recommendations'])}

✅ If you received this email, your fraud alert notifications are working correctly!

---
Fraud Detection System - Email Configuration Test
Sent from: {sender_email}
Recipients: {', '.join(recipients)}
SMTP Server: {smtp_server}:{smtp_port}
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipients, text)
        server.quit()
        
        logger.info("✅ Test email sent successfully!")
        logger.info(f"📧 Check your inbox at: {', '.join(recipients)}")
        
    except Exception as e:
        logger.error(f"❌ Failed to send test email: {str(e)}")
        return False
    
    # Step 4: Configuration summary
    logger.info("📊 Email Configuration Summary:")
    logger.info(f"   Sender: {sender_email}")
    logger.info(f"   Recipients: {len(recipients)} configured")
    logger.info(f"   SMTP: {smtp_server}:{smtp_port}")
    logger.info(f"   Status: ✅ WORKING")
    
    logger.info("🎉 Email configuration test completed successfully!")
    logger.info("💡 Next steps:")
    logger.info("   1. Check your email inbox for the test alert")
    logger.info("   2. Run the Alert Agent to process real fraud alerts")
    logger.info("   3. Monitor email delivery for production alerts")
    
    return True

def show_setup_instructions():
    """Show setup instructions for email configuration."""
    
    print("""
📧 EMAIL SETUP INSTRUCTIONS

1. GMAIL SETUP (Recommended):
   a. Enable 2-Factor Authentication on your Gmail account
   b. Go to Google Account → Security → 2-Step Verification → App passwords
   c. Generate password for "Mail" application
   d. Set environment variables:
      
      export ALERT_EMAIL_SENDER="your-email@gmail.com"
      export ALERT_EMAIL_PASSWORD="your-16-char-app-password"
      export ALERT_EMAIL_RECIPIENTS="recipient1@company.com,recipient2@company.com"

2. OUTLOOK SETUP:
   
   export ALERT_EMAIL_SENDER="your-email@outlook.com"
   export ALERT_EMAIL_PASSWORD="your-password"
   export ALERT_SMTP_SERVER="smtp-mail.outlook.com"
   export ALERT_SMTP_PORT="587"

3. CUSTOM SMTP SETUP:
   
   export ALERT_EMAIL_SENDER="your-email@company.com"
   export ALERT_EMAIL_PASSWORD="your-password"
   export ALERT_SMTP_SERVER="mail.company.com"
   export ALERT_SMTP_PORT="587"

4. TEST CONFIGURATION:
   
   python test_email_config.py

📋 For detailed setup guide, see: EMAIL_SETUP_GUIDE.md
""")

if __name__ == "__main__":
    # Check if environment variables are set
    if not os.getenv("ALERT_EMAIL_SENDER"):
        print("⚠️  Email not configured. Showing setup instructions...\n")
        show_setup_instructions()
    else:
        # Run email configuration test
        success = test_email_configuration()
        
        if not success:
            print("\n💡 Need help? Check EMAIL_SETUP_GUIDE.md for detailed instructions.")
