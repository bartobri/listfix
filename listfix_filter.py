#!/usr/bin/python3

import sys
import socket
import pwd
import os
import re

########################
## Function Defs
########################

def args_ok():
    if (len(sys.argv) > 2):
        if (not re_email.match(sys.argv[1]) or not re_email.match(sys.argv[2])):
            return False
        else:
            return True
    else:
        return False

def get_header(lines, header):
    rval = None

    re_header = re.compile("^" + header + ": ")

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
                if (re.match("^" + ex + ": ", line)):
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

def log_info(sender, recipient, lines):

    f = open("/tmp/listfix_log.txt", "a")
    f.write(f"Postfix Sender: {sender}\n")
    f.write(f"Postfix Recipient: {recipient}\n")

    for line in lines:
        if (re_header_end.match(line)):
                break

        f.write(line)

    f.write("\n")
    f.close()


########################
## Main Program
########################

re_header_cont = re.compile("^\s+\S+")
re_header_end = re.compile("^\s*$")
re_email = re.compile("([^<>\"\s]+)@(\S+\.[^<>\"\s]+)")
re_sender_name = re.compile("^From:\s+\"?([^<>\"]*)\"?\s*<?(\S*)@\S+\.\S+>?$")
re_auto_reply = re.compile("^Auto-Submitted: (auto-generated|auto-replied)", re.IGNORECASE)

fqdn = socket.getfqdn()
username = pwd.getpwuid(os.getuid())[0]

sender = None
recipient = None
to_line = None
from_line = None
sender_name = None
list_email = None
list_name = None
list_domain = None
email = []
email_filtered = []
logging = True

## Get/check args

if (args_ok()):
    sender = sys.argv[1]
    recipient = sys.argv[2]
else:
    raise ValueError('Missing or Invalid Arguments')

## Get email content

for line in sys.stdin:
    email.append(line)
if (len(email) == 0):
    raise ValueError('Missing Piped Data')

## Logging

if (logging):
    log_info(sender, recipient, email)

## Check if this is an auto-reply

auto_sub_line = get_header(email, "Auto-Submitted")
if (auto_sub_line and re_auto_reply.match(auto_sub_line)):
    exit()

## Get To: and From: lines

to_line = get_header(email, "To")
from_line = get_header(email, "From")
if (not to_line or not from_line):
    raise ValueError('Can not find To or From value in headers.')

## Get list info

if (re_email.search(to_line)):
    results = re_email.search(to_line)
    list_email = results.group(0)
    list_name = results.group(1)
    list_domain = results.group(2)
else:
    raise ValueError('Can not determine email list.')

## Get Sender Name

if (re_sender_name.match(from_line)):
    results = re_sender_name.search(from_line)
    sender_name = results.group(1) if results.group(1) else results.group(2)
else:
    raise ValueError('Can Not Determine Sender Name')

## If this is already filtered, add skip header and resubmit

listfix_email = f"{username}@{fqdn}"
if (sender == listfix_email):
    email.insert(0, "Listfix-Skip-Filter: yes\n")
    send_email(list_email, email)
    exit()

## Costruct Filtered Email

email_filtered.append(f"To: {list_email}\n")
email_filtered.append(f"From: \"{sender_name} via {list_name}\" <{list_email}>\n")
email_filtered.append(f"Reply-To: {list_email}\n")

exclude_headers = ["Subject", "Content-[^:]+", "MIME-Version"]
email_filtered.extend(strip_headers(email, exclude_headers))

send_email(list_email, email_filtered)
