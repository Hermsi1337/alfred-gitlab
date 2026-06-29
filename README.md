# Alfred Gitlab

Quickly navigate to GitLab projects in [Alfred 5][alfred].

![][sample]

## Setup and Usage
* Generate a GitLab personal access token (on GitLab.com: <https://gitlab.com/-/user_settings/personal_access_tokens>, on a self-hosted instance: `https://<host>/-/user_settings/personal_access_tokens`) with the `read_api` scope, then run `glsetkey <yourkey>`
* (Optionally) Tell it where the GitLab API you want to connect to is by running `glseturl https://<host>/api/v4/projects`
  * Defaults to GitLab.com's public API
* Search for projects with `gl <search>`
* Force a refresh of the cached project list with `glrefresh` (the list also refreshes automatically in the background — see below)

## Refreshing the project list
The project list is cached and refreshed in the background. By default the cache is considered stale
after one hour; the next time you run `gl` after that, a background refresh is kicked off and the
results update in place.

If you need fresh data immediately (e.g. you just created a project), run `glrefresh`. It clears the
cache and triggers an update right away.

If a background refresh fails (expired token, network/VPN issue, API error), `gl` now shows the error
at the top of the results instead of silently serving stale data.

## Configuration
Configure the workflow via [Workflow variables][wf-vars] (Alfred → Workflow → Configure Workflow / `[x]` button):

| Variable | Default | Effect |
| --- | --- | --- |
| `membership` | `true` | When `true`, only projects you are a *member* of are listed. Set it to `false` to list every project your token can see — useful on instances where you can access projects without being an explicit member. Expect a larger, slower fetch. |
| `refresh_interval` | `3600` | How long (in seconds) the cached project list is considered fresh before a background refresh is triggered. |
| `quick_open` | `true` | When `true`, selecting a project opens it directly. Set it to `false` to enable sub-page navigation (see below). |

### Sub-Page Navigation
![][sub-page]
After selecting a repository, you are prompted with a page to navigate to (Overview, Issues, Merge
Requests, Pipelines). This is controlled by the `quick_open` variable above.

## Notes
By default, only projects you are a member of are shown. See the `membership` variable above to change this.

# Thanks, License, Copyright

- This workflow is a fork of [lukewaite/alfred-gitlab][upstream].
- The [Alfred-Workflow][alfred-workflow] library is used heavily, and its wonderful documentation was key in building the plugin.
- The GitLab icon is used, care of GitLab.

All other code/media are released under the [MIT Licence][license].

[alfred]: https://www.alfredapp.com/
[alfred-workflow]: http://www.deanishe.net/alfred-workflow/
[wf-vars]: https://www.alfredapp.com/help/workflows/advanced/variables/
[license]: src/LICENSE.txt
[upstream]: https://github.com/lukewaite/alfred-gitlab
[sample]: https://raw.githubusercontent.com/hermsi1337/alfred-gitlab/master/docs/sample.png
[sub-page]: https://raw.githubusercontent.com/hermsi1337/alfred-gitlab/master/docs/sub-page.png
