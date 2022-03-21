#!/usr/bin/python3

import sys
import os
import re

########################
## Variable Defs
########################

local_domains = [
    "cityviewgr.com",
    "brianbarto.info"
]

email_lists = {
    "test@cityviewgr.com" : [
        "bartobrian@gmail.com",
        "bartobrian@outlook.com",
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

re_header_cont = re.compile("^\s+\S+")
re_header_end = re.compile("^\s*$")
re_email_arg = re.compile("([^<>\"\s]+)@(\S+\.[^<>\"\s]+)")
re_email_to = re.compile("[<, ](([^<>\"\s\,]+)@([^<>\"\s\,]+\.[^<>\"\s\,]+))")
re_email_parts = re.compile("(\S+)@(\S+\.\S+)")
re_sender_name = re.compile("^From:\s+\"?([^<>\"]*)\"?\s*<?(\S*)@\S+\.\S+>?$")
re_auto_reply = re.compile("^Auto-Submitted: (auto-generated|auto-replied)", re.IGNORECASE)

sender = None
list_email = None
list_name = None
list_domain = None
sender_name = None
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
    list_email = sys.argv[2]
    if (not sender or not list_email):
        raise ValueError('Missing or Invalid Arguments')
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
    log_info(sender, list_email, email)

## Check if this is an auto-reply

auto_sub_line = get_header(email, "Auto-Submitted")
if (auto_sub_line and re_auto_reply.match(auto_sub_line)):
    exit()

## Verify list_email is a known list

if (list_email not in email_lists.keys()):
    raise ValueError(f"Undefined Email List: {list_email}")

list_name = re_email_parts.search(list_email).group(1)
list_domain = re_email_parts.search(list_email).group(2)

## Get Sender Name

from_line = get_header(email, "From")
if (from_line):
    if (re_sender_name.match(from_line)):
        results = re_sender_name.search(from_line)
        sender_name = results.group(1) if results.group(1) else results.group(2)
        sender_name = sender_name.rstrip()
    else:
        raise ValueError('Can Not Determine Sender Name')
else:
    raise ValueError('Can Not Find \'From\' Line in Email')

## Costruct Filtered Email

email_filtered.append(f"From: \"{sender_name} via {list_name}\" <{list_email}>\n")
email_filtered.append(f"Reply-To: {list_email}\n")
exclude_headers = ["To", "Cc", "Subject", "Content-[^:]+", "MIME-Version"]
email_filtered.extend(strip_headers(email, exclude_headers))

## Send emails

for recipient in email_lists[list_email]:
    send_email(recipient, email_filtered)
