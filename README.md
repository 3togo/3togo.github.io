# 3togo.github.io

A personal homepage and searchable directory of **all public, non-fork repositories** owned by [3togo](https://github.com/3togo).

**Website:** https://3togo.github.io/

The directory includes archived source repositories, labels them, and offers an “Active only” filter. Forks and private repositories are excluded. Repository descriptions come from GitHub; a non-fork status is not a claim of original authorship.

## Build locally

Requires Python 3.10+ and the GitHub CLI (`gh`). Authenticate the CLI, then:

```sh
python3 scripts/build.py
python3 -m http.server 8765 --directory _site
```

Open http://localhost:8765. The generated HTML contains every repository link without requiring JavaScript. JavaScript progressively adds search, language filtering, active-only filtering, sorting, and a resettable empty state. The page follows the system light/dark preference and respects reduced motion.

## Update content

- Edit repository descriptions and topics on GitHub; the next build picks them up.
- Edit `featured_names` in `scripts/build.py` to change selected work. Removed, private, and forked repositories are automatically excluded, including from selected work.
- Edit `static/style.css` for appearance and `static/app.js` for directory interactions.
- The generator requests the public `/users/3togo/repos` API endpoint with full pagination. It fails the build if GitHub cannot supply data, retaining the last successful deployment.

## Publication

GitHub Pages uses the workflow in `.github/workflows/pages.yml`. It rebuilds on pushes to `main`, manual runs, and a daily schedule at **04:23 UTC**. New public source repositories appear on the next successful refresh, and repositories made private, deleted, or converted to forks disappear. GitHub schedules can be delayed and may be disabled after extended repository inactivity; check Actions and re-enable the workflow when necessary. No custom token or visitor-side API calls are required.

The Actions workflow has read-only repository access during the build; only deployment receives Pages and identity-token write permissions. Generated files are deployed as an artifact, not committed back to the repository.
