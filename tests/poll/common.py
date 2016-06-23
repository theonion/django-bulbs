import os

SECRETS = {
    'sodahead/token': {'value': os.environ.get("SODAHEAD_API_TOKEN", "")}
}
