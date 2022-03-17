#!/usr/bin/python3

import sys
import socket
import pwd
import os
import re

########################
## Variable Defs
########################

email_lists = [ "test@cityviewgr.com",
                "board@cityviewgr.com",
                "association@cityviewgr.com",
                "residents@cityviewgr.com" ]

re_header_cont = re.compile("^\s+\S+")
re_header_end = re.compile("^\s*$")
re_email_arg = re.compile("([^<>\"\s]+)@(\S+\.[^<>\"\s]+)")
re_email_to = re.compile("[<, ](([^<>\"\s\,]+)@([^<>\"\s\,]+\.[^<>\"\s\,]+))")
re_sender_name = re.compile("^From:\s+\"?([^<>\"]*)\"?\s*<?(\S*)@\S+\.\S+>?$")
re_auto_reply = re.compile("^Auto-Submitted: (auto-generated|auto-replied)", re.IGNORECASE)

fqdn = socket.getfqdn()
username = pwd.getpwuid(os.getuid())[0]

sender = None
recipients = []
to_line = None
from_line = None
sender_name = None
list_email = None
list_name = None
list_domain = None
email = []
email_filtered = []
logging = True

########################
## Function Defs
########################

def args_ok():
    if (len(sys.argv) > 2):
        for arg in sys.argv[1:]:
            if (not re_email_arg.match(arg) or not re_email_arg.match(arg)):
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
    p.write(f"To: {to_email}\n")
    for line in email_contents:
        p.write(line)
    p.close()

def log_info(sender, recipients, lines):

    f = open("/tmp/listfix_log.txt", "a")
    f.write(f"Postfix Sender: {sender}\n")

    for recipient in recipients:
        f.write(f"Postfix Recipient: {recipient}\n")

    for line in lines:
        if (re_header_end.match(line)):
                break

        f.write(line)

    f.write("\n")
    f.close()

def log_line(line):

    line = line.rstrip()

    f = open("/tmp/listfix_log.txt", "a")
    f.write(f"[Log Line] {line}\n")
    f.close()


########################
## Main Program
########################

## Get/check args

if (args_ok()):
    sender = sys.argv[1]
    for arg in sys.argv[2:]:
        recipients.append(arg)
else:
    raise ValueError('Missing or Invalid Arguments')

## Get email content

for line in sys.stdin:
    email.append(line)
if (len(email) == 0):
    raise ValueError('Missing Piped Data')

## Logging

if (logging):
    for arg in sys.argv[1:]:
        log_line(arg)
    log_info(sender, recipients, email)

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

if (re_email_to.search(to_line)):
    results = re_email_to.findall(to_line)
    for r in results:
        for email_list in email_lists:
            print(f"Checking result = {r} list = {email_list}")
            if (r[0] == email_list):
                list_email = r[0]
                list_name = r[1]
                list_domain = r[2]
            if (list_email):
                break
        if (list_email):
            break
    if (not list_email):
        raise ValueError('No email list recipient found.')
else:
    raise ValueError('Can not determine email list.')

## Get Sender Name

if (re_sender_name.match(from_line)):
    results = re_sender_name.search(from_line)
    sender_name = results.group(1) if results.group(1) else results.group(2)
    sender_name = sender_name.rstrip()
else:
    raise ValueError('Can Not Determine Sender Name')

## Costruct Filtered Email

email_filtered.append(f"From: \"{sender_name} via {list_name}\" <{list_email}>\n")
email_filtered.append(f"Reply-To: {list_email}\n")
exclude_headers = ["Subject", "Content-[^:]+", "MIME-Version"]
email_filtered.extend(strip_headers(email, exclude_headers))

## Send emails

for recipient in recipients:
    send_email(recipient, email_filtered)
