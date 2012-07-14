from django.db import models
from django.contrib.admin import widgets as admin_widgets
from afns.markdown import widgets as markdown_widgets
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ['^afns\.apps\.markdown\.models\.MarkdownField'])
except ImportError:
    pass

class MarkdownField(models.TextField):
    """
    A large string field for HTML content. It uses the TinyMCE widget in
    forms.
    """
    def formfield(self, **kwargs):
        defaults = {'widget': markdown_widgets.Markdown}
        defaults.update(kwargs)

        # As an ugly hack, we override the admin widget
        if defaults['widget'] == admin_widgets.AdminTextareaWidget:
            defaults['widget'] = markdown_widgets.AdminMarkdown

        return super(MarkdownField, self).formfield(**defaults)