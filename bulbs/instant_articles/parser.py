from __future__ import print_function

from bs4 import BeautifulSoup


def has_attr(attr):
    def inner_has_attr(tag):
        return tag.has_attr(attr)
    return inner_has_attr


def parse_betty(tag):
    if (tag.name == 'div' and
        'image' in tag.get('class', {}) and
            tag.attrs['data-type'] == 'image' and
            tag.has_attr('data-image-id')):
        return {'betty': {'image_id': tag.attrs['data-image-id']}}


def parse_instagram(tag):
    if tag.name == 'iframe' and 'instagram-media' in tag.get('class'):
        return {'instagram': {'iframe': str(tag)}}


PARSERS = [
    # Sorted by precedence
    parse_betty,
    parse_instagram,
]


def parse_tag(tag):
    for parser in PARSERS:
        match = parser(tag)
        if match:
            return match


def parse_body(html):
    components = []

    soup = BeautifulSoup(html)
    for tag in soup.recursiveChildGenerator():
        print(tag)
        matched = parse_tag(tag)
        if matched:
            components.append(matched)

    return components
