# Live Blog

## API (v1) Documentation

 - [Entry](#entry)

### Entry

#### Create a new entry (POST)

```
/api/v1/liveblog/entry/
```

##### Body

```json
{
  "liveblog": 123,
  "headline": "Something Really Funny",
  "authors": ["TODO"],
  "body": "Why are you reading this? Stop it.",
  "recirc_content": [501, 1801, 17203],
  "published": "2015-01-01T01:01:00.000Z",
  "responses": [
    {
      "author": "TODO",
      "body": "Some more really interesting stuff you should read."
    }
  ]
}
```

##### Status Codes

- `201` if successful

#### Get All Entries

**GET:**

```
/api/v1/liveblog/entries/<liveblog_id>/
```

##### Body

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "liveblog": 123,
      "headline": "Something Really Funny",
      "authors": ["TODO"],
      "body": "Why are you reading this? Stop it.",
      "recirc_content": [501, 1801, 17203],
      "published": "2015-01-01T01:01:00.000Z",
      "responses": [
        {
          "author": "TODO",
          "body": "Some more really interesting stuff you should read."
        }
      ]
    },
    {
      "liveblog": 123,
      "headline": "Something Really Funny",
      "authors": ["TODO"],
      "body": "Why are you reading this? Stop it.",
      "recirc_content": [501, 1801, 17203],
      "published": "2015-01-01T01:01:00.000Z",
      "responses": [
        {
          "author": "TODO",
          "body": "Some more really interesting stuff you should read."
        }
      ]
    }
  ]
 }
```

##### Filters

`if_modified_since=2015-01-01T01:01:00.000Z` conditional filtering for new entries

##### Status Codes

* `200` if successful
* `304` no modified entries

#### Get an entry

##### GET

```
/api/v1/liveblog/entry/<:entry_id>/
```

##### Response

```json
  {
    "liveblog": 123,
    "headline": "Something Really Funny",
    "authors": ["TODO"],
    "body": "Why are you reading this? Stop it.",
    "recirc_content": [501, 1801, 17203],
    "published": "2015-01-01T01:01:00.000Z",
    "responses": [
      {
        "author": "TODO",
        "body": "Some more really interesting stuff you should read."
      }
    ]
  }
```

##### Status Codes

* `200` if successful
* `404` if entry doesn't exist


#### Update an entry

##### PUT

* `200` if successful
* `404` if entry doesn't exist

```
/api/v1/liveblog/entry/<:entry_id>/
```

##### Body
```
  {
    "liveblog": 123,
    "headline": "Something Really Funny",
    "authors": ["TODO"],
    "body": "Why are you reading this? Stop it.",
    "recirc_content": [501, 1801, 17203],
    "published": "2015-01-01T01:01:00.000Z",
    "responses": [
      {
        "author": "TODO",
        "body": "Some more really interesting stuff you should read."
      }
    ]
  }
```

##### Response

```json
  {
    "liveblog": 123,
    "headline": "Something Really Funny",
    "authors": ["TODO"],
    "body": "Why are you reading this? Stop it.",
    "recirc_content": [501, 1801, 17203],
    "published": "2015-01-01T01:01:00.000Z",
    "responses": [
      {
        "author": "TODO",
        "body": "Some more really interesting stuff you should read."
      }
    ]
  }
```
