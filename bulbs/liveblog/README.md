# Live Blog Entry API

## Create new entry (POST)

```
/api/v1/liveblog/entry/
```

### Body

```json
{
  "liveblog": 123,
  "headline": "Something Really Funny",
  "authors": [50, 57],
  "body": "Why are you reading this? Stop it.",
  "recirc_content": [501, 1801, 17203],
  "published": "2015-01-01T01:01:00.000Z",
  "responses": [
    {
      "author": 85,
      "body": "Some more really interesting stuff you should read."
    }
  ]
}
```

### Status Codes

- `201` if successful

## Get All Entries

**GET:**

```
/api/v1/liveblog/entry/
```

### Body

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "liveblog": 123,
      "headline": "Something Really Funny",
      "authors": [50, 57],
      "body": "Why are you reading this? Stop it.",
      "recirc_content": [501, 1801, 17203],
      "published": "2015-01-01T01:01:00.000Z",
      "responses": [
        {
          "author": 85,
          "body": "Some more really interesting stuff you should read."
        }
      ]
    },
    {
      "liveblog": 123,
      "headline": "Something Really Funny",
      "authors": [50, 57],
      "body": "Why are you reading this? Stop it.",
      "recirc_content": [501, 1801, 17203],
      "published": "2015-01-01T01:01:00.000Z",
      "responses": [
        {
          "author": 85,
          "body": "Some more really interesting stuff you should read."
        }
      ]
    }
  ]
 }
```

### Filters

`liveblog=123` Conditional filtering to match entries for specific `LiveBlog`

## Get All Entries (PUBLIC)

**GET:**

```
/api/v1/liveblog/public/entry/
```

### Body

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "liveblog": 123,
      "headline": "Something Really Funny",
      "authors": [50, 57],
      "body": "Why are you reading this? Stop it.",
      "recirc_content": [501, 1801, 17203],
      "published": "2015-01-01T01:01:00.000Z",
      "responses": [
        {
          "author": 85,
          "body": "Some more really interesting stuff you should read."
        }
      ]
    },
    {
      "liveblog": 123,
      "headline": "Something Really Funny",
      "authors": [50, 57],
      "body": "Why are you reading this? Stop it.",
      "recirc_content": [501, 1801, 17203],
      "published": "2015-01-01T01:01:00.000Z",
      "responses": [
        {
          "author": 85,
          "body": "Some more really interesting stuff you should read."
        }
      ]
    }
  ]
 }
```

### Filters

`liveblog=123` Conditional filtering to match entries for specific `LiveBlog`
`if_modified_since=2015-01-01T01:01:00.000Z` Conditional filtering to return all entries published after specified ISO 8601 date/time.

### Status Codes

* `200` if successful (modified entries found)
* `304` no modified entries

## Get single entry

### GET

```
/api/v1/liveblog/entry/<:entry_id>/
```

### Response

```json
  {
    "liveblog": 123,
    "headline": "Something Really Funny",
    "authors": [50, 57],
    "body": "Why are you reading this? Stop it.",
    "recirc_content": [501, 1801, 17203],
    "published": "2015-01-01T01:01:00.000Z",
    "responses": [
      {
        "author": 60,
        "body": "Some more really interesting stuff you should read."
      }
    ]
  }
```

### Status Codes

* `200` if successful
* `404` if entry doesn't exist


## Update entry

### PUT

* `200` if successful
* `404` if entry doesn't exist

```
/api/v1/liveblog/entry/<:entry_id>/
```

### Body
```
  {
    "liveblog": 123,
    "headline": "Something Really Funny",
    "authors": [50, 57],
    "body": "Why are you reading this? Stop it.",
    "recirc_content": [501, 1801, 17203],
    "published": "2015-01-01T01:01:00.000Z",
    "responses": [
      {
        "author": 85,
        "body": "Some more really interesting stuff you should read."
      }
    ]
  }
```

### Response

```json
  {
    "liveblog": 123,
    "headline": "Something Really Funny",
    "authors": [50, 57],
    "body": "Why are you reading this? Stop it.",
    "recirc_content": [501, 1801, 17203],
    "published": "2015-01-01T01:01:00.000Z",
    "responses": [
      {
        "author": 85,
        "body": "Some more really interesting stuff you should read."
      }
    ]
  }
```
