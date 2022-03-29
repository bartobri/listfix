#!/usr/bin/python3

import sys
import os
import re

sys.path.insert(1, sys.path[0] + "/mods")

from listfixdb import ListfixDB

########################
## Function Defs
########################

def get_header(lines, header):
    rval = None

    re_header = re.compile("^" + header + ": ", re.IGNORECASE)

    header = header.rstrip()
    if (header[-1] == ":"):
        header = header[0:-1]

    append_next = False
    in_header = True
    for line in lines:
        if (in_header):
            if (re_header_cont.match(line) and append_next):
                rval = rval + " " + line.rstrip().lstrip()
                continue

            append_next = False
            if (re_header.match(line)):
                rval = line.rstrip()
                append_next = True
            elif (re_header_end.match(line)):
                in_header = False
        else:
            break

    return rval

def strip_headers(lines, exclude):
    rval = []

    append_next = False
    in_header = True
    for line in lines:
        if (in_header):
            if (re_header_cont.match(line) and append_next):
                rval.append(line)
                continue

            if (re_header_end.match(line)):
                rval.append(line)
                in_header = False
                continue

            append_next = False
            for ex in exclude:
                if (re.match("^" + ex + ": ", line, re.IGNORECASE)):
                    rval.append(line)
                    append_next = True
                    break
        else:
            rval.append(line)

    return rval

def send_email(to_email, email_contents):
    p = os.popen(f"/usr/sbin/sendmail -G -i {to_email}", "w")
    for line in email_contents:
        p.write(line)
    p.close()

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

re_header_cont = re.compile("^\s+\S+")
re_header_end = re.compile("^\s*$")
re_email_arg = re.compile("([^<>\"\s]+)@(\S+\.[^<>\"\s]+)")
re_email_parts = re.compile("(\S+)@(\S+\.\S+)")
re_sender_info = re.compile("^From:\s+\"?([^<>\"]*?)\"?\s*<?(([^<>\"\s]+)@\S+\.[^<>\"\s]+)>?$")
re_auto_reply = re.compile("^Auto-Submitted: (auto-generated|auto-replied)", re.IGNORECASE)

# 1 - Error
# 2 - Info
# 3 - Debug
# 4 - Trace
debug_level = 3
command = None
rval = None

## Connect to DB (create DB if needed) and check tables.

listfix_dir = os.path.dirname(os.path.realpath(__file__))
db = ListfixDB(listfix_dir + "/listfix.sqlite3")

## Get command

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

    recipient = sys.argv[2]

    content = []
    for line in sys.stdin:
        content.append(line)
    if (len(content) == 0):
        raise ValueError(f"Error while executing filter. No content.")

    sender = None
    sender_name = None
    from_line = get_header(content, "From")
    if (from_line):
        if (re_sender_info.match(from_line)):
            results = re_sender_info.search(from_line)
            sender_name = results.group(1) if results.group(1) else results.group(3)
            sender = results.group(2)
        else:
            raise ValueError(f"Error while executing filter. No matching email in From header.")
    else:
        raise ValueError(f"Error while executing filter. No From header.")

    auto_sub_line = get_header(content, "Auto-Submitted")
    if (auto_sub_line and re_auto_reply.match(auto_sub_line)):
        exit()

    list_name = db.get_list_name(recipient)
    if (not list_name):
        raise ValueError(f"Error while executing filter. List {recipient} not defined.")

    list_recipients = db.get_list_recipients(recipient)
    if (len(list_recipients) == 0):
        raise ValueError(f"Error while executing filter. No recipients defined for list {recipient}.")

    content_filtered = []
    content_filtered.append(f"From: \"{sender_name} via {list_name}\" <{recipient}>\n")
    if (sender not in list_recipients):
        content_filtered.append(f"Reply-To: {recipient}, {sender}\n")
    else:
        content_filtered.append(f"Reply-To: {recipient}\n")
    exclude_headers = ["To", "Cc", "Subject", "Content-[^:]+", "MIME-Version"]
    content_filtered.extend(strip_headers(content, exclude_headers))

    if sender in list_recipients:
        list_recipients.remove(sender)

    for r in list_recipients:
        #send_email(r, content_filtered)
        print(f"Sent to {r}")

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
