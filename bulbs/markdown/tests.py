import os
from django.template import Context, Template

import unittest

TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), 'test_data')


class MarkdownTestCase(unittest.TestCase):
    def testMarkdownFilter(self):

        test_template = Template("""{% load markdown %}{{ string|markdown }}""")

        test_markown = open(os.path.join(TEST_DATA_PATH, 'simple_string.md'), 'r').read()
        test_rendered = open(os.path.join(TEST_DATA_PATH, 'simple_string.txt'), 'r').read()

        test_context = Context({"string": test_markown})

        rendered = test_template.render(test_context)
        self.assertEqual(rendered, test_rendered)
