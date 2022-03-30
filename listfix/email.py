import re
import os

re_header_cont = re.compile("^\s+\S+")
re_header_end = re.compile("^\s*$")
re_email_parts = re.compile("(\S+)@(\S+\.\S+)")
re_sender_info = re.compile("^From:\s+\"?([^<>\"]*?)\"?\s*<?(([^<>\"\s]+)@\S+\.[^<>\"\s]+)>?$")
re_auto_reply = re.compile("^Auto-Submitted: (auto-generated|auto-replied)", re.IGNORECASE)

class Email:

    def __init__(self, content):
        if (type(content) is not list):
            raise TypeError("Email content should be of list type.")
        if (len(content) == 0):
            raise IndexError("Email content cannot be empty list.")
        self.content = content[:]

    def get_content(self):
        return self.content[:]

    def get_header(self, header):
        header = header.lstrip().rstrip()
        if (header[-1] == ":"):
            header = header[0:-1]
        re_header = re.compile("^" + header + ": ", re.IGNORECASE)

        rval = None
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

        if (not rval):
            raise ValueError(f"Could not find header for '{header}'")
        return rval

    def get_sender_email(self):
        from_line = self.get_header("From")
        if (not re_sender_info.match(from_line)):
            raise ValueError(f"Could not extract sender email for header '{header}'")
        results = re_sender_info.search(from_line)
        sender_email = results.group(2)
        return sender_email

    def get_sender_name(self):
        from_line = self.get_header("From")
        if (not re_sender_info.match(from_line)):
            raise ValueError(f"Could not extract sender name for header '{header}'")
        results = re_sender_info.search(from_line)
        sender_name = results.group(1) if results.group(1) else results.group(3)
        return sender_name

    def check_auto_reply(self):
        auto_sub_line = None
        try:
            auto_sub_line = self.get_header("Auto-Submitted")
        except ValueError:
            return False
        if (auto_sub_line and re_auto_reply.match(auto_sub_line)):
            return True

    def strip_headers(self, exclude=[]):
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

    def add_header(self, header):
        header = header.rstrip() + "\n"
        self.content.append(header)

    def add_header_prepend(self, header):
        header = header.rstrip() + "\n"
        self.content.insert(0, header)

    def send(self, recipient):
        p = os.popen(f"/usr/sbin/sendmail -G -i {recipient}", "w")
        for line in self.content:
            p.write(line)
        p.close()
