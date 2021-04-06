import unittest
import os
import sys
from pathlib import Path
sys.path.append(str(Path('.').absolute().parent))
import filedup

class TestFileDup(unittest.TestCase):

    def set_up(self):
        # override standard db location
        DATABASE_FILE = '/tmp/filedup.db'
        pass

    def tearDown(self):
        # remove test database
        try:
            os.remove('/tmp/filedup.db')
        except FileNotFoundError:
            pass

    def test_get_DB_object(self):
        a = filedup.open_db()
        self.assertIsInstance(a, filedup.MyDB)

if __name__ == '__main__':
    unittest.main()

