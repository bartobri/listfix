import json
from os.path import exists

class DB:

    def __init__(self, path):
        self.json = {}
        self.path = path
        if (exists(path)):
            with open(path) as f:
                self.json = json.load(f)

    def check_list_exists(self, list_email):
        if (list_email in self.json.keys()):
            return True
        else:
            return False

    def create_list(self, list_email, list_name):
        if (self.check_list_exists(list_email)):
            raise ValueError(f"Email list already exists: {list_email}")
        self.json[list_email] = { 'name': list_name, 'recipients': {} }

    def get_lists(self):
        return list(self.json.keys())

    def get_list_name(self, list_email):
        if (not self.check_list_exists(list_email)):
            raise ValueError(f"Email list does not exist: {list_email}")
        return self.json[list_email]['name']

    def check_recipient_exists(self, list_email, recipient_email):
        if (not self.check_list_exists(list_email)):
            raise ValueError(f"Email list does not exist: {list_email}")
        if (recipient_email in self.json[list_email]['recipients'].keys()):
            return True
        else:
            return False

    def create_recipient(self, list_email, recipient_email, recipient_name):
        if (self.check_recipient_exists(list_email, recipient_email)):
            raise ValueError(f"Recipient already exists: {recipient_email}")
        self.json[list_email]['recipients'][recipient_email] = { 'name': recipient_name }

    def get_list_recipients(self, list_email):
        if (not self.check_list_exists(list_email)):
            raise ValueError(f"Email list does not exist: {list_email}")
        return list(self.json[list_email]['recipients'].keys())

    def get_recipient_name(self, list_email, recipient_email):
        if (not self.check_list_exists(list_email)):
            raise ValueError(f"Email list does not exist: {list_email}")
        if (not self.check_recipient_exists(list_email, recipient_email)):
            raise ValueError(f"Recipient does not exist: {recipient_email}")
        return self.json[list_email]['recipients'][recipient_email]['name']

    def destroy_recipient(self, list_email, recipient_email):
        if (not self.check_list_exists(list_email)):
            raise ValueError(f"Email list does not exist: {list_email}")
        if (not self.check_recipient_exists(list_email, recipient_email)):
            raise ValueError(f"Recipient does not exist: {recipient_email}")
        del self.json[list_email]['recipients'][recipient_email]

    def destroy_list(self, list_email):
        if (not self.check_list_exists(list_email)):
            raise ValueError(f"Email list does not exist: {list_email}")
        del self.json[list_email]

    def lower_emails(self):
        lists = self.get_lists()
        for x in lists:
            self.json[x.lower()] = self.json.pop(x)
        lists = self.get_lists()
        for x in lists:
            recipients = self.get_list_recipients(x)
            for y in recipients:
                self.json[x]['recipients'][y.lower()] = self.json[x]['recipients'].pop(y)

    def save(self):
        f = open(self.path, "w")
        json.dump(self.json, f, indent=4)
        f.close()