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

    def get_headers(self):
        headers = []
        for line in self.content:
            if (re_header_end.match(line)):
                break
            headers.append(line)
        return headers

    def get_header(self, prefix):
        header = None
        prefix = prefix.lstrip().rstrip()
        if (prefix[-1] == ":"):
            prefix = prefix[0:-1]
        re_header = re.compile("^" + prefix + ": ", re.IGNORECASE)

        headers = self.get_headers();
        for i, line in enumerate(headers):
            if (re_header.match(line)):
                header = line.rstrip()
                i += 1
                while (i < len(headers) and re_header_cont.match(headers[i])):
                    header = header + "\n" + headers[i].rstrip()
                    i += 1
                break

        if (not header):
            raise ValueError(f"Could not find header for '{prefix}'")
        return header

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

    def strip_headers(self, exclude):
        ex_string = "|".join(exclude)
        re_exclude = re.compile("^(" + ex_string + "): ", re.IGNORECASE)

        j = 0
        header_cont = False
        for i, header in enumerate(self.get_headers()):
            if (re_exclude.match(header)):
                header_cont = True
                continue
            elif (header_cont == True and re_header_cont.match(header)):
                continue
            else:
                del self.content[i-j]
                header_cont = False
                j += 1

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
