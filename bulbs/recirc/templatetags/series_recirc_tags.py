from django import template

register = template.Library()


@register.inclusion_tag('recirc/series-recirc.html', takes_context=True)
def series_recirc_widget(context):
    return context
