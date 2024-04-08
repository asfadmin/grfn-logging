# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [PEP 440](https://www.python.org/dev/peps/pep-0440/)
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0]

### Changed
- For products with version >= `v3`:
  - Browse image downloads are reported under the `ARIA_S1_GUNW_BROWSE` collection.
  - All other product downloads are reported under the `ARIA_S1_GUNW` collection.
- For older products:
  - Browse image downloads are reported under the `SENTINEL-1_INTERFEROGRAMS_BROWSE` collection.
  - All other product downloads are reported under the `SENTINEL-1_INTERFEROGRAMS` collection.
- Upgraded lambda functions to Python 3.12 from Python 3.8.
- Upgraded Elasticsearch to 7.10 from 7.4.
- Upgraded instance type for Elasticsearch domain to `t3.small.search` from `t2.small.elasticsearch`.

### Removed
- Downloads of `.unw_geo.zip` products are no longer reported under the `SENTINEL-1_INSAR_UNWRAPPED_INTERFEROGRAM_AND_COHERENCE_MAP` collection. This collection was removed within the last year.

## [0.1.0]

This is the initial release after replacing the AWS CodePipeline workflow with a GitHub Actions deployment workflow.
