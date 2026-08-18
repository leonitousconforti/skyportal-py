Add `upsert_photometry` for `PUT /api/photometry`, which uploads photometry
while resolving points that already exist, where `post_photometry` fails on
them.
