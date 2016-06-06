from .parser import parse_body


def transform(html, renderer):
    """Convert blob of body content HTML into another output format (ex: FB Instant Article).
    This wires up separate "parser" and "renderer" subsystems.
    """
    return renderer.generate_body(parse_body(html))
