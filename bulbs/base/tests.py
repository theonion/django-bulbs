from django.utils import unittest

class PoniesTestCase(unittest.TestCase):
    def test_works(self):
        self.assertEqual(1, 1)

    def test_fails(self):
        self.assertEqual(1, 2)

