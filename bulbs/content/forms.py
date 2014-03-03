from django import forms
from django.utils.functional import lazy

from .models import Content


def mapping_type_choices(model, exclude_base=True):
    def get_choices():
        mapping_type_models = model.get_mapping_type_models(exclude_base=exclude_base)
        choices = []
        for mapping_type_name, content_type in mapping_type_models:
            choices.append((mapping_type_name, content_type.name))
        return choices
    return get_choices


class ContentDoctypeForm(forms.Form):
    """Form for choosing a Content subclass doctype."""
    doctype = forms.ChoiceField(
        choices=lazy(mapping_type_choices(Content, exclude_base=True), list)(),
        label='Type'
    )
