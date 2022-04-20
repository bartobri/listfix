#!/usr/bin/python3

import sys
import os
from listfix import Args, DB, Email, Errors, Log, Test

## Setup

listfix_dir = os.path.dirname(os.path.realpath(__file__))

log = Log(listfix_dir + "/listfix.log")

er = Errors(log, debug=False)
er.set_exception_handler()

db = DB(listfix_dir + "/listfix.json")

args = Args(sys.argv)
command = args.get_command()

## Evaluate command

if (command == "filter"):
    list_email = args.get_list_email()
    list_name = db.get_list_name(list_email)
    list_recipients = db.get_list_recipients(list_email)

    email_in = Email(list(sys.stdin))
    if (email_in.check_auto_reply()):
        exit()
    sender_email = email_in.get_sender_email()
    sender_name = email_in.get_sender_name()

    log.info(f"Email from: {sender_email}")
    log.info(f"Email list: {list_email}")

    email_out = Email(email_in.get_content())
    email_out.strip_headers(exclude = ["To", "Cc", "Subject", "Content-[^:]+", "MIME-Version"])
    if (sender_email not in list_recipients):
        email_out.add_header_prepend(f"Reply-To: {list_email}, {sender_email}")
    else:
        email_out.add_header_prepend(f"Reply-To: {list_email}")
    email_out.add_header_prepend(f"From: \"{sender_name} via {list_name}\" <{list_email}>")

    if sender_email in list_recipients:
        list_recipients.remove(sender_email)

    for r in list_recipients:
        log.info(f"Recipient: {r}")
        email_out.send(r)

elif (command == "lists"):
    lists = db.get_lists()
    if (len(lists) == 0):
        print("No lists defined.")
    else:
        for l in lists:
            list_name = db.get_list_name(l)
            print(f"{l} ({list_name})")

elif (command == "dump"):
    list_email = args.get_list_email()
    recipients = db.get_list_recipients(list_email)
    if (len(recipients) == 0):
        print(f"No recipients defined for list {list_email}")
    else:
        for r in recipients:
            recipient_name = db.get_recipient_name(list_email, r)
            print(f"{r} ({recipient_name})")

elif (command == "create"):
    list_email = args.get_list_email()
    list_name = args.get_list_name()
    db.create_list(list_email, list_name)
    print(f"New list ({list_email}) added.")

elif (command == "destroy"):
    list_email = args.get_list_email()
    db.destroy_list(list_email)
    print(f"Email list ({list_email}) destroyed.")

elif (command == "add"):
    list_email = args.get_list_email()
    recipient_email = args.get_recipient_email()
    recipient_name = args.get_recipient_name()
    db.create_recipient(list_email, recipient_email, recipient_name)
    print(f"New recipient ({recipient_email}) added to list ({list_email})")

elif (command == "remove"):
    list_email = args.get_list_email()
    recipient_email = args.get_recipient_email()
    db.destroy_recipient(list_email, recipient_email)
    print(f"Recipient ({recipient_email}) removed from list ({list_email})")

elif (command == "test"):
    test = Test()
    test.run_test()

else:
    raise ValueError(f"Unknown command: {command}")

## Disconnect from DB

db.save()
