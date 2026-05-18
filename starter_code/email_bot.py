"""
email_bot.py
============
Project:    Email Sender Bot
Difficulty: Intermediate
Skills:     Python, smtplib, email module, csv module, os module
Time:       Medium (a weekend)

What you will build:
    A script that reads a recipient list from a CSV file and sends each
    person a personalised email through Gmail's SMTP server. Credentials
    are read from environment variables — passwords never appear in source
    code. Every send attempt (success or failure) is logged to a report CSV.

How to run:
    1. Turn on 2-Step Verification in your Google account.
    2. Generate a Gmail App Password at myaccount.google.com/apppasswords.
    3. Set your credentials as environment variables:
           macOS / Linux:
               export EMAIL_ADDRESS="you@gmail.com"
               export EMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
           Windows (Command Prompt):
               set EMAIL_ADDRESS=you@gmail.com
               set EMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
    4. Create recipients.csv with at minimum two columns: name,email
    5. python email_bot.py

Learning goals:
    - Sending email programmatically with smtplib.SMTP_SSL
    - Building a proper Message object with email.mime.text.MIMEText
    - Reading secrets securely from environment variables (never hardcode!)
    - Parsing a CSV file and personalising content per recipient
    - Logging results and handling SMTP errors gracefully

Roadmap:
    Step 1:  Set up your env vars and create a recipients.csv with two test rows
    Step 2:  Complete get_credentials() to read and validate the env vars
    Step 3:  Complete load_recipients() to parse the CSV into a list of dicts
    Step 4:  Complete compose_message() to build a MIMEText email object
    Step 5:  Complete send_email() to open SMTP_SSL and deliver the message
    Step 6:  Complete log_result() to append each outcome row to the report CSV
    Step 7:  Complete send_bulk() to loop through all recipients and log results
    Step 8:  Test with yourself and one other address before sending to a larger list
"""

import csv
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# CSV file containing the recipient list — required columns: name, email
RECIPIENTS_FILE = "recipients.csv"

# Report CSV written after each bulk send run
REPORT_FILE = "send_report.csv"
REPORT_HEADERS = ["name", "email", "status", "timestamp"]


# ---------------------------------------------------------------------------
# Core functions — complete the TODOs to make each one work
# ---------------------------------------------------------------------------

def get_credentials():
    """
    Read the sender's Gmail address and App Password from environment variables.

    Returns:
        tuple[str, str]: (email_address, app_password)

    Raises:
        EnvironmentError: If either variable is missing or empty.

    Environment variables expected:
        EMAIL_ADDRESS       — the full Gmail address, e.g. you@gmail.com
        EMAIL_APP_PASSWORD  — the 16-character App Password from Google

    TODO:
        1. Read os.environ.get("EMAIL_ADDRESS") and os.environ.get("EMAIL_APP_PASSWORD").
        2. If either value is None or an empty string, raise EnvironmentError with
           a clear message that names both required variables.
        3. Return (email_address, app_password) as a tuple.
    """
    # --- Write your code here ---

    return ("", "")


def load_recipients(filepath):
    """
    Read the CSV file and return a list of recipient dicts.

    Args:
        filepath (str): Path to the CSV file. Must have "name" and "email" columns.

    Returns:
        list[dict]: Each dict has at least {"name": str, "email": str}.
                    Rows with an empty email field are skipped.
                    Returns an empty list if the file has no valid data rows.

    Raises:
        FileNotFoundError: If filepath does not exist.
        KeyError: If the CSV is missing a required column.

    TODO:
        1. Open filepath for reading with csv.DictReader.
        2. For each row, verify that "name" and "email" keys exist.
        3. Skip rows where row["email"].strip() is empty.
        4. Append valid rows to the results list and return it.
    """
    recipients = []

    # --- Write your code here ---

    return recipients


def compose_message(sender, recipient_name, recipient_email, subject, body_template):
    """
    Build and return a MIMEText email message object.

    The body_template may contain the placeholder {name}, which is replaced
    with recipient_name before the message is created.

    Args:
        sender (str):           The From address, e.g. "you@gmail.com".
        recipient_name (str):   Used to personalise the body.
        recipient_email (str):  The To address.
        subject (str):          Email subject line.
        body_template (str):    Plain-text body. Use {name} for personalisation.

    Returns:
        MIMEText: A fully addressed email message object ready to send.

    TODO:
        1. Personalise the body:
               body = body_template.format(name=recipient_name)
        2. Create the message object:
               msg = MIMEText(body, "plain")
        3. Set the headers:
               msg["From"]    = sender
               msg["To"]      = recipient_email
               msg["Subject"] = subject
        4. Return msg.
    """
    # --- Write your code here ---

    return MIMEText("", "plain")


def send_email(sender, password, message):
    """
    Open an SSL connection to Gmail's SMTP server and deliver one message.

    Args:
        sender (str):       The authenticated sender address.
        password (str):     The Gmail App Password.
        message (MIMEText): A composed message object from compose_message().

    Returns:
        bool: True if the message was delivered successfully, False on any error.

    TODO:
        1. Wrap the entire send logic in try/except smtplib.SMTPException.
        2. Use smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as a context manager.
        3. Inside the with block, call server.login(sender, password).
        4. Send with server.sendmail(sender, message["To"], message.as_string()).
        5. Return True if no exception is raised.
        6. In the except block, print the error and return False.
    """
    # --- Write your code here ---

    return False


def log_result(name, email, status):
    """
    Append one row to REPORT_FILE recording the outcome of a send attempt.

    Creates REPORT_FILE with a header row on the first call if it does not
    already exist.

    Args:
        name (str):   Recipient's name.
        email (str):  Recipient's email address.
        status (str): "sent" or "failed".

    TODO:
        1. Check if REPORT_FILE exists. If not, open it in write mode ("w")
           and write REPORT_HEADERS using csv.writer.writerow().
        2. Open REPORT_FILE in append mode ("a") with newline="".
        3. Use csv.DictWriter with fieldnames=REPORT_HEADERS to write one row:
               {
                   "name":      name,
                   "email":     email,
                   "status":    status,
                   "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
               }
    """
    # --- Write your code here ---

    pass


def send_bulk(subject, body_template):
    """
    Send a personalised email to every recipient in RECIPIENTS_FILE.

    Args:
        subject (str):       Email subject line.
        body_template (str): Body text — use {name} as a personalisation placeholder.

    Returns:
        dict: {"sent": int, "failed": int} — a summary of the run.

    TODO:
        1. Call get_credentials() to get (sender, password).
           Catch EnvironmentError, print it, and return {"sent": 0, "failed": 0}.
        2. Call load_recipients(RECIPIENTS_FILE) to get the list.
           If the list is empty, print a warning and return {"sent": 0, "failed": 0}.
        3. For each recipient dict:
               a. Call compose_message() with the recipient's name and email.
               b. Call send_email() and inspect the return value.
               c. Set status = "sent" if True, "failed" if False.
               d. Print a one-line progress update, e.g.:
                      "  [sent]   Alice <alice@example.com>"
               e. Call log_result(name, email, status).
               f. Increment summary["sent"] or summary["failed"] accordingly.
        4. Return the summary dict.
    """
    summary = {"sent": 0, "failed": 0}

    # --- Write your code here ---

    return summary


# ---------------------------------------------------------------------------
# Email content — edit the subject and body to customise your campaign
# ---------------------------------------------------------------------------

EMAIL_SUBJECT = "Hello from DevPath!"

EMAIL_BODY = """\
Hi {name},

Thank you for signing up. We are excited to have you on board.

Head over to DevPath to find your next coding project and get started today.

Best,
The DevPath Team
"""


# ---------------------------------------------------------------------------
# Entry point — already complete, no changes needed here
# ---------------------------------------------------------------------------

def main():
    """Run the bulk email sender and print a final summary."""
    print("\n== Email Sender Bot ==")
    print(f"Recipients file : {RECIPIENTS_FILE}")
    print(f"Report file     : {REPORT_FILE}\n")

    summary = send_bulk(EMAIL_SUBJECT, EMAIL_BODY)

    print("\n" + "=" * 35)
    print("  Send complete")
    print("=" * 35)
    print(f"  Sent   : {summary['sent']}")
    print(f"  Failed : {summary['failed']}")
    print(f"  Report : {REPORT_FILE}")
    print("=" * 35 + "\n")


if __name__ == "__main__":
    main()
