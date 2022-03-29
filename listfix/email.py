import re
import os

re_header_cont = re.compile("^\s+\S+")
re_header_end = re.compile("^\s*$")
re_email_parts = re.compile("(\S+)@(\S+\.\S+)")
re_sender_info = re.compile("^From:\s+\"?([^<>\"]*?)\"?\s*<?(([^<>\"\s]+)@\S+\.[^<>\"\s]+)>?$")
re_auto_reply = re.compile("^Auto-Submitted: (auto-generated|auto-replied)", re.IGNORECASE)

class Email:

    def __init__(self, content):
        self.content = []

        if (type(content) is list):
            if (len(content) > 0):
                self.content = content[:]
            else:
                return False
        else:
            return False

    def get_content(self):
        return self.content[:]


    def get_header(self, header):
        rval = None

        header = header.rstrip()
        if (header[-1] == ":"):
            header = header[0:-1]

        re_header = re.compile("^" + header + ": ", re.IGNORECASE)

        append_next = False
        in_header = True
        for line in self.content:
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

    def get_sender_email(self):
        sender_email = None

        from_line = self.get_header("From")
        if (from_line):
            if (re_sender_info.match(from_line)):
                results = re_sender_info.search(from_line)
                sender_email = results.group(2)
            else:
                return False
        else:
            return False

        return sender_email

    def get_sender_name(self):
        sender_name = None

        from_line = self.get_header("From")
        if (from_line):
            if (re_sender_info.match(from_line)):
                results = re_sender_info.search(from_line)
                sender_name = results.group(1) if results.group(1) else results.group(3)
            else:
                return False
        else:
            return False

        return sender_name

    def is_auto_reply(self):
        auto_sub_line = self.get_header("Auto-Submitted")
        if (auto_sub_line and re_auto_reply.match(auto_sub_line)):
            return True
        return False

    def strip_headers(self, exclude):
        stripped_content = []

        append_next = False
        in_header = True
        for line in self.content:
            if (in_header):
                if (re_header_cont.match(line) and append_next):
                    stripped_content.append(line)
                    continue

                if (re_header_end.match(line)):
                    stripped_content.append(line)
                    in_header = False
                    continue

                append_next = False
                for ex in exclude:
                    if (re.match("^" + ex + ": ", line, re.IGNORECASE)):
                        stripped_content.append(line)
                        append_next = True
                        break
            else:
                stripped_content.append(line)

        self.content = stripped_content[:]

        return True

    def add_header(self, header):
        header = header.rstrip() + "\n"
        self.content.append(header)
        return True

    def add_header_prepend(self, header):
        header = header.rstrip() + "\n"
        self.content.insert(0, header)
        return True

    def send(self, recipient):
        p = os.popen(f"/usr/sbin/sendmail -G -i {recipient}", "w")
        for line in self.content:
            p.write(line)
        p.close()
        return True
