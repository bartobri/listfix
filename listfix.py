#!/usr/bin/python3

import sys
import os
import re

sys.path.insert(1, sys.path[0] + "/mods")
from listfixdb import ListfixDB

########################
## Variable Defs
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

def command_filter(db):

    recipient = None
    sender = None
    sender_name = None
    content = []
    content_filtered = []
    list_name = None
    list_recipients = []
    
    ## Process Args

    if (len(sys.argv) >= 3):
        if (not re_email_arg.match(sys.argv[2])):
            debug_line(1, f"Invalid argument for filter command: {sys.argv[2]}")
            return False
    else:
        debug_line(1, f"Missing argument for filter command.")
        return False

    recipient = sys.argv[2]

    debug_line(2, f"Original Recipient - {recipient}")

    ## Get email contents

    for line in sys.stdin:
        content.append(line)
    if (len(content) == 0):
        debug_line(1, "STDIN does not contain email data.")
        return False

    ## Get sender info

    from_line = get_header(content, "From")
    if (from_line):
        if (re_sender_info.match(from_line)):
            results = re_sender_info.search(from_line)
            sender_name = results.group(1) if results.group(1) else results.group(3)
            sender = results.group(2)
        else:
            debug_line(1, "From line does not match regular expression.")
            debug_line(3, from_line)
            return False
    else:
        debug_line(1, "Could not find From line in email contents.")
        return False

    debug_line(2, f"Original Sender - {sender}")

    ## Skip if this is an auto-reply

    auto_sub_line = get_header(content, "Auto-Submitted")
    if (auto_sub_line and re_auto_reply.match(auto_sub_line)):
        return True

    ## Get email list info

    list_name = db.get_list_name(recipient)
    if (not list_name):
        debug_line(1, f"Recipient email list {recipient} not defined in database.")
        return False

    ## Get recipient list

    list_recipients = db.get_list_recipients(recipient)
    if (len(list_recipients) == 0):
        debug_line(1, f"No recipients defined for email list: {recipient}.")

    ## Costruct Filtered Email

    content_filtered.append(f"From: \"{sender_name} via {list_name}\" <{recipient}>\n")
    if (sender not in list_recipients):
        content_filtered.append(f"Reply-To: {recipient}, {sender}\n")
    else:
        content_filtered.append(f"Reply-To: {recipient}\n")
    exclude_headers = ["To", "Cc", "Subject", "Content-[^:]+", "MIME-Version"]
    content_filtered.extend(strip_headers(content, exclude_headers))

    ## Remove sender from list

    if sender in list_recipients:
        list_recipients.remove(sender)

    ## Send emails

    for r in list_recipients:
        send_email(r, content_filtered)
        debug_line(3, f"List Recipient: {r}")

    return True

def command_lists(db):
    lists = db.get_lists()

    for l in lists:
        list_name = db.get_list_name(l)
        print(f"{l} ({list_name})")

    return True

def command_dump(db):

    list_email = None

    ## Check args

    if (len(sys.argv) >= 3):
        if (not re_email_arg.match(sys.argv[2])):
            print(f"Invalid argument for dump command: {sys.argv[2]}")
            return False
    else:
        print(f"Missing argument for dump command.")
        return False

    list_email = sys.argv[2]

    ## Print list recipients

    recipients = db.get_list_recipients(list_email)

    for r in recipients:
        recipient_name = db.get_recipient_name(list_email, r)
        print(f"{r} ({recipient_name})")

    return True

def command_create(db):

    list_email = None
    list_name = None

    ## Check args

    if (len(sys.argv) >= 4):
        if (not re_email_arg.match(sys.argv[2])):
            print(f"Invalid argument for create command: {sys.argv[2]}")
            return False
    else:
        print(f"Missing argument for create command.")
        return False

    list_email = sys.argv[2]
    list_name = sys.argv[3]
    
    ## Insert into database

    db.create_list(list_email, list_name)

    print(f"New list ({list_email}) added.")

    return True

def command_destroy(db):

    list_email = None

    ## Check args

    if (len(sys.argv) >= 3):
        if (not re_email_arg.match(sys.argv[2])):
            print(f"Invalid argument for destroy command: {sys.argv[2]}")
            return False
    else:
        print(f"Missing argument for destroy command.")
        return False

    list_email = sys.argv[2]

    ## Destroy list

    db.destroy_list(list_email)

    print(f"Email list ({list_email}) destroyed.")

    return True

def command_add(db):

    list_email = None
    recipient_email = None
    recipient_name = None

    ## Check Args

    if (len(sys.argv) >= 5):
        if (not re_email_arg.match(sys.argv[2]) or not re_email_arg.match(sys.argv[3])):
            print(f"Invalid arguments for add command: {sys.argv[2]}, {sys.argv[3]}, {sys.argv[4]}")
            return False
    else:
        print(f"Missing arguments for add command.")
        return False

    list_email = sys.argv[2]
    recipient_email = sys.argv[3]
    recipient_name = sys.argv[4]

    ## Check if recipient already exists in list

    if (db.check_recipient_exists(list_email, recipient_email)):
        print(f"Recipient ({recipient_email}) already exists in list ({list_email})")
        return False

    ## Insert into database

    db.create_recipient(list_email, recipient_email, recipient_name)

    print(f"New recipient ({recipient_email}) added to list ({list_email})")

    return True

def command_remove(db):

    list_email = None
    recipient_email = None

    ## Check Args

    if (len(sys.argv) >= 4):
        if (not re_email_arg.match(sys.argv[2]) or not re_email_arg.match(sys.argv[3])):
            print(f"Invalid arguments for remove command: {sys.argv[2]}, {sys.argv[3]}")
            return False
    else:
        print(f"Missing arguments for remove command.")
        return False

    list_email = sys.argv[2]
    recipient_email = sys.argv[3]

    ## Destroy Recipient

    db.destroy_recipient(list_email, recipient_email)

    print(f"Recipient ({recipient_email}) removed from list ({list_email})")

    return True


########################
## Main Program
########################

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
    rval = command_filter(db)
    if (not rval):
        raise ValueError(f"Error while executing command_filter()")
elif (command == "lists"):
    rval = command_lists(db)
    if (not rval):
        raise ValueError(f"Error while executing command_lists()")
elif (command == "dump"):
    rval = command_dump(db)
    if (not rval):
        raise ValueError(f"Error while executing command_dump()")
elif (command == "create"):
    rval = command_create(db)
    if (not rval):
        raise ValueError(f"Error while executing command_create()")
elif (command == "destroy"):
    rval = command_destroy(db)
    if (not rval):
        raise ValueError(f"Error while executing command_destroy()")
elif (command == "add"):
    rval = command_add(db)
    if (not rval):
        raise ValueError(f"Error while executing command_add()")
elif (command == "remove"):
    rval = command_remove(db)
    if (not rval):
        raise ValueError(f"Error while executing command_remove()")
else:
    raise ValueError(f"Unknown Command: {command}")

## Disconnect from DB

db.close()
