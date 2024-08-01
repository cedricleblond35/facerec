import unittest
import classes.url as URL


class TestUrl(unittest.TestCase):
    def test_something(self):
        URL.Url.get_file()
        self.assertEqual(True, False)



if __name__ == '__main__':
    unittest.main()
