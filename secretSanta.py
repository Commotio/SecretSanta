import argparse
import logging
import random
import os
import configparser
import csv
from collections import Counter
import smtplib
import ssl
from email.message import EmailMessage

# ---------------------------
# Giver Class
# ---------------------------
class Giver:
    def __init__(self, name, email=None, categories=None):
        self.name = name
        self.email = email
        self.assignments = dict.fromkeys(categories or [None])

    def assign(self, receiver_list):
        for ind, category in enumerate(self.assignments):
            self.assignments[category] = receiver_list[ind]

    def __str__(self):
        if len(self.assignments) > 1:
            msg = "\n".join(f"{cat}: {rec}" for cat, rec in self.assignments.items())
        else:
            msg = f"{self.assignments[None]}"
        return f"{self.name}'s Top Secret Assignment:\n\n{msg}"

# ---------------------------
# Read File
# ---------------------------
def readFromFile(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f]

# ---------------------------
# Load Participants
# ---------------------------
def load_participants(file_path, categories, require_email=False):
    givers = []
    _, ext = os.path.splitext(file_path.lower())
    if ext == ".csv":
        with open(file_path, newline='', encoding='utf-8') as f:
            # Try DictReader first
            try:
                reader = csv.DictReader(f)
                first_row = next(reader)
                # Check if 'Name' exists
                if 'Name' in first_row or 'name' in first_row:
                    # Use DictReader as normal
                    f.seek(0)
                    reader = csv.DictReader(f)
                    for row in reader:
                        name = row.get('Name') or row.get('name')
                        email = row.get('Email') or row.get('email') or ''
                        if name is None:
                            raise ValueError(f"CSV row missing a name: {row}")
                        name = name.strip()
                        email = email.strip()
                        if require_email and not email:
                            raise ValueError(f"Participant '{name}' has no email, but email sending is enabled.")
                        givers.append(Giver(name=name, email=email if email else None, assignments=dict.fromkeys([None])))
                else:
                    # CSV has no headers, fallback to first column = name, second = email
                    f.seek(0)
                    reader = csv.reader(f)
                    for row in reader:
                        if not row:
                            continue
                        name = row[0].strip()
                        email = row[1].strip() if len(row) > 1 else None
                        if require_email and not email:
                            raise ValueError(f"Participant '{name}' has no email, but email sending is enabled.")
                        givers.append(Giver(name=name, email=email, categories=categories))
            except StopIteration:
                raise ValueError("CSV file is empty")
    else:
        for line in readFromFile(file_path):
            name = line.strip()
            email = None
            if require_email:
                raise ValueError(f"Participant '{name}' has no email, but email sending is enabled.")
            givers.append(Giver(name=name, email=email, categories=categories))
    return givers

# ---------------------------
# Create Assignments
# ---------------------------
def createAssignments(givers, participants, categories):
    #Assign a unique recipient for each giver in each category.
    receiver_map = []

    for giver in givers:
        assigned = []
        for category in categories:
            # Available recipients for this category
            potential_receivers = [p for p in participants if p != giver.name and p not in assigned]
            if not potential_receivers:
                raise ValueError("Not enough participants to assign without repeats")
            recipient = random.choice(potential_receivers)
            assigned.append(recipient)
        receiver_map.append(assigned)
    return receiver_map


# ---------------------------
# Finalize Assignments
# ---------------------------
def finalizeAssignments(givers, receiver_map):
    for ind, giver in enumerate(givers):
        giver.assign(receiver_map[ind])

# ---------------------------
# Write Assignment Files
# ---------------------------
def writeAssignmentsFile(givers, path):
    os.makedirs(path, exist_ok=True)
    for giver in givers:
        file_path = os.path.join(path, f"{giver.name}_SecretSantaAssignments.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(giver))
    print(f"Files written to {path}")

# ---------------------------
# Send Email
# ---------------------------
def send_email(receiver, html_template=None, body_override=None, config_path="config.ini"):
    # Load config
    config = configparser.ConfigParser()
    with open(config_path, encoding="utf-8") as f:
        config.read_file(f)
    email_conf = config["email"]

    smtp_server = email_conf.get("smtp_server", "smtp.gmail.com")
    port = email_conf.getint("port", 465)
    sender = email_conf.get("sender_email")
    password = email_conf.get("password")
    subject = email_conf.get("subject", "Your Secret Santa Assignment!")

    # Prepare body
    text_body = body_override or "Your Secret Santa assignments are ready!"
    html_body = html_template

    # Create message
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.set_content(text_body)
    if html_body:
        msg.add_alternative(html_body, subtype="html")

    # Send
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender, password)
        server.send_message(msg)

# ---------------------------
# Send Emails to All Givers
# ---------------------------
def sendEmails(givers, template_file, config_path="config.ini"):
    if not os.path.exists(template_file):
        logging.error(f"Email template '{template_file}' not found.")
        return

    with open(template_file, 'r', encoding='utf-8') as f:
        template_body = f.read()

    for giver in givers:
        if not giver.email:
            logging.warning(f"No email for {giver.name}, skipping...")
            continue

        assignments_str = "\n".join(f"{cat}: {rec}" for cat, rec in giver.assignments.items())
        html_body = template_body.replace("{{name}}", giver.name).replace("{{assignment}}", assignments_str)
        body_override = f"Hi {giver.name},\nYour Secret Santa assignment is:\n{assignments_str}"

        send_email(receiver=giver.email, html_template=html_body, body_override=body_override, config_path=config_path)
    print("Emails sent")

# ---------------------------
# Main
# ---------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--categories', help='File or comma-separated list of categories')
    parser.add_argument('-p', '--participants', help='File or comma-separated list of participants', required=True)
    parser.add_argument('-o', '--output_files', action='store_true', help='Save assignments to files')
    parser.add_argument('-of', '--output_path', default='./Assignments', help='Directory to save files')
    parser.add_argument('--send_emails', action='store_true', help='Send emails')
    parser.add_argument('--email_template', help='Path to HTML email template')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-vv', '--very_verbose', action='store_true')
    args = parser.parse_args()

    # Load config
    config_path="config.ini"
    config = configparser.ConfigParser()
    with open(config_path, encoding="utf-8") as f:
        config.read_file(f)

    # Logging
    if args.very_verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    # Load categories
    if args.categories:
        if os.path.isfile(args.categories):
            categories = readFromFile(args.categories)
        else:
            categories = [c.strip() for c in args.categories.split(',')]
    else:
        categories = [None]

    # Load participants
    require_email = args.send_emails or config.getboolean("email", "send_emails", fallback=False)
    givers = load_participants(args.participants, categories, require_email=require_email)
    participants = [g.name for g in givers]

    # Validate uniqueness
    if len(participants) != len(set(participants)):
        logging.error("Duplicate participants found")
        exit(1)
    if len(categories) != len(set(categories)):
        logging.error("Duplicate categories found")
        exit(1)
    if len(participants) <= len(categories):
        logging.error("Not enough participants compared to categories")
        exit(1)

    # Generate assignments
    receiver_map = createAssignments(givers, participants, categories)
    finalizeAssignments(givers, receiver_map)
    logging.info("Assignments completed.")

    # Write files
    if args.output_files:
        writeAssignmentsFile(givers, args.output_path)

    # Send emails
    if require_email:
        email_template = args.email_template or config.get("email", "email_template", fallback="templates/christmas.html")
        sendEmails(givers, email_template)
        
    # If not outputting to file or sending emails, print to screen
    if not args.output_files and not require_email:
        for giver in givers:
            print(f"\n{giver}")
            print("-" * 40)

if __name__ == "__main__":
    main()
