from django import template
from bulbs.utils.methods import get_overridable_template_name

register = template.Library()

# Liveblog Template
liveblog_template_name = get_overridable_template_name(
    'liveblog/bulbs_liveblog.html',
    'liveblog/liveblog_override.html')


@register.inclusion_tag(liveblog_template_name, takes_context=True)
def liveblog_partial(context):
    return context

# Entries Template
entries_template_name = get_overridable_template_name(
    'liveblog/entries.html',
    'liveblog/entries_override.html',
    must_inherit=False)


@register.inclusion_tag(entries_template_name, takes_context=True)
def liveblog_entries_partial(context):
    return context

# Recirc Template
recirc_template_name = get_overridable_template_name(
    'liveblog/recirc.html',
    'liveblog/recirc_override.html',
    must_inherit=False)


@register.inclusion_tag(recirc_template_name, takes_context=True)
def liveblog_recirc_partial(context):
    return context

# Sharetools Template
entry_sharetools_template_name = get_overridable_template_name(
    'liveblog/entry_sharetools.html',
    'liveblog/entry_sharetools_override.html',
    must_inherit=False)


@register.inclusion_tag(entry_sharetools_template_name, takes_context=True)
def liveblog_entry_sharetools_partial(context):
    return context
