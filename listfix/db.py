import sqlite3

class DB:

    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.check_tables()

    def check_tables(self):
        row = self.db.execute("select count(*) from sqlite_master where type = 'table' and name = 'lists'").fetchone()
        if (not row[0]):
            self.db.execute("create table lists(id INTEGER primary key autoincrement, name text, email text)")
            self.db.commit()
        row = self.db.execute("select count(*) from sqlite_master where type = 'table' and name = 'recipients'").fetchone()
        if (not row[0]):
            self.db.execute("create table recipients(id INTEGER primary key autoincrement, list_id int, name text, email text)")
            self.db.commit()

    def check_list_exists(self, list_email):
        try:
            self.get_list_id(list_email)
        except ValueError:
            return False
        return True

    def get_lists(self):
        lists = []
        rows = self.db.execute("SELECT email FROM lists")
        for row in rows:
            lists.append(row[0])
        return lists

    def get_list_id(self, list_email):
        row = self.db.execute("SELECT id FROM lists WHERE email = ?", [list_email]).fetchone()
        if (not row):
            raise ValueError(f"Email list does not exist: {list_email}")
        return row[0]

    def get_list_name(self, list_email):
        row = self.db.execute("SELECT name FROM lists WHERE email = ?", [list_email]).fetchone()
        if (not row):
            raise ValueError(f"Email list does not exist: {list_email}")
        return row[0]
    
    def get_list_recipients(self, list_email):
        recipients = []
        list_id = self.get_list_id(list_email)
        rows = self.db.execute("SELECT email FROM recipients WHERE list_id = ?", [list_id])
        for row in rows:
            recipients.append(row[0])
        return recipients

    def create_list(self, list_email, list_name):
        if (self.check_list_exists(list_email)):
            raise ValueError(f"Email list already exists: {list_email}")
        self.db.execute("INSERT INTO lists (name, email) VALUES (?,?)", [list_name, list_email])
        self.db.commit()

    def destroy_list(self, list_email):
        list_id = self.get_list_id(list_email)
        self.db.execute("DELETE FROM lists WHERE id = ?", [list_id])
        self.db.execute("DELETE FROM recipients WHERE list_id = ?", [list_id])
        self.db.commit()

    def check_recipient_exists(self, list_email, recipient_email):
        try:
            self.get_recipient_id(list_email, recipient_email)
        except ValueError:
            return False
        return True

    def get_recipient_id(self, list_email, recipient_email):
        list_id = self.get_list_id(list_email)
        row = self.db.execute("SELECT id FROM recipients WHERE list_id = ? and email = ?", [list_id, recipient_email]).fetchone()
        if (not row):
            raise ValueError(f"Recipient does not exist: {recipient_email}")
        return row[0]

    def get_recipient_name(self, list_email, recipient_email):
        list_id = self.get_list_id(list_email)
        row = self.db.execute("SELECT name FROM recipients WHERE list_id = ? and email = ?", [list_id, recipient_email]).fetchone()
        if (not row):
            raise ValueError(f"Recipient does not exist: {recipient_email}")
        return row[0]

    def create_recipient(self, list_email, recipient_email, recipient_name):
        if (self.check_recipient_exists(list_email, recipient_email)):
            raise ValueError(f"Recipient already exists: {recipient_email}")
        list_id = self.get_list_id(list_email)
        self.db.execute("INSERT INTO recipients (list_id, name, email) VALUES (?,?,?)", [list_id, recipient_name, recipient_email])
        self.db.commit()

    def destroy_recipient(self, list_email, recipient_email):
        list_id = self.get_list_id(list_email)
        recipient_id = self.get_recipient_id(list_email, recipient_email)
        self.db.execute("DELETE FROM recipients WHERE id = ?", [recipient_id])
        self.db.commit()

    def close(self):
        self.db.close()