#!/usr/bin/python3

import sys
import os
import re
import sqlite3

########################
## Variable Defs
########################

local_domains = [
    "cityviewgr.com",
    "brianbarto.info"
]

"""
email_lists = {
    "test@cityviewgr.com" : [
        "bartobrian@gmail.com",
        "bartobrian@outlook.com"
    ],
    "board@cityviewgr.com" : [
        "ksteindler@sbcglobal.net",
        "Matt.Clarke@firstcb.com",
        "bartobrian@gmail.com",
        "matt@sbbllaw.com",
        "michael_sytsma@keybank.com",
        "Gail.Lopez@colliers.com"
    ],
    "association@cityviewgr.com" : [
        "matt.clarke@firstcb.com",
        "Mark.Brant@firstcb.com",
        "jon@parklandgr.com",
        "mike@sbbllaw.com",
        "matt@sbbllaw.com",
        "heath@sbbllaw.com",
        "peterman@sbbllaw.com",
        "gary@sbbllaw.com",
        "cahaskins@me.com",
        "ccyoung@me.com",
        "grhsrent@gmail.com",
        "michael.clarke123@yahoo.com",
        "anja.harmon@hubinternational.com",
        "rickganzi@gmail.com",
        "marissamartz@hotmail.com",
        "junshenmsu@gmail.com",
        "curticas@mail.gvsu.edu",
        "paulboehms@gmail.com",
        "erharte@comcast.net",
        "Brich8b@gmail.com",
        "armbrecht2002@yahoo.com",
        "jgrotenrath@toolingsystemsgroup.com",
        "abagge05@gmail.com",
        "bartobrian@gmail.com",
        "LSamrick@yahoo.com",
        "Kelly.Rodenhouse@gmail.com",
        "alex@lgwd.net",
        "sara@lgwd.net",
        "tim@asco-components.com",
        "trcrpn@aol.com",
        "thegrimmlife@gmail.com",
        "dmcritchell@yahoo.com",
        "alissa.gramajo@yahoo.com",
        "jonathonperkins22@yahoo.com",
        "barnaclebob@gmail.com",
        "steindler@sbcglobal.net",
        "ksteindler@sbcglobal.net",
        "mfsytsma@yahoo.com",
        "mgordon1450@gmail.com"
    ],
    "residents@cityviewgr.com" : [
        "cahaskins@me.com",
        "ccyoung@me.com",
        "grhsrent@gmail.com",
        "streeterkelsei@gmail.com",
        "drewprescottdesign@gmail.com",
        "amandaw1190@gmail.com",
        "rickganzi@gmail.com",
        "marissamartz@hotmail.com",
        "junshenmsu@gmail.com",
        "curticas@mail.gvsu.edu",
        "paulboehms@gmail.com",
        "erharte@comcast.net",
        "Brich8b@gmail.com",
        "armbrecht2002@yahoo.com",
        "jgrotenrath@toolingsystemsgroup.com",
        "abagge05@gmail.com",
        "bartobrian@gmail.com",
        "LSamrick@yahoo.com",
        "Kelly.Rodenhouse@gmail.com",
        "alex@lgwd.net",
        "sara@lgwd.net",
        "tim@asco-components.com",
        "trcrpn@aol.com",
        "thegrimmlife@gmail.com",
        "dmcritchell@yahoo.com",
        "danny693@gmail.com",
        "barnaclebob@gmail.com",
        "steindler@sbcglobal.net",
        "ksteindler@sbcglobal.net",
        "mfsytsma@yahoo.com",
        "mgordon1450@gmail.com"
    ]
}
"""

re_header_cont = re.compile("^\s+\S+")
re_header_end = re.compile("^\s*$")
re_email_arg = re.compile("([^<>\"\s]+)@(\S+\.[^<>\"\s]+)")
re_email_parts = re.compile("(\S+)@(\S+\.\S+)")
re_sender_name = re.compile("^From:\s+\"?([^<>\"]*)\"?\s*<?(\S*)@\S+\.\S+>?$")
re_auto_reply = re.compile("^Auto-Submitted: (auto-generated|auto-replied)", re.IGNORECASE)

# 1 - Error
# 2 - Info
# 3 - Debug
# 4 - Trace
debug_level = 3
command = None
rval = None
db = None

########################
## Function Defs
########################

def check_database_tables(db):
    row = db.execute("select count(*) from sqlite_master where type = 'table' and name = 'lists'").fetchone()
    if (not row[0]):
        db.execute("create table lists(id INTEGER primary key autoincrement, name text, email text)")
    row = db.execute("select count(*) from sqlite_master where type = 'table' and name = 'recipients'").fetchone()
    if (not row[0]):
        db.execute("create table recipients(id INTEGER primary key autoincrement, list_id int, name text, email text)")

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

def command_filter():

    sender = None
    recipient = None
    content = []
    content_filtered = []
    sender_name = None
    list_id = None
    list_name = None
    list_recipients = []
    
    ## Process Args

    if (len(sys.argv) >= 4):
        if (not re_email_arg.match(sys.argv[2]) or not re_email_arg.match(sys.argv[3])):
            debug_line(1, f"Invalid arguments for filter command: {sys.argv[2]}, {sys.argv[3]}")
            return False
    else:
        debug_line(1, f"Missing arguments for filter command.")
        return False

    sender = sys.argv[2]
    recipient = sys.argv[3]

    for line in sys.stdin:
        content.append(line)
    if (len(content) == 0):
        debug_line(1, "STDIN does not contain email data.")
        return False

    ## Debug Data

    debug_line(2, f"Original Sender - {sender}")
    debug_line(2, f"Original Recipient - {recipient}")
    for line in content:
        if (re_header_end.match(line)):
            break
        debug_line(4, "Header - " + line)

    ## Skip if this is an auto-reply

    auto_sub_line = get_header(content, "Auto-Submitted")
    if (auto_sub_line and re_auto_reply.match(auto_sub_line)):
        return True

    ## Get Sender Name

    from_line = get_header(content, "From")
    if (from_line):
        if (re_sender_name.match(from_line)):
            results = re_sender_name.search(from_line)
            sender_name = results.group(1) if results.group(1) else results.group(2)
            sender_name = sender_name.rstrip()
        else:
            results = re_email_parts.search(sender)
            sender_name = results.group(1)
    else:
        results = re_email_parts.search(sender)
        sender_name = results.group(1)

    ## Get email list info

    row = db.execute("SELECT id, name FROM lists WHERE email = ?", [recipient]).fetchone()
    if (not row):
        debug_line(1, f"Recipient email list {recipient} not defined in database.")
        return False

    list_id = row[0]
    list_name = row[1]

    ## Get recipient list

    rows = db.execute("SELECT email FROM recipients WHERE list_id = ?", [list_id])
    for row in rows:
        list_recipients.append(row[0])

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

def command_lists():

    rows = db.execute("SELECT name, email FROM lists")
    for row in rows:
        print(f"{row[1]} ({row[0]})")

    return True

def command_dump():

    list_email = None
    list_id = None
    list_recipients = []

    ## Check args

    if (len(sys.argv) >= 3):
        if (not re_email_arg.match(sys.argv[2])):
            print(f"Invalid argument for dump command: {sys.argv[2]}")
            return False
    else:
        print(f"Missing argument for dump command.")
        return False

    list_email = sys.argv[2]

    ## Get email list id

    row = db.execute("SELECT id FROM lists WHERE email = ?", [list_email]).fetchone()
    if (not row):
        print(f"Email list {list_email} not defined in database.")
        return False

    list_id = row[0]

    ## Get email list recipients

    rows = db.execute("SELECT email FROM recipients WHERE list_id = ?", [list_id])
    for row in rows:
        list_recipients.append(row[0])

    ## Print recipients

    for r in list_recipients:
        print(r)

    return True

def command_create():

    list_email = None
    list_id = None
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

    ## Check if exists in db

    row = db.execute("SELECT id FROM lists WHERE email = ?", [list_email]).fetchone()
    if (row):
        print(f"Email list {list_email} already defined in database.")
        return False

    ## Insert into database

    db.execute("INSERT INTO lists (name, email) VALUES (?,?)", [list_name, list_email])
    db.commit()

    print(f"New list ({list_email}) added.")

    return True

def command_add():

    list_email = None
    list_id = None
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

    ## Get list id in db

    row = db.execute("SELECT id FROM lists WHERE email = ?", [list_email]).fetchone()
    if (not row):
        print(f"Email list {list_email} not defined in database.")
        return False

    list_id = row[0]

    ## Check if recipient already exists in list

    row = db.execute("SELECT count(*) FROM recipients WHERE list_id = ? AND email = ?", [list_id, recipient_email]).fetchone()
    if (row and row[0] > 0):
        print("Recipient ({recipient_email}) already exists in list ({list_email})")
        return False

    ## Insert into database

    db.execute("INSERT INTO recipients (list_id, name, email) VALUES (?,?, ?)", [list_id, recipient_name, recipient_email])
    db.commit()

    print(f"New recipient ({recipient_email}) added to list ({list_email})")

    return True


########################
## Main Program
########################

## Connect to DB (create DB if needed) and check tables.

listfix_dir = os.path.dirname(os.path.realpath(__file__))
db = sqlite3.connect(listfix_dir + "/listfix.db")

check_database_tables(db)

## Get command

if (len(sys.argv) >= 1):
    command = sys.argv[1]
else:
    raise ValueError("Missing Command Argument")

## Evaluate command

if (command == "filter"):
    rval = command_filter()
    if (not rval):
        raise ValueError(f"Error while executing command_filter()")
elif (command == "lists"):
    rval = command_lists()
    if (not rval):
        raise ValueError(f"Error while executing command_lists()")
elif (command == "dump"):
    rval = command_dump()
    if (not rval):
        raise ValueError(f"Error while executing command_dump()")
elif (command == "create"):
    rval = command_create()
    if (not rval):
        raise ValueError(f"Error while executing command_create()")
elif (command == "add"):
    rval = command_add()
    if (not rval):
        raise ValueError(f"Error while executing command_add()")
else:
    raise ValueError(f"Unknown Command: {command}")

## Disconnect from DB

db.close()
