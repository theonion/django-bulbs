from .parser import parse_body


def transform(html, renderer):
    return renderer.generate_body(parse_body(html))
