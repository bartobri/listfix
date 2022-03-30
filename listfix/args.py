import re

re_email_arg = re.compile("([^<>\"\s]+)@(\S+\.[^<>\"\s]+)")

class Args:

    def __init__(self, args):
        if (type(args) is not list):
            raise TypeError("Arguments should be of list type.")
        if (len(args) < 2):
            raise IndexError("Missing command argument.")
        self.args = args
        self.command = args[1]

    def get_command(self):
        return self.command

    def get_list_email(self):
        if (len(self.args) < 3):
            raise IndexError(f"Missing argument(s) for '{self.command}' command.")
        if (not re_email_arg.match(self.args[2])):
            raise ValueError(f"Invalid argument value: {self.args[2]}")
        return self.args[2]

    def get_list_name(self):
        if (len(self.args) < 4):
            raise IndexError(f"Missing argument(s) for '{self.command}' command.")
        return self.args[3]

    def get_recipient_email(self):
        if (len(self.args) < 4):
            raise IndexError(f"Missing argument(s) for '{self.command}' command.")
        if (not re_email_arg.match(self.args[3])):
            raise ValueError(f"Invalid argument value: {self.args[3]}")
        return self.args[3]

    def get_recipient_name(self):
        if (len(self.args) < 5):
            raise IndexError(f"Missing argument(s) for '{self.command}' command.")
        return self.args[4]

