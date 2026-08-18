# Releasing

## Cutting a release

All commands run inside the nix dev shell (`nix develop`), which provides uv.

1. Preview the changelog for the version you are about to release:

       uv run towncrier build --draft --version X.Y.Z

2. Compile the changelog. This inserts a new section into `CHANGES.md` and
   deletes the consumed fragments from `changes.d/`:

       uv run towncrier build --version X.Y.Z

3. Commit and land the result on `main` (use the `skip-changelog` label if it
   goes through a pull request):

       git add -A && git commit -m "Release X.Y.Z"

4. Tag the release commit. setuptools_scm derives the package version from
   this tag, so the tag must be `v` + the exact version:

       git tag vX.Y.Z
       git push origin main --tags

5. Publish a GitHub release for the tag, pasting the new `CHANGES.md` section
   as the notes:

       gh release create vX.Y.Z --title "vX.Y.Z"

   Publishing the GitHub release is what triggers the upload; a tag alone
   does nothing. The `python-publish.yml` workflow builds the sdist and wheel
   with `uv build` and uploads them to PyPI via trusted publishing.

6. Verify the new version appears at <https://pypi.org/project/skyportal-py/>
   and that the "Upload Python Package" workflow run is green.
