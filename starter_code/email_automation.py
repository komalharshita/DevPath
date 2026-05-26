# Starter code: Simple Email Automation
import smtplib
import os
from email.mime.text import MIMEText

def send_email(sender, receiver, subject, body):
    """Send an email using Gmail SMTP."""
    # TODO: Step 1 — Get password safely from environment variable
    # Never hardcode passwords in your code!
    password = os.environ.get("EMAIL_PASSWORD")

    # TODO: Step 2 — Create the email message
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    # TODO: Step 3 — Connect to Gmail SMTP server
    # with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    #     server.login(sender, password)
    #     server.send_message(msg)
    pass

def read_recipients(file_path):
    """Read recipient emails from a text file."""
    # TODO: Open the file and read emails line by line
    # with open(file_path, "r") as f:
    #     return [line.strip() for line in f.readlines()]
    pass

if __name__ == "__main__":
    # Set EMAIL_PASSWORD in terminal before running:
    # Windows: set EMAIL_PASSWORD=yourpassword
    # Mac/Linux: export EMAIL_PASSWORD=yourpassword
    sender = input("Enter your Gmail address: ")
    receiver = input("Enter receiver email: ")
    send_email(sender, receiver, "Hello", "This is a test email.")