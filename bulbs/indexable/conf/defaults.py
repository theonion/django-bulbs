ES_URLS = ["http://localhost:9200"]

ES_SETTINGS = {
    "index": {
        "analysis": {
            "analyzer": {
                "autocomplete": {
                    "type": "custom",
                    "tokenizer": "edge_ngram_tokenizer",
                    "filter": ["asciifolding", "lowercase"]
                },
                "html": {
                    "type": "custom",
                    "char_filter": ["html_strip"],
                    "tokenizer": "standard",
                    "filter": ["asciifolding", "lowercase", "stop", "snowball"]
                }
            },
            "tokenizer": {
                "edge_ngram_tokenizer": {
                    "type" : "edgeNGram",
                    "min_gram" : "3",
                    "max_gram" : "10",
                    "token_chars": "letter"
                }
            }
        }
    }
}