#!/usr/bin/python3

import sys
import re
import os
from listfix import DB, Email

########################
## Function Defs
########################

def debug_line(level, line):

    levels = {
        1 : "Error",
        2 : "Info",
        3 : "Debug",
        4 : "Trace"
    }

    if (level not in levels.keys()):
        return

    line = line.rstrip()

    if (level <= debug_level):
        f = open("/tmp/listfix_log.txt", "a")
        f.write(f"[{levels[level]}] {line}\n")
        f.close()

########################
## Main Program
########################

re_email_arg = re.compile("([^<>\"\s]+)@(\S+\.[^<>\"\s]+)")

## Connect to DB (create DB if needed) and check tables.

listfix_dir = os.path.dirname(os.path.realpath(__file__))
db = DB(listfix_dir + "/listfix.sqlite3")

## Get command

command = None
if (len(sys.argv) >= 1):
    command = sys.argv[1]
else:
    raise ValueError("Missing Command Argument")

## Evaluate command

if (command == "filter"):

    if (len(sys.argv) >= 3):
        if (not re_email_arg.match(sys.argv[2])):
            raise ValueError(f"Error while executing filter.")
    else:
        raise ValueError(f"Error while executing filter.")

    list_email = sys.argv[2]

    content = []
    for line in sys.stdin:
        content.append(line)

    email_in = Email(content)

    if (email_in.is_auto_reply()):
        exit()

    sender_email = email_in.get_sender_email()
    sender_name = email_in.get_sender_name()

    list_name = db.get_list_name(list_email)
    list_recipients = db.get_list_recipients(list_email)

    email_out = Email(email_in.get_content())
    email_out.strip_headers(exclude = ["To", "Cc", "Subject", "Content-[^:]+", "MIME-Version"])
    if (sender_email not in list_recipients):
        email_out.add_header_prepend(f"Reply-To: {list_email}, {sender}")
    else:
        email_out.add_header_prepend(f"Reply-To: {list_email}")
    email_out.add_header_prepend(f"From: \"{sender_name} via {list_name}\" <{list_email}>")

    if sender_email in list_recipients:
        list_recipients.remove(sender_email)

    for r in list_recipients:
        email_out.send(r)

elif (command == "lists"):

    lists = db.get_lists()
    for l in lists:
        list_name = db.get_list_name(l)
        print(f"{l} ({list_name})")

elif (command == "dump"):

    if (len(sys.argv) >= 3):
        if (not re_email_arg.match(sys.argv[2])):
            raise ValueError(f"Error while executing dump.")
    else:
        raise ValueError(f"Error while executing dump.")

    list_email = sys.argv[2]

    recipients = db.get_list_recipients(list_email)
    for r in recipients:
        recipient_name = db.get_recipient_name(list_email, r)
        print(f"{r} ({recipient_name})")

elif (command == "create"):

    if (len(sys.argv) >= 4):
        if (not re_email_arg.match(sys.argv[2])):
            raise ValueError(f"Error while executing create.")
    else:
        raise ValueError(f"Error while executing create.")

    list_email = sys.argv[2]
    list_name = sys.argv[3]

    db.create_list(list_email, list_name)

    print(f"New list ({list_email}) added.")

elif (command == "destroy"):

    if (len(sys.argv) >= 3):
        if (not re_email_arg.match(sys.argv[2])):
            raise ValueError(f"Error while executing destroy.")
    else:
        raise ValueError(f"Error while executing destroy.")

    list_email = sys.argv[2]

    db.destroy_list(list_email)

    print(f"Email list ({list_email}) destroyed.")

elif (command == "add"):

    if (len(sys.argv) >= 5):
        if (not re_email_arg.match(sys.argv[2]) or not re_email_arg.match(sys.argv[3])):
            raise ValueError(f"Error while executing add.")
    else:
        raise ValueError(f"Error while executing add.")

    list_email = sys.argv[2]
    recipient_email = sys.argv[3]
    recipient_name = sys.argv[4]

    db.create_recipient(list_email, recipient_email, recipient_name)

    print(f"New recipient ({recipient_email}) added to list ({list_email})")

elif (command == "remove"):

    if (len(sys.argv) >= 4):
        if (not re_email_arg.match(sys.argv[2]) or not re_email_arg.match(sys.argv[3])):
            raise ValueError(f"Error while executing remove.")
    else:
        raise ValueError(f"Error while executing remove.")

    list_email = sys.argv[2]
    recipient_email = sys.argv[3]

    db.destroy_recipient(list_email, recipient_email)

    print(f"Recipient ({recipient_email}) removed from list ({list_email})")

else:

    raise ValueError(f"Unknown Command: {command}")

## Disconnect from DB

db.close()
