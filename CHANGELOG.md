# django-bulbs Change Log

## Development

## Version 2.7.6

- `migrate_to_ia` command now only migrates previously un-migrated content

## Version 2.7.5

- Fixed import issue in `migrate_to_ia` command

## Version 2.7.4

- Fixed `migrate_to_ia` command to migrate Feature Types passed in on command line

## Version 2.7.3

- Added `migrate_to_ia` command to migrate entire Feature Types over to Instant Articles

## Version 2.7.2

- Changed `instant_article_id` on Content model from `IntegerField` to `BigIntegerField`

## Version 2.7.1

- Added analytics to video series js and updated tests for latest episode js

## Version 2.7.0

- Added `videos.VideoMixin` and merged `videohub-client` repository into `django-bulbs` (one less repository!)

## Version 2.6.0

- Added Series Detail View to Videos App.

## Version 2.5.4
> *__This version safe to roll-out without changes to site.__*

- Added `target-host-channel` attribute to the `bulbs-video` element on the base special coverage landing page.

## Version 2.5.3
> *__This version safe to roll-out without changes to site.__*

- Changed css and html for special_coverage_landing

## Version 2.5.2

- Changed Instant Article `vault.read()`s to check for key of `authtoken` & throw an error if it's not present

## Version 2.5.1

- Removed 'FACEBOOK_API_ENV' in favor of boolean 'FACEBOOK_POST_TO_IA' for determining if article should be posted to IA or not
- Added `FACEBOOK_API_DEVELOPMENT_MODE` and `FACEBOOK_API_PUBLISH_ARTICLE` settings flags for instant article testing

## Version 2.5.0

- Added publishing to Facebook's Instant Article API on Content.save(), if the content feature type supports Instant Artices & the content is published.
- Added deletion from Facebook's Instant Article API on Content.save(), if the content has already been pushed to the Instant Article platform & is being unpublished
- Added deletion from Facebook's Instant Article API on Contnet.delete(), if the content had been pushed to the Instant Article platform

## Version 2.4.2

- Added animated gif support to the instant article renderer & parser

## Version 2.4.1

- Added twitter video parsing
- Parser checks `src` on youtube iframe embeds

## Version 2.4.0

- Added [`ReportBugEmail`](https://github.com/theonion/django-bulbs/blob/4034cb55ec4142d022bf8b48fa71cd935dc473db/bulbs/api/views.py#L608-L638) view for a common bug reporter endpoint

## Version 2.3.2

- Added `<blockquote>`, `<ol>`, `<ul>`, `<h3>`, and `<h4>` support to instant article parser
- Added in `content.subhead` to `base_instant_article.html`

## Version 2.3.0

- Added `parser.py`, which parses article bodies, and sends them to `renderer.py`, which can render article bodies in a particular format
- Update `base_instant_article.html` and `base_instant_article_rss.xml` to use generated body, based on `parser.py` & `renderer.py`

## Version 2.2.1

- Move special coverage styles into bulbs styles

## Version 2.2.0

- A little directory restructuring in bulbs-styles

## Version 2.1.0

- change `special_coverage_landing_partial` template tag
  It now expects a `twitter_handle` and `share_message` argument:

  `{% special_coverage_landing_partial twitter_handle='theonion' share_message='via theonion.com' %}`

## Version 2.0.2

- Move instant article ads to header in base_instant_article.html

## Version 2.0.0

- Merged in all 0.8.x changes.

## Version 1.1.1

- Update video grid styles and add bulbs-video-play-button

## Version 0.11.6

- Add video recirc widget and global SASS styles

## Version 0.11.5

- Minor tweaks to Glance feed:
  - Glance feed 5min cache time
  - Switch thumbnails to "image" key

## Version 0.11.4

- Add Glance JSON feed for content ingestion: `/feeds/glance.json`

## Version 0.11.1

- Fix content API "Trash" to ignore ES 404 error by using new DJES "delete from index on save" functionality

## Version 0.10.2

- Added `TunicClient` with initial support for a single method `get_active_campaigns`. Requires these settings:
    - TUNIC_STAFF_BACKEND_ROOT (ex: "http://onion.local/api/v1/")
    - TUNIC_REQUEST_TOKEN (ex: "12345")
    - TUNIC_API_PATH (ex: "/api/v1/")

## Version 0.8.18

- Change default sort order of Instant Article feed to last modified time, than published date

## Version 0.8.17

- Add Glance JSON feed for content ingestion: `/feeds/glance.json`
- Instant article improvements
- Targeting + footer improvements

## Version 0.8.10

- Adds tag-based recirc fallback to `RecircViewSet` `GET` request

## Version 0.8.9

- Adds `get_inline_recirc_content()` to `BaseQueryMixin`
- Added `InlineRecircViewSet` to `recirc/views` which provides a `GET` request to get an objects inline recirc content

## Version 0.8.8
- `bulbs.special_coverage.views.SpecialCoverageView` sets dfp tracking values in context

## Version 0.8.7

- `utils.test.BaseIndexableTestCase` now waits for ES shard startup, to reduce flaky tests querying ES before it's ready.

## Version 0.8.6

- Added `recirc` app
- Added `BaseQueryMixin` to `recirc/mixins`, which provides a `query` json field and some utility functions
- Added `RecircViewSet` to `recirc/views` which provides a `GET` request to get an objects recirc content

## Version 0.8.5

- Added poll image field to polls
- Added images and image url fields to poll answers

## Version 0.8.4

- Started `videos` app
- Added `SeriesDetailView` to `videos/views`

## Version 0.8.3

- Reduce RSS view caching from 10 to 5 min (per social squad)

## Version 0.8.2

- Fixed bugs with reading poll data for unpublished polls.
  We were returning an error when sodahead reads failed.
  We now return partial data.

## Version 0.8.1

- Add `bulbs/reading_list` application
  Adding `bulbs.reading_list.mixins.ReadingListMixin` adds the reading list methods and properties
    to a given object.

- Relocate `bulbs.content.models.ContentManager` to `bulbs.content.managers.ContentManager`

- Add common query methods to the `bulbs.content.models.ContentManager`
  - evergreen: returning all Content with evergreen=True.
  - evergreen_video: returning all Content with the configured VIDEO_DOC_TYPE document type.
  - sponsored: returning all Content associated with a campaign.

- Add `pageview_client.clients.TrendingClient` popular logic to retrieve popular Content ids from
    the service.

- Relocate `bulbs.special_coverage.search.SearchSlicer` to
    `bulbs.reading_list.slicers.SearchSlicer`

- Add `bulbs.sections.managers.SectionIndexableManager` to retrieve sections by their percolator
    identifier via elasticsearch

- Add `bulbs.sections.managers.SectionManager` to retrieve sections by their percolator
    identifier via django

- Add `bulbs.special_coverage.managers.SpecialCoverage` to retrieve sections by their percolator
    identifier via django


## Version 0.8.0

### Polls

- Adds `bulbs/poll` application
  Adding `"bulbs.poll"` to `INSTALLED_APPS` will
    automatically add poll api routes to the `bulbs.api` routes

- Added `bulbs.poll.urls`
  Adding `url(r'^', include('bulbs.poll.urls')),` creates a read-only
    endpoint that exposes merged data from sodahead and our database.

    It is accessible at `/poll/:poll_id/merged.json`

- Added `SODAHEAD_BASE_URL` to settings.
  Most likely value is: `'https://onion.sodahead.com'`

- Added `SODAHEAD_TOKEN_VAULT_PATH` to settings.
  In local/testing environments, this should be: `'sodahead/token'`
  In production environments, this should be: `:property/sodahead/token`
    ie: `starwipe/sodahead/token`.

  In production, each app has it's own sodahead token, and all test
    enviromnents share a sodahead token.

### Vault

Vault is a credentials storage server:
<a href="https://www.vaultproject.io/">https://www.vaultproject.io/</a>

- Adds a vault client at: `bulbs.utils.vault`
  `bulbs.utils.vault.read(path)` combines `VAULT_BASE_SECRET_PATH`
    as a prefix to the passed in path and reads it from Vault.

- Adds vault test mocking at: `bulbs.utils.test.mock_vault`
  See the implementation for documentation on mocking the vault in tests:
  <a href="https://github.com/theonion/django-bulbs/blob/master/bulbs/utils/test/__init__.py#L131-L144">
    https://github.com/theonion/django-bulbs/blob/master/bulbs/utils/test/__init__.py#L131-L144
  </a>

- Added `VAULT_BASE_URL` to settings.
  The base url of our Vault credentials store.
    ie: 'http://hostname:8200/v1/'

- Added `VAULT_BASE_SECRET_PATH` to settings.
    ie: `secrets/example`

- Added `VAULT_ACCESS_TOKEN` to settings.
    ie: `very-secret-token`

## Version 0.7.11

- Remove redundant ES_URLS setting, just use ES_CONNECTIONS. Eventually all client projects can stop using ES_URLS too.
- Example app checks ELASTICSEARCH_HOST env variable (useful for using docker-based ES served inside VM)

## Version 0.7.10

- Added `special_coverage` object to SpecialCoverageView context

## Version 0.7.9

- Added SpecialCoverageView to /bulbs/special_coverage/views for Special Coverage reuse

## Version 0.7.8

- Hotfix for contribution csv & api discrepencies with publish filters.

## Version 0.7.6

- Add `Content.evergreen` boolean column to indicate "always fresh" content

## Version 0.7.5

- Improved special coverage percolator retrieval logging

## Version 0.7.3

- Fix special coverage migration to grab model directly so that custom `SpecialCoverage.save()` method is called and triggers `_save_percolator`
- Campaign.save() triggers `SpecialCoverage._save_percolator()` via Celery task
- Install: Celery is now a regular (non-dev) requirement
- Bump min DJES dependency to reflect latest requirements

## Version 0.7.1

- Fix `Content.percoloate_special_coverage()` to ignore non-special-coverage results (ex: Sections)
- Fix `Content.percoloate_special_coverage()` to filter out entries without `start_date` fields (prevents search failure if one entry in shard was missing field)

## Version 0.7.0

- Added `Content.percolate_special_coverage()` containing new Special Coverage ordering rules to be shared by all client sites
- Fixed `SpecialCoverage._save_percolator()` to *always* save to percolator. This fixes regression in **0.6.49** with switch from `active` boolean flag to `is_active` property based on start/end dates, which would cause inclusion in percolator based on when SpecialCoverage was last saved. This fix requires percolator retrieval to filter active Special Coverage by start/end dates, and is the reason for the breaking minor version change. Easiest to just use the new `Content.percolate_special_coverage()` method instead of site-specific queries.

## Version 0.6.43

- Added `instant_article` flag to content model to set whether or not content eligible for Instant Articles RSS Feed
