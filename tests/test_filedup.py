import unittest
import os


class TestFileDup(unittest.TestCase):

    def set_up(self):
        # override standard db location
        DATABASE_FILE = '/tmp/filedup.db'
        pass

    def tearDown(self):
        # remove test database
        os.remove('/tmp/filedup.db')
        pass

    def test_sum(self):
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")

    def test_sum_tuple(self):
        self.assertEqual(sum((1, 2, 2)), 6, "Should be 6")

if __name__ == '__main__':
    unittest.main()

