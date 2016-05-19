import re

from bs4 import BeautifulSoup
import six


def has_attr(attr):
    """Useful wrapper for filtering w/ BeautifulSoup 'find' methods

    ex:  tag.find('iframe', has_attr('src'))
    """
    def inner_has_attr(tag):
        return tag and tag.has_attr(attr)
    return inner_has_attr


def clean_iframe(iframe):
    # Strip out style attribute
    if iframe.has_attr('style'):
        del iframe.attrs['style']
    return iframe


def parse_betty(tag):
    if (tag.name == 'div' and
        'image' in tag.get('class', {}) and
            tag.attrs.get('data-type') == 'image' and
            tag.has_attr('data-image-id')):
        caption = tag.find('span', class_='caption')
        return {'betty': {'image_id': tag.attrs['data-image-id'],
                          'caption': caption.text if caption else ''}}


def parse_facebook(tag):
    if tag.name == 'div' and tag.attrs.get('data-type') == 'embed':
        iframe = tag.find('iframe')
        if iframe:
            # Only way to identify is by 'src' URL
            if iframe.attrs.get('src', '').startswith('https://www.facebook.com/plugins/'):
                iframe = clean_iframe(iframe)
                return {'facebook': {'iframe': six.text_type(iframe)}}


def parse_instagram(tag):
    # Just pass along ID
    # if tag.name == 'iframe' and 'instagram-media' in tag.get('class'):
    #     return {'instagram': {'iframe': six.text_type(tag)}}
    # return {'instagram': {'instagram_id': ###}}

    INSTAGRAM_ID_REGEX = re.compile('https?://www.instagram.com/p/([^/]+)/')

    if tag.name == 'div' and tag.attrs.get('data-type') == 'embed':
        # IFRAME
        iframe = tag.find('iframe', 'instagram-media', has_attr('src'))
        if iframe:
            m = INSTAGRAM_ID_REGEX.match(iframe['src'])
            if m:
                return {'instagram': {'instagram_id': m.group(1)}}

        # Blockquote
        blockquote = tag.find('blockquote', 'instagram-media')
        if blockquote:
            for a in blockquote.findAll('a'):
                if a.has_attr('href'):
                    m = INSTAGRAM_ID_REGEX.match(a['href'])
                    if m:
                        return {'instagram': {'instagram_id': m.group(1)}}


def parse_text(tag):
    if tag.name == 'p':
        return {'text': {'raw': six.text_type(tag)}}


def parse_twitter(tag):
    if tag.name == 'div' and tag.attrs.get('data-type') == 'embed':
        blockquote = tag.find('blockquote', class_='twitter-tweet')
        if blockquote:
            return {'twitter': {'blockquote': six.text_type(blockquote)}}


def parse_youtube(tag):
    if tag.name == 'div':
        # No-IFRAME - grab ID from attribute
        if tag.attrs.get('data-type') == 'youtube':
            video_id = tag.attrs.get('data-youtube-id')
            if video_id:
                return {'youtube': {'video_id': video_id}}
        # IFRAME - parse ID from 'src' attribute
        if tag.attrs.get('data-type') == 'embed':
            iframe = tag.find('iframe')
            if iframe:
                m = re.match('https?://www.youtube.com/embed/(.+)', iframe.attrs['src'])
                if m:
                    return {'youtube': {'video_id': m.group(1)}}


def parse_onion_video(tag):
    if tag.name == 'div' and tag.attrs.get('data-type') == 'embed':
        iframe = tag.find('iframe', class_='onionstudios-playlist')
        if iframe:
            iframe = clean_iframe(iframe)
            return {'onion_video': {'iframe': six.text_type(iframe)}}


def parse_vimeo(tag):
    # return {'vimeo': {'iframe': iframe}}
    pass


def parse_soundcloud(tag):
    # return {'soundcloud': {'iframe': iframe}}
    pass


def parse_imgur(tag):
    if tag.name == 'div' and tag.attrs.get('data-type') == 'embed':
        iframe = tag.find('iframe', class_='imgur-embed-iframe-pub')
        if iframe:
            iframe = clean_iframe(iframe)
            return {'imgur': {'iframe': six.text_type(iframe)}}


PARSERS = [
    # Sorted by precedence (initially alphabically since no precedence required for now)
    parse_betty,
    parse_facebook,
    parse_facebook,
    parse_imgur,
    parse_instagram,
    parse_onion_video,
    parse_soundcloud,
    parse_twitter,
    parse_vimeo,
    parse_youtube,
    # Simple <p> tags have lowest priority
    parse_text,
]


def parse_tag(tag):
    for parser in PARSERS:
        match = parser(tag)
        if match:
            return match


def parse_children(parent):
    """Recursively parse child tags until match is found"""

    components = []
    for tag in parent.children:
        matched = parse_tag(tag)
        if matched:
            components.append(matched)
        elif hasattr(tag, 'contents'):
            parse_children(tag)
    return components


def parse_body(html):
    return parse_children(BeautifulSoup(html))
