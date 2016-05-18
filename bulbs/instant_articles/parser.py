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
        caption = tag.find('span', class_='caption')
        return {'betty': {'image_id': tag.attrs['data-image-id'],
                          'caption': caption.text if caption else ''}}


def parse_facebook(tag):
    # Grab iframe, strip out style attribute
    # return {'facebook': {'iframe': iframe}}
    pass


def parse_instagram(tag):
    # Just pass along ID
    # if tag.name == 'iframe' and 'instagram-media' in tag.get('class'):
    #     return {'instagram': {'iframe': str(tag)}}
    # return {'instagram': {'instagram_id': ###}}
    pass


def parse_text(tag):
    # return {'text': {'raw': TEXT}}
    pass


def parse_twitter(tag):
    # Just pass blockquote tag verbatim
    # return {'twitter': {'blockquote': blockquote}}
    pass


def parse_youtube(tag):
    # return {'youtube': {'video_id': ###}}
    pass


def parse_onion_video(tag):
    # return {'onion_video': {'iframe': iframe}}
    pass


def parse_vimeo(tag):
    # return {'vimeo': {'iframe': iframe}}
    pass


def parse_soundcloud(tag):
    # return {'soundcloud': {'iframe': iframe}}
    pass


def parse_imgur(tag):
    # return {'imgur': {'iframe': iframe}}
    pass


PARSERS = [
    # Sorted by precedence
    parse_betty,
    parse_facebook,
    parse_instagram,
    parse_twitter,
    parse_youtube,

    parse_text,
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
        matched = parse_tag(tag)
        if matched:
            components.append(matched)

    return components
