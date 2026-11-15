# AGENTS.md

Guidance for any AI agent (Claude, Codex, …) working in this repository.
`CLAUDE.md` is a symlink to this file.

## What this is

An Alfred 5 workflow to search and open your GitLab projects. Written in Python 3 and
distributed as a `.alfredworkflow` bundle.

## Layout

- `src/`: the workflow root; everything here ends up in the distributed bundle.
  - `src/gitlab.py`: Script Filter entry point (keyword `gl`); also handles `--setkey`, `--seturl`, `--refresh`.
  - `src/update.py`: background job that fetches the project list from the GitLab API and caches it.
  - `src/config.py`: reads the workflow variables from the environment, shared by both scripts.
  - `src/info.plist`: the Alfred workflow definition (keywords, variables, connections, version).
  - `src/workflow/` and `src/mureq.py`: **vendored third-party libraries. Do not edit them.**
- `tests/`: stdlib `unittest` tests; not part of the bundle.
- `.github/workflows/check.yml`: compile, plist lint and tests on every push and PR.
- `.github/workflows/release.yml`: the release pipeline (see Releases).
- `docs/`: screenshots referenced by the README.

## Hard rules

- **Never change `bundleid`** in `info.plist` (`com.lukewaite.alfred-gitlab`). It keys the macOS
  Keychain entry (API token) and the cache directory; changing it strands every existing install.
- **Never edit vendored code** (`src/workflow/**`, `src/mureq.py`). Treat it as read-only.
- **Keep documentation current.** Any change that affects behaviour, configuration, the API, or the
  release process MUST update this `AGENTS.md` and `README.md` in the same change. Out-of-date docs
  are treated as a bug, not a follow-up.

## Conventions

- Python 3, standard library plus the two vendored libs only — no new dependencies.
- Self-explanatory code; no inline comments that merely restate the code.
- f-strings; a blank line before `return` (unless it is the only statement in the block);
  descriptive error variable names (e.g. `fetch_err`, never a bare `err`).

## Configuration (Alfred workflow variables, read from the environment)

Boolean variables accept `true`/`false`, `1`/`0`, `yes`/`no`, `on`/`off`; anything else falls back to the default.

- `membership` (default `true`): when true, only projects the user is a member of are fetched.
- `hide_archived` (default `false`): when true, archived projects are filtered out at display time in
  `gitlab.py`, so toggling it needs no refresh. The cache always holds archived projects too.
- `refresh_interval` (default `3600`): seconds before the cached project list is refreshed.
- `quick_open` (default `true`): open projects directly vs. show the sub-page menu.

New variables get a default in the `variables` dict of `info.plist`, a reader in `config.py`, and an
entry in the README table and the `readme` string of `info.plist`.

## GitLab API

- REST API v4. Authenticate with the `PRIVATE-TOKEN` header — never the deprecated
  `private_token` query parameter.
- The project list is paginated via the `X-Next-Page` response header.
- `update.py` caches only the fields in `CACHED_PROJECT_FIELDS`. A new field read in `gitlab.py` must be
  added there, and must be read with `.get()` since existing caches lack it until the next refresh.

## Verify before pushing

- `python3 -m py_compile src/config.py src/gitlab.py src/update.py`
- `plutil -lint src/info.plist`
- `python3 -m unittest discover -s tests`

## Local testing

Editing files under `src/` does **not** change the workflow Alfred is running — that is a separate
installed copy under `~/Library/Application Support/Alfred/.../workflows/`. To try changes live,
copy the edited files into that folder and reload Alfred, or import a freshly built bundle.

## Releases

- Cut a release from the **Release** GitHub Actions workflow (Actions → Release → Run workflow →
  enter a semver version).
- It writes the version into `src/info.plist`, builds `GitLab.alfredworkflow`, and publishes a
  GitHub Release with that bundle attached.
- Git tags and GitHub-generated release notes are the source of truth — there is **no** CHANGELOG file.
- The in-app updater offers an update only when the released tag version is greater than the
  installed `info.plist` version.
