#!/usr/bin/python
#
# This file is a part of EM Media Handler Testing Module
# Copyright (c) 2014-2015 Erin Morelli
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
'''Initialize module'''

import os
import re
import sys
import shutil
from pwd import getpwuid

import _common
from _common import unittest
from _common import tempfile
from _common import MHTestSuite

import mediahandler.util.config as Config


class FindModulesTests(unittest.TestCase):

    def test_find_module_success(self):
        mod_yes = Config._find_module('mediahandler', 'util')
        self.assertTrue(mod_yes)

    def test_find_module_failure(self):
        module = _common.random_string(8)
        submod = _common.random_string(5)
        regex = r'Module {0}.{1} is not installed'.format(module, submod)
        self.assertRaisesRegexp(ImportError, regex,
                                Config._find_module, module, submod)

    def test_find_app_success(self):
        settings = _common.get_settings()['TV']
        app = {'name': 'Filebot', 'exec': 'filebot'}
        Config._find_app(settings, app)
        self.assertIn('filebot', settings.keys())

    def test_find_app_failure(self):
        settings = _common.get_settings()['Movies']
        app = {'name': 'NotReal', 'exec': 'notreal.php'}
        regex = r'NotReal application not found'
        self.assertRaisesRegexp(
            ImportError, regex, Config._find_app, settings, app)


class CheckModulesTests(unittest.TestCase):

    def setUp(self):
        # Get settings
        self.settings = _common.get_settings()
        # Remove settings we are testing for
        del self.settings['TV']['filebot']
        del self.settings['Movies']['filebot']
        if 'abc' in self.settings['Audiobooks'].keys():
            del self.settings['Audiobooks']['abc']
            del self.settings['Audiobooks']['php']

    def test_check_logging(self):
        # Modify settings
        self.settings['Logging']['enabled'] = True
        # Run
        result = Config._check_modules(self.settings)
        self.assertIsNone(result)

    @_common.skipUnlessHasMod('deluge', 'ui')
    def test_check_deluge(self):
        # Modify settings
        self.settings['Deluge']['enabled'] = True
        # Run
        result = Config._check_modules(self.settings)
        self.assertIsNone(result)

    def test_check_filebot(self):
        # Modify settings
        self.settings['TV']['enabled'] = True
        self.settings['Movies']['enabled'] = False
        # Run
        result = Config._check_modules(self.settings)
        self.assertIsNone(result)
        self.assertIn('filebot', self.settings['TV'].keys())
        self.assertNotIn('filebot', self.settings['Movies'].keys())
        # Modify settings again
        self.settings['Movies']['enabled'] = True
        # Run2
        result2 = Config._check_modules(self.settings)
        self.assertIsNone(result2)
        self.assertIn('filebot', self.settings['Movies'].keys())

    def test_audiobook_module(self):
        # Modify settings
        self.settings['Audiobooks']['enabled'] = True
        self.settings['Audiobooks']['make_chapters'] = False
        # Run
        result = Config._check_modules(self.settings)
        self.assertIsNone(result)
        self.assertNotIn('abc', self.settings['Audiobooks'].keys())
        self.assertNotIn('php', self.settings['Audiobooks'].keys())

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires a Linux system")
    def test_audiobook_good_abc_(self):
        # Modify settings
        self.settings['Audiobooks']['enabled'] = True
        self.settings['Audiobooks']['make_chapters'] = True
        # Run
        result = Config._check_modules(self.settings)
        self.assertIsNone(result)
        self.assertIn('abc', self.settings['Audiobooks'].keys())
        self.assertIn('php', self.settings['Audiobooks'].keys())

    @unittest.skipUnless(
        not sys.platform.startswith("linux"), "requires non-Linux system")
    def test_audiobook_bad_abc_(self):
        # Modify settings
        self.settings['Audiobooks']['enabled'] = True
        self.settings['Audiobooks']['make_chapters'] = True
        # Run
        regex = r'ABC application not found'
        self.assertRaisesRegexp(
            ImportError, regex, Config._check_modules, self.settings)

    @_common.skipUnlessHasMod('beets', 'util')
    def test_music_modules(self):
        # Modify settings
        self.settings['Music']['enabled'] = True
        # Run
        result = Config._check_modules(self.settings)
        self.assertIsNone(result)


class InitLoggingTests(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = _common.get_conf_file()
        # Unique test ID
        self.name = 'test-{0}'.format(_common.get_test_id())
        self.folder = _common.random_string(9)
        # Set logfile
        self.dir = os.path.join(os.path.dirname(self.conf), self.folder)
        self.log_file = os.path.join(self.dir, '{0}.log'.format(self.name))

    def tearDown(self):
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
        if os.path.exists(self.log_file):
            os.unlink(self.log_file)

    @_common.skipUnlessHasMod('deluge', 'log')
    def test_init_logging(self):
        # Use custom settings
        settings = {
            'Logging': {
                'log_file': self.log_file,
                'level': 20,
            },
            'Deluge': {
                'enabled': True,
            },
        }
        # # Send to logging config
        self.assertIsNone(Config._init_logging(settings))
        self.assertTrue(os.path.exists(self.dir))


class SimpleValidationConfigTests(unittest.TestCase):

    def setUp(self):
        self.settings = _common.get_settings()

    def test_valid_bool(self):
        # Empty string case
        bool_null = Config._get_valid_bool('Deluge', 'user', None)
        self.assertFalse(bool_null)
        # Valid case
        bool_reg = Config._get_valid_bool('TV', 'enabled', True)
        self.assertTrue(bool_reg)
        # Bad case
        regex = r'Value provided for \'Sect: opt\' is not a valid boolean'
        self.assertRaisesRegexp(
            ValueError, regex,
            Config._get_valid_bool, 'Sect', 'opt', 'astring')

    def test_valid_string(self):
        # Empty string case
        string_null = Config._get_valid_string('Deluge', 'pass', None)
        self.assertIsNone(string_null)
        # Valid case
        value_reg = self.settings['Deluge']['host']
        string_reg = Config._get_valid_string('Deluge', 'host', value_reg)
        self.assertIs(type(string_reg), str)
        self.assertEqual(string_reg, '127.0.0.1')
        # Bad case
        regex = r'Value provided for \'Sect: opt\' is not a valid string'
        self.assertRaisesRegexp(
            ValueError, regex, Config._get_valid_string, 'Sect', 'opt', 6789)

    def test_valid_number(self):
        # Empty string case
        num_null = Config._get_valid_number('Audiobooks', 'folder', None)
        self.assertIsNone(num_null)
        # Valid case
        value_reg = self.settings['Deluge']['port']
        num_reg = Config._get_valid_number('Deluge', 'port', value_reg)
        self.assertIs(type(num_reg), int)
        self.assertEqual(num_reg, 58846)
        # Bad case
        regex = r'Value provided for \'Sect: opt\' is not a valid number'
        self.assertRaisesRegexp(
            ValueError, regex,
            Config._get_valid_number, 'Sect', 'opt', 'astring')


class FileValidationConfigTests(unittest.TestCase):

    def setUp(self):
        # Get original conf file
        self.conf = _common.get_conf_file()
        # Setup temp conf path
        conf_dir = os.path.dirname(self.conf)
        self.new_conf = os.path.join(conf_dir, 'temp_FVCT.yml')
        # Copy into temp file
        shutil.copy(self.conf, self.new_conf)
        # Placholders
        self.tmp_file = ''
        self.dir = ''

    def tearDown(self):
        os.unlink(self.new_conf)
        if os.path.exists(self.tmp_file):
            os.unlink(self.tmp_file)
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)

    def test_valid_file(self):
        self.tmp_file = _common.make_tmp_file('.log')
        # Empty string case
        file_null = Config._get_valid_file('Deluge', 'user', None)
        self.assertIsNone(file_null)
        # Valid case
        file_good = Config._get_valid_file('Music', 'log_file', self.tmp_file)
        self.assertEqual(file_good, self.tmp_file)
        # Invalid case
        log_file = os.path.join('path', 'to', 'log.log')
        regex = "File path provided for 'Logging: log_file' does not exist:"
        self.assertRaisesRegexp(
            ValueError, regex,
            Config._get_valid_file, 'Logging', 'log_file', log_file)

    def test_valid_folder(self):
        self.dir = self.dir = tempfile.mkdtemp(
            dir=os.path.dirname(self.conf))
        # Empty string case
        folder_null = Config._get_valid_folder('Deluge', 'pass', None)
        self.assertIsNone(folder_null)
        # Valid case
        folder_good = Config._get_valid_folder('TV', 'folder', self.dir)
        self.assertEqual(folder_good, self.dir)
        # Invalid case
        mov_folder = os.path.join('path', 'to', 'movies')
        regex = r"Path provided for 'Movies: folder' does not exist: .*"
        self.assertRaisesRegexp(
            ValueError, regex,
            Config._get_valid_folder, 'Movies', 'folder', mov_folder)


class MissingSectionConfigTest(unittest.TestCase):

    def setUp(self):
        # Get original conf file
        self.old_conf = _common.get_conf_file()
        # Setup temp conf path
        conf_dir = os.path.dirname(self.old_conf)
        self.new_conf = os.path.join(conf_dir, 'temp_MSCT.yml')
        # Copy into temp file
        shutil.copy(self.old_conf, self.new_conf)

    def tearDown(self):
        os.unlink(self.new_conf)

    def test_missing_section(self):
        self.remove_conf_section()
        settings = _common.get_settings(self.new_conf)
        expected = {
            'enabled': False,
            'notify_name': None,
            'pushover': {
                'api_key': None,
                'user_key': None,
            },
            'pushbullet': {
                'token': None,
            }
        }
        self.assertDictEqual(expected, settings['Notifications'])

    def remove_conf_section(self):
        # Get conf file content
        with open(self.new_conf) as conf_file:
                conf_content = conf_file.read()
        # Set up new file content
        regex = r'(Notifications:(.|\n)*)notify_name:\s'
        # Make updates
        conf_content = re.sub(regex, r'\1', conf_content)
        # Write new file
        new_conf = open(self.new_conf, 'w')
        new_conf.write(conf_content)
        new_conf.close()
        return


class MissingOptionConfigTest(unittest.TestCase):

    def setUp(self):
        old_conf = _common.get_conf_file()
        conf_dir = os.path.dirname(old_conf)
        self.conf = os.path.join(conf_dir, 'temp_MOCT.yml')
        shutil.copy(old_conf, self.conf)
        self.remove_conf_option()

    def tearDown(self):
        os.unlink(self.conf)

    def test_missing_option(self):
        settings = Config.parse_config(self.conf)
        self.assertIn('host', settings['Deluge'].keys())
        self.assertEqual(settings['Deluge']['host'], '127.0.0.1')

    def remove_conf_option(self):
        # Get conf file content
        with open(self.conf) as conf_file:
                conf_content = conf_file.read()
        # Set up new file content
        regex = r'(Deluge:(.|\n)*)host: 127.0.0.1'
        # Make updates
        conf_content = re.sub(regex, r"\1", conf_content)
        # Write new file
        new_conf = open(self.conf, 'w')
        new_conf.write(conf_content)
        new_conf.close()


class MissingOptionSectionConfigTest(unittest.TestCase):

    def setUp(self):
        old_conf = _common.get_conf_file()
        conf_dir = os.path.dirname(old_conf)
        self.conf = os.path.join(conf_dir, 'temp_MOSCT.yml')
        shutil.copy(old_conf, self.conf)
        self.remove_conf_option()

    def tearDown(self):
        os.unlink(self.conf)

    def test_missing_option(self):
        settings = Config.parse_config(self.conf)['Notifications']
        self.assertIn('api_key', settings['pushover'].keys())
        self.assertIsNone(settings['pushover']['api_key'])

    def remove_conf_option(self):
        # Get conf file content
        with open(self.conf) as conf_file:
                conf_content = conf_file.read()
        # Set up new file content
        regex = r'(Notifications:(.|\n)*)pushover:(.|\n)*user_key:'
        # Make updates
        conf_content = re.sub(regex, r"\1", conf_content)
        # Write new file
        new_conf = open(self.conf, 'w')
        new_conf.write(conf_content)
        new_conf.close()


class MakeConfigTests(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = os.path.join(
            os.path.expanduser("~"), '.config', 'mediahandler', 'config.yml')
        self.name = _common.get_test_id()
        # New conf
        self.tmp_file = ''
        self.maxDiff = None

    def tearDown(self):
        folder = os.path.join(os.path.dirname(self.conf), 'tmp')
        if os.path.exists(folder):
            shutil.rmtree(folder)
        if os.path.exists(self.tmp_file):
            os.unlink(self.tmp_file)

    def test_default_conf(self):
        new_conf = Config.make_config()
        self.assertEqual(new_conf, self.conf)

    @unittest.skipIf('SUDO_UID' in os.environ.keys(), 'for non-sudoers only')
    def test_bad_conf(self):
        self.tmp_file = _common.make_tmp_file('.yml')
        os.chmod(self.tmp_file, 0o000)
        regex = r'Configuration file cannot be opened'
        self.assertRaisesRegexp(
            Warning, regex, Config.make_config, self.tmp_file)

    @unittest.skipUnless('SUDO_UID' in os.environ.keys(), 'for sudoers only')
    def test_conf_permissions(self):
        self.tmp_file = os.path.join(
            os.path.dirname(self.conf), '{0}.yml'.format(self.name))
        file_path = Config.make_config(self.tmp_file)
        self.assertEqual(
            int(os.environ['SUDO_UID']), self.get_owner(file_path))

    def test_custom_conf(self):
        name = 'test-{0}.conf'.format(_common.get_test_id())
        self.tmp_file = os.path.join(os.path.dirname(self.conf), 'tmp', name)
        results = Config.make_config(self.tmp_file)
        self.assertEqual(self.tmp_file, results)
        # Check formatting
        expected = Config.parse_config(self.conf)
        settings = Config.parse_config(results)
        self.assertListEqual(settings.keys(), expected.keys())

    def get_owner(self, filename):
        return getpwuid(os.stat(filename).st_uid).pw_uid


def suite():
    s = MHTestSuite()
    tests = unittest.TestLoader().loadTestsFromName(__name__)
    s.addTest(tests)
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2)
