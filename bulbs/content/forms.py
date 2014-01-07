from django import forms

from .models import Content


class DoctypeChoiceField(forms.ChoiceField):
    """Field for choosing amongst the doctypes of a given polymorphic model."""
    def __init__(self, model, exclude_base=False, *args, **kwargs):
        mapping_type_models = model.get_mapping_type_models(exclude_base=exclude_base)
        choices = []
        for mapping_type_name, content_type in mapping_type_models:
            choices.append((mapping_type_name, content_type.name))
        super(DoctypeChoiceField, self).__init__(choices=choices, *args, **kwargs)


class ContentDoctypeForm(forms.Form):
    """Form for choosing a Content subclass doctype."""
    doctype = DoctypeChoiceField(Content, exclude_base=True, label='Type')

