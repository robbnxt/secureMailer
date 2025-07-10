# 📧 SecureMailer - Robust Email Sending Tool 🔐

A secure, feature-rich Python email sending utility that makes sending emails with attachments simple and safe.

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- 🛡️ **Enhanced Security**: No hardcoded credentials, secure password input
- 📎 **Multiple Attachments**: Send one or many files in a single email
- 👥 **CC/BCC Support**: Full recipient control with CC and BCC fields  
- ✅ **Input Validation**: Email format validation and file existence checks
- 📝 **Detailed Logging**: Clear feedback on the email sending process
- ⚙️ **Flexible Configuration**: External config file for easy customization

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/robbnxt/secureMailer.git
cd secureMailer

# Install dependencies (if you add any beyond standard library)
# pip install -r requirements.txt
```

## 🔧 Configuration

On first run, the script will create a default `email_config.ini` file. Edit it to include your details:

```ini
[EMAIL]
SENDER_EMAIL = youremail@example.com
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
```

## 🖥️ Usage

### Command Line Interface

Run the script directly to use the interactive interface:

```bash
python secure_mailer.py
```

The script will guide you through entering:
- Recipient email(s)
- Email subject
- Email body (multi-line supported)
- File attachments (optional)
- Password (securely entered, not displayed)

### As a Module

Import and use in your own Python scripts:

```python
from secure_mailer import send_email

success = send_email(
    sender_email="your@email.com",
    password="your_secure_password",  # Consider using environment variables
    receiver_email=["recipient@example.com"],
    subject="Important Update",
    body="Hello, please find the attached documents.",
    attachment_paths=["document1.pdf", "document2.xlsx"],
    cc="manager@example.com",
    bcc=["archive@company.com"]
)

if success:
    print("Email sent successfully!")
```

## 📌 Important Notes

- For Gmail users: You'll need to use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular account password
- Make sure to add `email_config.ini` to your `.gitignore` file to prevent accidentally committing your email configuration

## 🔒 Security Best Practices

- Never hardcode passwords in your scripts
- Consider using environment variables for sensitive information
- Regularly update your email application passwords
- Use TLS/SSL for secure communication with email servers

## 🤝 Contributing

Contributions welcome! Feel free to submit pull requests or open issues to improve the functionality.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---
