import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import config
from gitlab import project_subtitle, toggle_hide_archived, visible_projects
from update import slim_project

ACTIVE = {'id': 1, 'name_with_namespace': 'Group / Active', 'path_with_namespace': 'group/active',
          'web_url': 'https://gitlab.example/group/active', 'archived': False}
ARCHIVED = {'id': 2, 'name_with_namespace': 'Group / Old', 'path_with_namespace': 'group/old',
            'web_url': 'https://gitlab.example/group/old', 'archived': True}


class EnvFlagTest(unittest.TestCase):
    def test_recognises_true_and_false_spellings(self):
        for value, expected in [('true', True), ('TRUE', True), ('1', True), (' yes ', True),
                                ('false', False), ('0', False), ('No', False)]:
            with self.subTest(value=value), mock.patch.dict(os.environ, {'flag': value}):
                self.assertIs(config.env_flag('flag', not expected), expected)

    def test_falls_back_to_default_when_unset_or_unrecognised(self):
        with mock.patch.dict(os.environ, {'flag': 'maybe'}):
            self.assertTrue(config.env_flag('flag', True))
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(config.env_flag('flag', False))

    def test_invalid_refresh_interval_uses_default(self):
        with mock.patch.dict(os.environ, {'refresh_interval': 'soon'}):
            self.assertEqual(config.refresh_interval(), config.DEFAULT_REFRESH_INTERVAL)


class ToggleHideArchivedTest(unittest.TestCase):
    def test_first_toggle_hides_archived_projects(self):
        settings = {}
        self.assertTrue(toggle_hide_archived(settings))
        self.assertEqual(settings, {'hide_archived': True})

    def test_second_toggle_shows_them_again(self):
        settings = {}
        toggle_hide_archived(settings)
        self.assertFalse(toggle_hide_archived(settings))
        self.assertEqual(settings, {'hide_archived': False})


class VisibleProjectsTest(unittest.TestCase):
    def test_keeps_archived_projects_when_not_hiding(self):
        self.assertEqual(visible_projects([ACTIVE, ARCHIVED], False), [ACTIVE, ARCHIVED])

    def test_drops_archived_projects_when_hiding(self):
        self.assertEqual(visible_projects([ACTIVE, ARCHIVED], True), [ACTIVE])

    def test_treats_projects_without_archived_field_as_active(self):
        legacy = {key: value for key, value in ACTIVE.items() if key != 'archived'}
        self.assertEqual(visible_projects([legacy], True), [legacy])

    def test_marks_archived_projects_in_subtitle(self):
        self.assertEqual(project_subtitle(ARCHIVED), 'group/old (archived)')
        self.assertEqual(project_subtitle(ACTIVE), 'group/active')


class SlimProjectTest(unittest.TestCase):
    def test_keeps_only_fields_the_script_filter_reads(self):
        api_project = dict(ARCHIVED, description='x', namespace={'id': 9}, star_count=3)
        self.assertEqual(slim_project(api_project), ARCHIVED)


if __name__ == '__main__':
    unittest.main()
