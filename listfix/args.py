import re

re_email_arg = re.compile("([^<>\"\s]+)@(\S+\.[^<>\"\s]+)")

class Args:

    def __init__(self, args):
        self.args = []
        self.command = None

        if (type(args) is list):
            if (len(args) >= 2):
                self.args = args
                self.command = args[1]
            else:
                raise IndexError("Missing command argument.")
        else:
            raise TypeError("Arguments should be of list type.")

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

