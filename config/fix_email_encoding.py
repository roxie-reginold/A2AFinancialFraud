#!/usr/bin/env python3
"""
Fix email encoding issues by cleaning the .env file.
"""

import os
import re

def fix_email_encoding():
    """Fix encoding issues in email configuration."""
    
    print("🔧 FIXING EMAIL ENCODING ISSUES")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found. Please run setup_email.py first.")
        return False
    
    # Read current .env file
    print("📖 Reading current .env file...")
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Clean the content
    print("🧹 Cleaning encoding issues...")
    
    # Remove non-breaking spaces and other problematic characters
    cleaned_content = content.replace('\xa0', '')  # Remove non-breaking spaces
    cleaned_content = re.sub(r'[\u00a0\u2000-\u200f\u2028-\u202f]', '', cleaned_content)  # Remove various Unicode spaces
    
    # Extract and clean email credentials
    lines = cleaned_content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        if line.startswith('ALERT_EMAIL_SENDER='):
            email = line.split('=', 1)[1].strip()
            cleaned_email = email.replace('\xa0', ' ').strip()
            cleaned_lines.append(f'ALERT_EMAIL_SENDER={cleaned_email}')
            print(f"✅ Cleaned sender email: {cleaned_email}")
            
        elif line.startswith('ALERT_EMAIL_PASSWORD='):
            password = line.split('=', 1)[1].strip()
            # Remove all spaces and non-breaking spaces from password
            cleaned_password = password.replace('\xa0', '').replace(' ', '')
            cleaned_lines.append(f'ALERT_EMAIL_PASSWORD={cleaned_password}')
            print(f"✅ Cleaned password: {'*' * len(cleaned_password)} ({len(cleaned_password)} chars)")
            
        elif line.startswith('ALERT_EMAIL_RECIPIENTS='):
            recipients = line.split('=', 1)[1].strip()
            cleaned_recipients = recipients.replace('\xa0', ' ').strip()
            cleaned_lines.append(f'ALERT_EMAIL_RECIPIENTS={cleaned_recipients}')
            print(f"✅ Cleaned recipients: {cleaned_recipients}")
            
        else:
            cleaned_lines.append(line)
    
    # Write cleaned content back
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Backup original file
    print("💾 Creating backup of original .env file...")
    with open('.env.backup', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Write cleaned file
    print("📝 Writing cleaned .env file...")
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print("✅ Email encoding issues fixed!")
    print("📁 Original file backed up as .env.backup")
    
    return True

def test_cleaned_configuration():
    """Test the cleaned email configuration."""
    
    print("\n🧪 Testing cleaned email configuration...")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment variables")
    
    sender = os.getenv('ALERT_EMAIL_SENDER', '').strip()
    password = os.getenv('ALERT_EMAIL_PASSWORD', '').strip()
    recipients = os.getenv('ALERT_EMAIL_RECIPIENTS', '').strip()
    
    print(f"📧 Sender: {sender}")
    print(f"🔑 Password length: {len(password)} characters")
    print(f"📬 Recipients: {recipients}")
    
    # Check for problematic characters
    issues = []
    
    if '\xa0' in sender:
        issues.append("Sender email contains non-breaking spaces")
    if '\xa0' in password:
        issues.append("Password contains non-breaking spaces")
    if '\xa0' in recipients:
        issues.append("Recipients contain non-breaking spaces")
    
    if not sender:
        issues.append("Sender email is empty")
    if not password:
        issues.append("Password is empty")
    if not recipients:
        issues.append("Recipients are empty")
    
    if issues:
        print("❌ Issues found:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ Configuration looks clean!")
        return True

def main():
    """Main function."""
    
    try:
        # Fix encoding issues
        if fix_email_encoding():
            # Test the cleaned configuration
            if test_cleaned_configuration():
                print("\n🎉 Email configuration fixed successfully!")
                print("\n📋 Next steps:")
                print("   1. Test email: python test_email_config.py")
                print("   2. Test alerts: python test_alert_agent.py")
            else:
                print("\n❌ Configuration still has issues. You may need to:")
                print("   1. Regenerate your Gmail app password")
                print("   2. Run setup_email.py again")
        
    except Exception as e:
        print(f"\n❌ Error fixing email configuration: {str(e)}")
        print("💡 Try running setup_email.py to recreate the configuration")

if __name__ == "__main__":
    main()
