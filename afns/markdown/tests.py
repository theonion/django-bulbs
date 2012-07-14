from django.template import Context, Template

import unittest

class MarkdownTestCase(unittest.TestCase):
    def testMarkdownFilter(self):
        
        test_template = Template("""
        {% load markdown %}
        {{ string|markdown }}
        """)
        
        test_markown_string = """
        ### Test Headline
        
         - List Item One
         - List Item Two
         - List Item Three
         
        *Italic*
        
        **Bold** 
        """
        
        
        test_context = Context({"string": test_markown_string})
        
        rendered = test_template.render(test_context)
        
        print(rendered)