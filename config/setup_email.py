#!/usr/bin/env python3
"""
Interactive email setup script for the Alert Agent.
"""

import os
import getpass

def setup_email_configuration():
    """Interactive setup for email configuration."""
    
    print("📧 FRAUD ALERT EMAIL SETUP")
    print("=" * 50)
    
    # Get email provider choice
    print("\n1. Choose your email provider:")
    print("   1) Gmail (recommended)")
    print("   2) Outlook/Hotmail")
    print("   3) Custom SMTP server")
    
    while True:
        choice = input("\nEnter choice (1-3): ").strip()
        if choice in ['1', '2', '3']:
            break
        print("Please enter 1, 2, or 3")
    
    # Get sender email
    sender_email = input("\nEnter your email address: ").strip()
    
    # Get password
    print("\n⚠️  For Gmail: Use App Password (not your regular password)")
    print("   Go to: Google Account → Security → 2-Step Verification → App passwords")
    sender_password = getpass.getpass("Enter your email password/app password: ")
    
    # Get recipients
    print("\nEnter recipient email addresses (comma-separated):")
    recipients = input("Recipients: ").strip()
    if not recipients:
        recipients = sender_email
        print(f"Using sender email as recipient: {sender_email}")
    
    # Set SMTP settings based on provider
    if choice == '1':  # Gmail
        smtp_server = "smtp.gmail.com"
        smtp_port = "587"
    elif choice == '2':  # Outlook
        smtp_server = "smtp-mail.outlook.com"
        smtp_port = "587"
    else:  # Custom
        smtp_server = input("Enter SMTP server: ").strip()
        smtp_port = input("Enter SMTP port (usually 587): ").strip() or "587"
    
    # Create .env file
    env_content = f"""# Email Configuration for Fraud Alert System
# Generated on {os.popen('date').read().strip()}

# Email sender configuration
ALERT_EMAIL_SENDER={sender_email}
ALERT_EMAIL_PASSWORD={sender_password}

# Email recipients (comma-separated)
ALERT_EMAIL_RECIPIENTS={recipients}

# SMTP server configuration
ALERT_SMTP_SERVER={smtp_server}
ALERT_SMTP_PORT={smtp_port}

# Optional: Enable debug mode
ALERT_EMAIL_DEBUG=false
"""
    
    # Write .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ Email configuration saved to .env file")
    
    # Test configuration
    print("\n🧪 Testing email configuration...")
    
    # Set environment variables for immediate testing
    os.environ['ALERT_EMAIL_SENDER'] = sender_email
    os.environ['ALERT_EMAIL_PASSWORD'] = sender_password
    os.environ['ALERT_EMAIL_RECIPIENTS'] = recipients
    os.environ['ALERT_SMTP_SERVER'] = smtp_server
    os.environ['ALERT_SMTP_PORT'] = smtp_port
    
    # Import and run test
    try:
        from test_email_config import test_email_configuration
        success = test_email_configuration()
        
        if success:
            print("\n🎉 Email setup completed successfully!")
            print("📧 Check your inbox for the test alert email.")
            print("\n📋 Next steps:")
            print("   1. Run the Alert Agent: python alert_agent.py")
            print("   2. Process fraud alerts with: python test_alert_agent.py")
        else:
            print("\n❌ Email test failed. Please check your configuration.")
            
    except Exception as e:
        print(f"\n❌ Error testing email: {str(e)}")
        print("💡 You can manually test with: python test_email_config.py")
    
    print(f"\n📁 Configuration saved in: {os.path.abspath('.env')}")
    print("🔒 Keep your .env file secure and don't commit it to Git!")

if __name__ == "__main__":
    try:
        setup_email_configuration()
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Setup error: {str(e)}")
        print("💡 For manual setup, see EMAIL_SETUP_GUIDE.md")
