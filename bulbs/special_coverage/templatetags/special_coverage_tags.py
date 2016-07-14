from django import template

register = template.Library()


@register.inclusion_tag('special_coverage/bulbs_sc_landing.html', takes_context=True)
def special_coverage_landing_partial(context, twitter_handle, share_message, share_style):
    context['twitter_handle'] = twitter_handle
    context['share_message'] = share_message
    context['share_style'] = share_style
    return context
