# django-bulbs Change Log

## Version 0.7.8

- Remove redundant ES_URLS settings, just use ES_CONNECTIONS

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
