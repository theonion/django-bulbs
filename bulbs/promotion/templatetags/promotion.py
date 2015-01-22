import operator

from django import template
from django.template.base import parse_bits, Variable, VariableDoesNotExist
from django.template.defaulttags import ForNode

from bulbs.promotion.models import PZone


register = template.Library()


class PZoneSequence(object):

    def __init__(self, pzone_name, slice_string=None, apply=True):
        self.pzone_name = pzone_name
        if slice_string:
            bits = []
            for x in slice_string.split(':'):
                if len(x) == 0:
                    bits.append(None)
                else:
                    bits.append(int(x))
            self.slice = slice(*bits)
        else:
            self.slice = None

        self.apply = apply

    def resolve(self, context, ignore_failures=False):
        
        try:
            when = Variable("pzone_preview").resolve(context)
            pzone = PZone.objects.preview(name=self.pzone_name, when=when)
        except VariableDoesNotExist:
            pzone = PZone.objects.applied(name=self.pzone_name)
        if self.slice:
            return pzone[self.slice]
        else:
            return pzone


@register.tag('forpzone')
def do_pzone(parser, token):
    """

    {% forpzone "homepage" slice=":3" %}
        <h1>
            <a href="{{ content.get_absolute_url }}">{{ content.title }}</a>
        </h1>
        <span>{{ content.description }}</span>
    {% endforpzone %}

    """

    bits = token.split_contents()

    if len(bits) < 2:
        raise TemplateSyntaxError("'pzone' statements should have at least two"
                                  " words: %s" % token.contents)

    nodelist_loop = parser.parse(("endforpzone","empty"))
    token = parser.next_token()
    if token.contents == 'empty':
        nodelist_empty = parser.parse(('endfor',))
        parser.delete_first_token()
    else:
        nodelist_empty = None

    params = ["slice", "name", "apply"]
    args, kwargs = parse_bits(parser, bits, params, None, None, [], False, "forpzone")
    
    pzone_name = kwargs["name"].resolve({})

    slice_string = None
    if "slice" in kwargs:
        slice_string = kwargs["slice"].resolve({})
        slice_bits = []
        for x in slice_string.split(':'):
            if len(x) == 0:
                slice_bits.append(None)
            else:
                slice_bits.append(int(x))
        slice_object = slice(*slice_bits)

    apply = False
    if "apply" in kwargs:
        apply = kwargs["apply"].resolve({})

    sequence = PZoneSequence(pzone_name, slice_string=slice_string, apply=apply)

    loopvars = ["content"]
    is_reversed = False

    return ForNode(loopvars, sequence, is_reversed, nodelist_loop, nodelist_empty)