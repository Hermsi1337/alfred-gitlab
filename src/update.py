import os

from workflow import Workflow, PasswordNotFound
import mureq

log = None

DEFAULT_API_URL = 'https://gitlab.com/api/v4/projects'
DEFAULT_REFRESH_INTERVAL = 3600


def refresh_interval():
    try:
        return int(os.environ.get('refresh_interval', DEFAULT_REFRESH_INTERVAL))
    except ValueError:
        return DEFAULT_REFRESH_INTERVAL


def membership_only():
    return os.environ.get('membership', 'true').strip().lower() != 'false'


def get_projects(api_key, url):
    projects = []
    page = 1
    while page:
        log.info(f'Calling API page {page}')
        params = {'per_page': 100, 'page': page}
        if membership_only():
            params['membership'] = 'true'

        response = mureq.get(url, headers={'PRIVATE-TOKEN': api_key}, params=params)
        response.raise_for_status()

        projects.extend(response.json())

        next_page = response.headers.get('X-Next-Page')
        page = int(next_page) if next_page else None

    return projects


def main(wf):
    try:
        api_key = wf.get_password('gitlab_api_key')
    except PasswordNotFound:
        wf.logger.error('No API key saved')
        return

    api_url = wf.settings.get('api_url', DEFAULT_API_URL)

    if wf.cached_data_fresh('projects', max_age=refresh_interval()):
        return

    try:
        projects = get_projects(api_key, api_url)
        wf.cache_data('projects', projects)
        wf.cache_data('update_error', None)
        wf.logger.debug(f'{len(projects)} gitlab projects cached')
    except Exception as fetch_err:
        wf.cache_data('update_error', str(fetch_err))
        wf.logger.error(f'Failed to fetch GitLab projects: {fetch_err}')


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    wf.run(main)
