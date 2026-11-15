from workflow import Workflow, PasswordNotFound
import mureq

from config import membership_only, refresh_interval

DEFAULT_API_URL = 'https://gitlab.com/api/v4/projects'
CACHED_PROJECT_FIELDS = ('id', 'name_with_namespace', 'path_with_namespace', 'web_url', 'archived')


def slim_project(project):
    return {field: project.get(field) for field in CACHED_PROJECT_FIELDS}


def get_projects(wf, api_key, url):
    projects = []
    page = 1
    while page:
        wf.logger.info(f'Calling API page {page}')
        params = {'per_page': 100, 'page': page}
        if membership_only():
            params['membership'] = 'true'

        response = mureq.get(url, headers={'PRIVATE-TOKEN': api_key}, params=params)
        response.raise_for_status()

        projects.extend(slim_project(project) for project in response.json())

        next_page = response.headers.get('X-Next-Page')
        page = int(next_page) if next_page else None

    return projects


def main(wf):
    try:
        api_key = wf.get_password('gitlab_api_key')
    except PasswordNotFound:
        wf.logger.error('No API key saved')

        return

    if wf.cached_data_fresh('projects', max_age=refresh_interval()):
        return

    api_url = wf.settings.get('api_url', DEFAULT_API_URL)
    try:
        projects = get_projects(wf, api_key, api_url)
    except Exception as fetch_err:
        wf.cache_data('update_error', str(fetch_err))
        wf.logger.error(f'Failed to fetch GitLab projects: {fetch_err}')

        return

    wf.cache_data('projects', projects)
    wf.cache_data('update_error', None)
    wf.logger.debug(f'{len(projects)} gitlab projects cached')


if __name__ == '__main__':
    Workflow().run(main)
