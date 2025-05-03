import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import re
import configparser
import logging
from pathlib import Path
import sys
import getpass

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('SecureMailer')

# Config file location
CONFIG_FILE = 'email_config.ini'

def create_default_config():
    """Create a default config file if it doesn't exist"""
    config = configparser.ConfigParser()
    config['EMAIL'] = {
        'SENDER_EMAIL': 'youremail@example.com',
        'SMTP_SERVER': 'smtp.gmail.com',
        'SMTP_PORT': '587'
    }
    
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    logger.info(f"Created default config file at {CONFIG_FILE}")
    logger.info("Please update the config file with your email settings")

def load_config():
    """Load configuration from file"""
    if not os.path.exists(CONFIG_FILE):
        create_default_config()
        logger.info("Please edit the config file with your email settings and run the script again.")
        sys.exit(1)
        
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    
    # Verify required config settings exist
    required_keys = ['SENDER_EMAIL', 'SMTP_SERVER', 'SMTP_PORT']
    for key in required_keys:
        if key not in config['EMAIL']:
            logger.error(f"Missing required configuration: {key}")
            logger.info("Please check your config file and add all required settings.")
            sys.exit(1)
    
    return {
        'sender_email': config['EMAIL']['SENDER_EMAIL'],
        'smtp_server': config['EMAIL']['SMTP_SERVER'],
        'smtp_port': int(config['EMAIL']['SMTP_PORT']),
    }

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def send_email(sender_email, password, receiver_email, subject, body, attachment_paths=None, cc=None, bcc=None):
    """
    Send email with improved error handling and security
    
    Args:
        sender_email (str): Sender's email address
        password (str): Sender's email password or app password
        receiver_email (str or list): Recipient email address(es)
        subject (str): Email subject
        body (str): Email body text
        attachment_paths (list, optional): List of file paths to attach
        cc (str or list, optional): CC recipients
        bcc (str or list, optional): BCC recipients
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Validate email addresses
    if not is_valid_email(sender_email):
        logger.error(f"Invalid sender email format: {sender_email}")
        return False
    
    # Convert single receiver to list for consistency
    if isinstance(receiver_email, str):
        receiver_email = [receiver_email]
    
    # Validate all receiver emails
    for email in receiver_email:
        if not is_valid_email(email):
            logger.error(f"Invalid receiver email format: {email}")
            return False
    
    try:
        # Load configuration
        config = load_config()
        
        # Set up the MIME
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ', '.join(receiver_email)
        msg['Subject'] = subject
        
        # Add CC if provided
        all_recipients = receiver_email.copy()
        if cc:
            if isinstance(cc, str):
                cc = [cc]
            msg['Cc'] = ', '.join(cc)
            all_recipients.extend(cc)
        
        # Add BCC if provided (only to recipients list, not in headers)
        if bcc:
            if isinstance(bcc, str):
                bcc = [bcc]
            all_recipients.extend(bcc)
        
        # Attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))
        
        # Attachments
        if attachment_paths:
            if isinstance(attachment_paths, str):
                attachment_paths = [attachment_paths]
                
            for attachment_path in attachment_paths:
                # Convert to Path object for better path handling
                path = Path(attachment_path)
                
                if not path.exists():
                    logger.warning(f"Attachment not found: {attachment_path}")
                    continue
                    
                try:
                    with open(path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        
                    encoders.encode_base64(part)
                    
                    # Add header to attachment based on file type
                    filename = path.name
                    content_type = "application/octet-stream"
                    
                    # Try to guess content type based on file extension
                    if path.suffix.lower() in ['.pdf']:
                        content_type = "application/pdf"
                    elif path.suffix.lower() in ['.jpg', '.jpeg']:
                        content_type = "image/jpeg"
                    elif path.suffix.lower() in ['.png']:
                        content_type = "image/png"
                    elif path.suffix.lower() in ['.txt']:
                        content_type = "text/plain"
                    elif path.suffix.lower() in ['.html', '.htm']:
                        content_type = "text/html"
                    elif path.suffix.lower() in ['.doc', '.docx']:
                        content_type = "application/msword"
                    elif path.suffix.lower() in ['.xls', '.xlsx']:
                        content_type = "application/vnd.ms-excel"
                    elif path.suffix.lower() in ['.zip']:
                        content_type = "application/zip"
                        
                    part.add_header(
                        'Content-Disposition', 
                        f'attachment; filename="{filename}"'
                    )
                    part.add_header('Content-Type', content_type)
                    msg.attach(part)
                    logger.info(f"Attached file: {path.name}")
                except Exception as e:
                    logger.error(f"Failed to attach {path}: {str(e)}")
        
        # Connect to the server and send the email
        logger.info(f"Connecting to {config['smtp_server']}:{config['smtp_port']}...")
        try:
            with smtplib.SMTP(config['smtp_server'], config['smtp_port'], timeout=30) as server:
                server.starttls()  # Enable security
                server.login(sender_email, password)
                
                text = msg.as_string()
                server.sendmail(sender_email, all_recipients, text)
                
            logger.info("Email sent successfully!")
            return True
        except smtplib.SMTPAuthenticationError:
            logger.error("Authentication failed. Please check your email and password.")
            logger.info("For Gmail users: You may need to use an App Password. "
                       "See https://support.google.com/accounts/answer/185833")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send email. Error: {str(e)}")
        return False

def main():
    """Main function for running the script directly"""
    print("📧 SecureMailer - Email Sending Utility 🔐")
    print("------------------------------------------")
    
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        return
    
    # Get email details
    sender_email = config['sender_email']
    print(f"Sender email: {sender_email}")
    
    # Get recipient email(s)
    while True:
        receiver_email = input("Enter recipient email address(es) (comma-separated): ")
        receiver_list = [email.strip() for email in receiver_email.split(',')]
        valid = True
        for email in receiver_list:
            if not is_valid_email(email):
                logger.error(f"Invalid email format: {email}")
                valid = False
        if valid:
            break
        print("Please enter valid email address(es)")
    
    # Get CC (optional)
    cc_list = []
    cc_input = input("Enter CC email address(es) (comma-separated, or press Enter to skip): ")
    if cc_input.strip():
        cc_list = [email.strip() for email in cc_input.split(',')]
        for email in cc_list:
            if not is_valid_email(email):
                logger.warning(f"Invalid CC email format: {email} - will be skipped")
                cc_list.remove(email)
    
    # Get BCC (optional)
    bcc_list = []
    bcc_input = input("Enter BCC email address(es) (comma-separated, or press Enter to skip): ")
    if bcc_input.strip():
        bcc_list = [email.strip() for email in bcc_input.split(',')]
        for email in bcc_list:
            if not is_valid_email(email):
                logger.warning(f"Invalid BCC email format: {email} - will be skipped")
                bcc_list.remove(email)
    
    # Get subject
    subject = input("Enter email subject: ")
    
    # Get body with multi-line support
    print("Enter email body (press Enter twice when done):")
    body = []
    while True:
        line = input()
        if not line and not body:
            # Don't end on first empty line if body is empty
            continue
        if not line and body and body[-1] == "":
            # End on second consecutive empty line
            break
        body.append(line)
    body_text = "\n".join(body)
    
    # Ask for attachments
    attachments = []
    print("Enter attachment paths (or press Enter to skip/finish):")
    while True:
        attachment = input("> ")
        if not attachment:
            break
        path = Path(attachment)
        if not path.exists():
            logger.warning(f"File not found: {attachment}")
            continue
        attachments.append(str(path))
        logger.info(f"Added attachment: {path.name}")
    
    # Get password securely
    password = getpass.getpass("Enter your email password (input will be hidden): ")
    
    # Send the email
    success = send_email(
        sender_email=sender_email,
        password=password,
        receiver_email=receiver_list,
        subject=subject,
        body=body_text,
        attachment_paths=attachments if attachments else None,
        cc=cc_list if cc_list else None,
        bcc=bcc_list if bcc_list else None
    )
    
    if success:
        logger.info("Email sent successfully!")
    else:
        logger.error("Failed to send email. Please check the errors above.")

if __name__ == "__main__":
    main()
