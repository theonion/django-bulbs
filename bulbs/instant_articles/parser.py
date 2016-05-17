from __future__ import print_function

from bs4 import BeautifulSoup


def has_attr(attr):
    def inner_has_attr(tag):
        return tag.has_attr(attr)
    return inner_has_attr


def parse_betty(element):
    if element.name == 'figure':
        div = element.find('div', has_attr('data-image-id'), class_='image')
        if div:
            return {'betty': {'image_id': div.attrs['data-image-id']}}


def parse_instagram(element):
    if element.name == 'iframe' and 'instagram-media' in element.get('class'):
        return {'instagram': {'iframe': str(element)}}


PARSERS = [
    # Sorted by precedence
    parse_betty,
    parse_instagram,
]


def parse_element(element):
    for parser in PARSERS:
        match = parser(element)
        if match:
            return match


def parse_content(content):
    components = []

    soup = BeautifulSoup(content)
    for element in soup.recursiveChildGenerator():
        print(element)
        matched = parse_element(element)
        if matched:
            components.append(matched)

    return components
