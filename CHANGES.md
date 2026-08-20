# Changes

<!-- towncrier release notes start -->

## 0.3.3 (2026-08-20)

### Bug fixes

- `Comment` gains `system`, the flag SkyPortal sets on comments the app posts
  itself rather than ones typed by their author. ([#13](https://github.com/leonitousconforti/skyportal-py/pull/13))


## 0.3.2 (2026-08-20)

No significant changes.


## 0.3.1 (2026-08-20)

### Bug fixes

- Fix response models against what the server actually sends, caught by the
  first full CI run of SkyPortal's dogfooded API test suite:
  `FollowupRequestPostResponse` gains `request_status`, `Comment` gains
  `channel`, `ObjTagPostResponse` gains `groups`, `ApiToken` gains the
  eager-loaded `acls` and `created_by`, and a photometry point's `altdata`
  may be the literal string `"NaN"` after a duplicate-resolving upload.
  `GalaxyCatalogPost` now decodes bytes entries in `catalog_data` (as
  HDF5-read astropy tables produce), which the JSON encoder used to reject. ([#12](https://github.com/leonitousconforti/skyportal-py/pull/12))


## 0.3.0 (2026-08-19)

### New features

- Fill in gaps found while dogfooding the client in SkyPortal's API test
  suite: `fetch_group` gained `include_group_users=`, and the new
  `fetch_groups_by_name` covers the `name=` form of `GET /api/groups` (which
  returns a plain list); `fetch_telescopes` gained the `name=` and
  latitude/longitude box filters; `fetch_users` gained the remaining query
  filters (name/email/role/ACL/group/stream, expired accounts, sorting) and
  stopped forcing a page size; `update_user` now distinguishes an omitted
  `expiration_date` from an explicit `None`, so an expiration can be cleared;
  and the new `update_profile` covers `PATCH /api/internal/profile`.

  `create_client` now forwards extra keyword arguments to `httpx.Client`
  (e.g. `trust_env=False` to keep a netrc entry from overriding the token
  header) and accepts `timeout=None` to disable the request timeout.

  `fetch_sources` gained the `source_id=` partial-match filter, the new
  `fetch_dbinfo` covers `GET /api/internal/dbinfo`, and the new `tokens`
  module covers API token management (`fetch_tokens`, `fetch_token`,
  `post_token`, `update_token`, `delete_token`).

  `update_comment` can now replace a comment's attachment and no longer
  requires `text`: all fields are optional and omitted ones are left
  unchanged.

  The plain comment and annotation functions (`post_comment`,
  `update_comment`, `delete_comment`, `fetch_comments`, `post_annotation`,
  `update_annotation`, `delete_annotation`, `fetch_annotations`) now take a
  `resource_type=` keyword like their siblings, so comments on spectra,
  shifts, GCN events and earthquakes, and annotations on spectra and
  photometry, are no longer sources-only; their first parameter is renamed
  `obj_id` -> `resource_id` to match.

  Candidates and sources: `fetch_candidates` gained the scanner's full
  query surface (autocomplete, annotation sorting and filters,
  classification/redshift filters, cached-query replay, photometry
  annotation filters, `include_photometry=`), `fetch_candidate` gained
  `include_photometry=`/`include_spectra=`, and the new `candidate_exists`
  covers the endpoint's HEAD form; `fetch_sources` gained the spatial
  catalog filters and `fetch_source` gained `include_color_magnitude=`;
  `update_annotation` can rename an annotation's `origin`; and the new
  `post_classifications` covers the batch classification POST.

  `fetch_sources` gained the sources page's full filter surface (save
  times, spectra/TNS/follow-up existence, classifications, redshift and
  magnitude ranges, annotation/comment filters, exclusion lists, sorting),
  with the new `fetch_sources_save_summary` covering the `saveSummary`
  form's distinct row shape; `fetch_source` gained the remaining include
  flags (photometry-exists, detection stats, period-exists, labellers,
  GCN crossmatches, deduplicated photometry); `update_source` gained
  `transient`/`ra_dis`/`altdata`/`summary`; and the new `source_exists`
  covers the endpoint's HEAD form.

  `fetch_sources` also gained the GCN localization filters
  (`localization_dateobs`/`localization_name`/`localization_cumprob`);
  `fetch_source` gained `include_analyses=`; `fetch_instrument` gained
  `include_geojson=`/`include_geojson_summary=`/`include_region=` and
  `fetch_instruments` a `name=` filter; and `update_profile` can target
  another user's profile via `user_id=` (requires the "Manage users" ACL).

  A systematic audit of the server's `get_query_argument` reads against the
  client then filled every remaining GET query-param hole: the sources page
  and single-source GET (TNS/alias/origin filters, labelling filters,
  comment/annotation time and author filters, the remaining include flags),
  the candidate scanner (filter IDs, listing filters, detection-count and
  localization filters, autosave), source photometry (annotation/owner/
  stream info, phase folding, individual-vs-series, deduplication), source
  spectra (normalization, sorting), followup requests (observation windows,
  priority threshold, requesters, sorting, thumbnails), allocations
  (API-type filters and embedded-request pagination/sorting), comments
  (text/channel filters and pagination), instruments (localization overlap
  and airmass), and analysis results (`download=`).

  SuperObj aggregation: `fetch_source` gained
  `include_super_objs=`/`include_comments=`, `fetch_classifications`
  `include_super_objs=`, and `fetch_photometry`
  `include_super_objs_photometry=`; the new
  `fetch_altdata_info`/`fetch_annotations_info` cover the altdata and
  annotation key catalogs.

  Photometry: `PhotometryPost` now expresses the endpoint's bulk form
  (every measurement field accepts a 1D list, with scalars broadcast) and
  the `group_ids="all"` sentinel; `fetch_photometry` gained
  `include_extinction=` and `include_validation_info=`; `PhotometryUpdate`
  sends only explicitly-set fields, so an explicit `None` (e.g. turning a
  detection into a non-detection) reaches the server as null; `fetch_source`
  gained `include_photometry=`; `fetch_spectrum`/`fetch_spectra` gained
  `include_original_file=`; and the new `delete_source_photometry` covers
  `DELETE /api/sources/{obj_id}/photometry`. ([#10](https://github.com/leonitousconforti/skyportal-py/pull/10))


## 0.2.0 (2026-08-18)

### Breaking changes

- All models now use `extra="forbid"`: unknown fields in request payloads and
  server responses raise a validation error instead of being silently ignored
  or kept as extra attributes. ([#7](https://github.com/leonitousconforti/skyportal-py/pull/7))
- Response models now type timestamp fields as `datetime.datetime` (or
  `datetime.date`) rather than `str`, so attributes like `created_at` and
  `modified` come back as datetime objects. Request payload models keep string
  timestamps so they stay JSON-serializable. ([#8](https://github.com/leonitousconforti/skyportal-py/pull/8))

### New features

- Add typed endpoint functions for spectra, instruments, telescopes,
  taxonomies, filters, annotations, and users, all bound as methods on the
  `SkyPortal` client. ([#5](https://github.com/leonitousconforti/skyportal-py/pull/5))
- Add typed endpoint functions covering the rest of the SkyPortal API, in new
  modules for GCN events, localizations, observation plans, observations,
  survey efficiency, galaxies, spatial catalogs, catalog queries, analysis
  services, assignments, brokers, sharing services, MMA detectors,
  earthquakes, skymap triggers, healpix, objs, tags, source groups, shifts,
  reminders, invitations, group admission requests, teams, listings, ACLs,
  roles, thumbnails, sharing, public pages, moving objects, photometric
  series, recurring APIs, news feed, weather, and system info; plus the
  missing create, update, and delete verbs on the resources that were already
  covered. Every endpoint function is bound as a method on the `SkyPortal`
  client.

  Response models now declare the full payload the server sends: every column of
  the underlying record, the related objects the endpoint includes, and the
  fields the server computes per request. This fixes several models that could
  not validate a real response at all, including the source spectra, sources,
  candidates, photometry upload, and comment endpoints. ([#8](https://github.com/leonitousconforti/skyportal-py/pull/8))
- Add `upsert_photometry` for `PUT /api/photometry`, which uploads photometry
  while resolving points that already exist, where `post_photometry` fails on
  them. ([#9](https://github.com/leonitousconforti/skyportal-py/pull/9))


## 0.1.0 (2026-08-18)

### New features

- Add typed endpoint functions for groups, candidates, photometry, comments,
  and classifications, all bound as methods on the `SkyPortal` client. ([#2](https://github.com/leonitousconforti/skyportal-py/pull/2))


## 0.1.dev6+g983a29b40 (2026-08-18)

### Other changes

- Set up the release pipeline: publish to PyPI via trusted publishing on GitHub
  release, and track changelog entries with towncrier fragments.
