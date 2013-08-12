from django import forms
from .models import Content


class DoctypeChoiceField(forms.ChoiceField):
    """Field for choosing amongst the doctypes of a given polymorphic model."""
    def __init__(self, model, exclude_base=False, *args, **kwargs):
        choices = [
            (doctype_id, klass.__name__) for doctype_id, klass in model.get_doctypes().items()
            if not exclude_base or klass != model
        ]
        super(DoctypeChoiceField, self).__init__(choices=choices)


class ContentModelTypeForm(forms.Form):
    """Form for choosing a Content subclass doctype."""
    doctype = DoctypeChoiceField(Content, exclude_base=True)

