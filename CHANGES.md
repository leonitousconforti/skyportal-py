# Changes

<!-- towncrier release notes start -->

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
