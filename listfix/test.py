import unittest
import os
import listfix

from os.path import exists
from listfix import DB, Log

class Test(unittest.TestCase):

    def run_test(self):
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
        unittest.TextTestRunner().run(suite)

    def setUp(self):

        ## db setup
        self.db_name = "/tmp/test.sqlite3"
        if (exists(self.db_name)):
            os.remove(self.db_name)

        ## log setup
        self.log_name = "/tmp/test.log"
        if (exists(self.log_name)):
            os.remove(self.log_name)

    def test_db(self):

        list_id = None
        list_name = "List Name"
        list_email = "test@test.com"
        recipient_name = "Recipient Name"
        recipient_email = "test@recipient.com"

        ## init
        db = DB(self.db_name)
        self.assertTrue(type(db) is listfix.db.DB)
        self.assertTrue(exists(self.db_name))

        ## create_list()
        db.create_list(list_email, list_name)
        row = db.db.execute("select id, name, email from lists").fetchone()
        list_id = row[0]
        self.assertEqual(row[1], list_name)
        self.assertEqual(row[2], list_email)

        ## check_list_exists()
        self.assertTrue(db.check_list_exists(list_email))

        ## get_list_id()
        self.assertEqual(list_id, db.get_list_id(list_email))

        ## get_list_name()
        self.assertEqual(list_name, db.get_list_name(list_email))

        ## get_lists()
        self.assertIn(list_email, db.get_lists())

        ## create_recipient()
        db.create_recipient(list_email, recipient_email, recipient_name)
        row = db.db.execute("select id, list_id, name, email from recipients").fetchone()
        recipient_id = row[0]
        self.assertEqual(row[1], list_id)
        self.assertEqual(row[2], recipient_name)
        self.assertEqual(row[3], recipient_email)

        ## check_recipient_exists()
        self.assertTrue(db.check_recipient_exists(list_email, recipient_email))

        ## get_recipient_id()
        self.assertEqual(recipient_id, db.get_recipient_id(list_email, recipient_email))

        ## get_recipient_name()
        self.assertEqual(recipient_name, db.get_recipient_name(list_email, recipient_email))

        ## get_list_recipients()
        self.assertIn(recipient_email, db.get_list_recipients(list_email))

        ## destroy_recipient()
        db.destroy_recipient(list_email, recipient_email)
        self.assertNotIn(recipient_email, db.get_list_recipients(list_email))

        ## destroy_list()
        db.destroy_list(list_email)
        self.assertFalse(db.check_list_exists(list_email))

        ## close
        db.close()
        os.remove(self.db_name)

    def test_log(self):

        test_type = "TEST"
        test_text = "This is a test"
        log = Log(self.log_name)

        ## write()
        log.write(test_type, test_text)
        f = open(self.log_name, "r")
        last_line = f.readlines()[-1]
        self.assertEqual(last_line[0:6], "[" + test_type + "]")
        self.assertEqual(last_line[-15:-1], test_text)
        f.close()

        ## info()
        log.info(test_text)
        f = open(self.log_name, "r")
        last_line = f.readlines()[-1]
        self.assertEqual(last_line[0:6], "[INFO]")
        self.assertEqual(last_line[-15:-1], test_text)
        f.close()

        ## error()
        log.error(test_text)
        f = open(self.log_name, "r")
        last_line = f.readlines()[-1]
        self.assertEqual(last_line[0:7], "[ERROR]")
        self.assertEqual(last_line[-15:-1], test_text)
        f.close()

        ## debug()
        log.debug(test_text)
        f = open(self.log_name, "r")
        last_line = f.readlines()[-1]
        self.assertEqual(last_line[0:7], "[DEBUG]")
        self.assertEqual(last_line[-15:-1], test_text)
        f.close()