import os
import sys
import argparse

from workflow import Workflow3, ICON_WARNING, ICON_INFO, ICON_ERROR, PasswordNotFound
from workflow.background import run_in_background, is_running

log = None

DEFAULT_REFRESH_INTERVAL = 3600


def refresh_interval():
    try:
        return int(os.environ.get('refresh_interval', DEFAULT_REFRESH_INTERVAL))
    except ValueError:
        return DEFAULT_REFRESH_INTERVAL


def search_for_project(project):
    elements = [project['name_with_namespace'], project['path_with_namespace']]

    return ' '.join(elements)


def trigger_update(wf):
    if not is_running('update'):
        run_in_background('update', [sys.executable, wf.workflowfile('update.py')])


def main(wf):
    parser = argparse.ArgumentParser()
    parser.add_argument('--setkey', dest='apikey', nargs='?', default=None)
    parser.add_argument('--seturl', dest='apiurl', nargs='?', default=None)
    parser.add_argument('--refresh', dest='refresh', action='store_true')
    parser.add_argument('query', nargs='?', default=None)
    args = parser.parse_args(wf.args)

    if args.apikey:
        log.info('Setting API Key')
        wf.save_password('gitlab_api_key', args.apikey)

        return 0

    if args.apiurl:
        log.info(f'Setting API URL to {args.apiurl}')
        wf.settings['api_url'] = args.apiurl

        return 0

    if args.refresh:
        log.info('Manual refresh requested')
        wf.clear_cache(lambda f: f.startswith('projects'))
        wf.cache_data('update_error', None)
        trigger_update(wf)

        return 0

    try:
        wf.get_password('gitlab_api_key')
    except PasswordNotFound:
        wf.add_item('No API key set.',
                    'Please use glsetkey to set your GitLab API key.',
                    valid=False,
                    icon=ICON_WARNING)
        wf.send_feedback()

        return 0

    query = args.query

    projects = wf.cached_data('projects', None, max_age=0)

    if wf.update_available:
        wf.add_item('New version available',
                    'Action this item to install the update',
                    autocomplete='workflow:update',
                    icon=ICON_INFO)

    update_error = wf.cached_data('update_error', None, max_age=0)
    if update_error:
        wf.add_item('Could not update project list',
                    str(update_error),
                    valid=False,
                    icon=ICON_ERROR)

    if is_running('update') and not projects:
        wf.rerun = 0.5
        wf.add_item('Updating project list via GitLab...',
                    subtitle='This can take some time if you have a large number of projects.',
                    valid=False,
                    icon=ICON_INFO)

    if not wf.cached_data_fresh('projects', max_age=refresh_interval()) and not is_running('update'):
        trigger_update(wf)
        wf.rerun = 0.5

    if query and projects:
        projects = wf.filter(query, projects, key=search_for_project, min_score=20)

    if not projects:
        wf.add_item('No projects found', icon=ICON_WARNING)
        wf.send_feedback()

        return 0

    for project in projects:
        wf.add_item(title=project['name_with_namespace'],
                    subtitle=project['path_with_namespace'],
                    arg=project['web_url'],
                    valid=True,
                    icon=None,
                    uid=str(project['id']))

    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow3(update_settings={
        'github_slug': 'hermsi1337/alfred-gitlab',
    })
    log = wf.logger
    sys.exit(wf.run(main))
