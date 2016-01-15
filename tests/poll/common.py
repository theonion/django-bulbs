import os

SECRETS = {
    'sodahead/token': os.environ.get("SODAHEAD_API_TOKEN", "")
}
