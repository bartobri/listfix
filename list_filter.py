#!/usr/bin/python3

import sys
import os
import re

sender = "None"
recipient = "None"
if (len(sys.argv) > 2):
    sender = sys.argv[1]
    recipient = sys.argv[2]

#print(f"Sender: {sender}")
#print(f"Recipient: {recipient}")
#f = open("/tmp/filter.txt", "a")
#f.write(f"Sender: {sender}\n")
#f.write(f"Recipient: {recipient}\n")
#f.close()

orig_to = ""
orig_from = ""
list_email = ""
list_name = ""
list_domain = ""

stdin= []
for line in sys.stdin:
    if (list_email == "" and line[0:4] == "To: "):
        orig_to = line[4:].rstrip()
        list_email = re.search("\S+@\S+\.\S+", orig_to).group()
        if (list_email[-1] == ","):
            list_email = list_email[0:-1]
        if (list_email[0] == "\"" and list_email[-1] == "\""):
            list_email = list_email[1:-1]
        elif (list_email[0] == "<" and list_email[-1] == ">"):
            list_email = list_email[1:-1]
        list_name = re.search("^[^@]+", list_email).group()
        list_domain = re.search("^[^@]+@(.+)$", list_email).group(1)
    stdin.append(line)

sender_name = ""
for line in stdin:
    if (sender_name == "" and line[0:6] == "From: "):
        orig_from = line[6:].rstrip()
        if (re.search("^\"[^\"]+\"", orig_from)):
            sender_name = re.search("^\"([^\"]+)\"", orig_from).group(1)
        elif (re.search("^[^<]+ <", orig_from)):
            sender_name = re.search("^([^<]+) <", orig_from).group(1)
        else:
            sender_name = re.search("(\S+)@\S+\.\S+", orig_from).group(1)
            if (sender_name[0] == "\"" or sender_name[0] == "<"):
                sender_name = sender_name[1:]

for line in stdin:
    if (re.search("^Auto-Submitted: auto-generated", line, re.IGNORECASE)):
        exit()
    if (re.search("^Auto-Submitted: auto-replied", line, re.IGNORECASE)):
        exit()
    if (re.search("^\s*$", line)):
        break

## We add the filter skip header after the from line had been changed
## and reinjected. This is necessary to get the dkim milter to run
## for the new "From" header. Otherwise it doesn't run.
contents = []
if (re.search(list_email, orig_from)):
    contents.append(f"List-Skip-Filter: yes\n")
    for line in stdin:
        contents.append(line)
else:
    contents.append(f"To: {list_email}\n")
    contents.append(f"From: \"{sender_name} via {list_name}\" <{list_email}>\n")
    contents.append(f"Reply-To: {list_email}, {sender}\n")

    in_header = 1
    included = 0
    for line in stdin:
        if (in_header == 1):
            if (re.search("^\s+\S+", line) and included == 1):
                contents.append(line)
                continue

            included = 0
            if (re.search("^Subject: ", line)):
                contents.append(line)
                included = 1
            elif (re.search("^Content-", line)):
                contents.append(line)
                included = 1
            elif (re.search("^\s*$", line)):
                contents.append(line)
                in_header = 0
        else:
            contents.append(line)

    #found_from = 0
    #found_to = 0
    #for line in stdin:
    #    if (found_from == 0 and line[0:6] == "From: "):
    #        line = f"From: \"{sender_name} via {list_name}\" <{list_email}>\n"
    #        contents.append(f"Reply-To: {sender}, {list_email}\n")
    #        found_from = 1
    #    elif (found_to == 0 and line[0:4] == "To: "):
    #        line = f"To: {list_email}\n"
    #        found_to = 1
    #    contents.append(line)

#for line in contents:
#    print(line, end = "")

p = os.popen(f"/usr/sbin/sendmail -G -i {list_email}", "w")
for line in contents:
    p.write(line)
p.close()
