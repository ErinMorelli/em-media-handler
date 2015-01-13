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
import logging

import _common
from _common import unittest
from _common import tempfile

import mediahandler.util.config as Config

try:
    import ConfigParser as CP
except ImportError:
    import configparser as CP


class FindModulesTests(unittest.TestCase):

    def test_find_module_success(self):
        mod_yes = Config._find_module('mediahandler', 'util')
        self.assertTrue(mod_yes)

    def test_find_module_failure(self):
        module = _common.random_string(8)
        submod = _common.random_string(5)
        regex = "Module %s.%s is not installed" % (module, submod)
        self.assertRaisesRegexp(ImportError, regex,
                                Config._find_module, module, submod)


class CheckModulesTests(unittest.TestCase):

    def setUp(self):
        # Get settings
        self.settings = _common.get_settings()
        # Bypass unneeded sections
        self.settings['has_filebot'] = False 
    
    def test_check_logging(self):
        # Modify settings
        self.settings['Logging']['enabled'] = True 
        # Run
        result = Config._check_modules(self.settings)
        self.assertIsNone(result)

    def test_check_deluge(self):
        # Modify settings
        self.settings['Deluge']['enabled'] = True 
        # Run
        result = Config._check_modules(self.settings)
        self.assertIsNone(result)

    def test_check_filebot(self):
        # Modify settings
        self.settings['TV']['enabled'] = True    
        # Run
        result = Config._check_modules(self.settings)
        self.assertIsNone(result)
        self.assertTrue(self.settings['has_filebot'])

    def test_audiobook_module(self):
        # Modify settings
        self.settings['Audiobooks']['enabled'] = True
        self.settings['Audiobooks']['make_chapters'] = False
        # Run
        result = Config._check_modules(self.settings)
        self.assertIsNone(result)

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Ubuntu")
    def test_audiobook_good_abc_(self):
        # Modify settings
        self.settings['Audiobooks']['enabled'] = True
        self.settings['Audiobooks']['make_chapters'] = True
        # Run
        result = Config._check_modules(self.settings)
        self.assertIsNone(result)

    @unittest.skipUnless(not sys.platform.startswith("linux"), "requires not Ubuntu")
    def test_audiobook_bad_abc_(self):
        # Modify settings
        self.settings['Audiobooks']['enabled'] = True
        self.settings['Audiobooks']['make_chapters'] = True
        # Run
        regex = r'ABC application not found'
        self.assertRaisesRegexp(
            ImportError, regex, Config._check_modules, self.settings)

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
        self.name = 'test-%s' % _common.get_test_id()
        self.folder = _common.random_string(9)
        # Set logfile
        self.dir = '%s/%s' % (os.path.dirname(self.conf), self.folder)
        self.log_file = '%s/%s.log' % (self.dir, self.name)

    def tearDown(self):
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
        if os.path.exists(self.log_file):
            os.unlink(self.log_file)

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
        self.assertIsNone(Config.init_logging(settings))
        self.assertTrue(os.path.exists(self.dir))


class SimpleValidationConfigTests(unittest.TestCase):

    def setUp(self):
        self.conf = _common.get_conf_file()
        self.parser = CP.ConfigParser()
        self.parser.read(self.conf)

    def test_valid_bool(self):
        # Empty string case
        bool_null = Config._get_valid_bool(self.parser, 'Deluge', 'user')
        self.assertFalse(bool_null)
        # Valid case
        bool_reg = Config._get_valid_bool(self.parser, 'TV', 'enabled')
        self.assertTrue(bool_reg)

    def test_valid_string(self):
        # Empty string case
        string_null = Config._get_valid_string(self.parser, 'Deluge', 'pass')
        self.assertIsNone(string_null)
        # Valid case
        string_reg = Config._get_valid_string(self.parser, 'Deluge', 'host')
        self.assertTrue(string_reg)

    def test_valid_number(self):
        # Empty string case
        num_null = Config._get_valid_number(self.parser, 'Audiobooks', 'folder')
        self.assertIsNone(num_null)
        # Valid case
        num_reg = Config._get_valid_number(self.parser, 'Deluge', 'port')
        self.assertEqual(num_reg, 58846)


class FileValidationConfigTests(unittest.TestCase):

    def setUp(self):
        # Get original conf file
        self.conf = _common.get_conf_file()
        # Setup temp conf path
        conf_dir = os.path.dirname(self.conf)
        self.new_conf = os.path.join(conf_dir, 'temp_FVCT.conf')
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
        self.modify_conf_file_options(self.tmp_file)
        parser = CP.ConfigParser()
        parser.read(self.new_conf)
        # Empty string case
        file_null = Config._get_valid_file(parser, 'Deluge', 'user')
        self.assertIsNone(file_null)
        # Valid case
        file_good = Config._get_valid_file(parser, 'Music', 'log_file')
        self.assertEqual(file_good, self.tmp_file)
        # Invalid case
        regex = "Path to file provided for 'Logging: log_file' does not exist:"
        self.assertRaisesRegexp(CP.Error, regex,
                                Config._get_valid_file, parser, 'Logging', 'log_file')

    def test_valid_folder(self):
        self.dir = self.dir = tempfile.mkdtemp(
            dir=os.path.dirname(self.conf))
        self.modify_conf_folder_options(self.dir)
        parser = CP.ConfigParser()
        parser.read(self.new_conf)
        # Empty string case
        folder_null = Config._get_valid_folder(parser, 'Deluge', 'pass')
        self.assertIsNone(folder_null)
        # Valid case
        folder_good = Config._get_valid_folder(parser, 'TV', 'folder')
        self.assertEqual(folder_good, self.dir)
        # Invalid case
        regex = r"Path provided for 'Movies: folder' does not exist: .*"
        self.assertRaisesRegexp(CP.Error, regex,
                                Config._get_valid_folder, parser, 'Movies', 'folder')

    def modify_conf_file_options(self, tmp_file):
        # Get conf file content
        with open(self.new_conf) as conf_file:
                conf_content = conf_file.read()
        # Set up new file content
        regex_file1 = r"(\[Music\]\n.*\n)log_file = \n"
        replace_file1 = r'\1log_file = %s\n' % tmp_file
        regex_file2 = r"(\[Logging\]\n.*\n.*\n)log_file = \n"
        replace_file2 = r"\1log_file = /path/to/fake.tmp\n"
        # Make updates
        conf_content = re.sub(regex_file1, replace_file1, conf_content)
        conf_content = re.sub(regex_file2, replace_file2, conf_content)
        # Write new file
        new_conf = open(self.new_conf, 'w')
        new_conf.write(conf_content)
        new_conf.close()

    def modify_conf_folder_options(self, tmp_file):
        # Get conf file content
        with open(self.new_conf) as conf_file:
                conf_content = conf_file.read()
        # Set up new folder content
        regex_folder1 = r"(\[TV\]\n.*\n)folder = \n"
        replace_folder1 = r"\1folder = %s\n" % tmp_file
        regex_folder2 = r"(\[Movies\]\n.*\n)folder = \n"
        replace_folder2 = r"\1folder = /path/to/fake\n"
        # Make updates
        conf_content = re.sub(regex_folder1, replace_folder1, conf_content)
        conf_content = re.sub(regex_folder2, replace_folder2, conf_content)
        # Write new file
        new_conf = open(self.new_conf, 'w')
        new_conf.write(conf_content)
        new_conf.close()


class MissingSectionConfigTest(unittest.TestCase):

    def setUp(self):
        # Get original conf file
        self.old_conf = _common.get_conf_file()
        # Setup temp conf path
        conf_dir = os.path.dirname(self.old_conf)
        self.new_conf = os.path.join(conf_dir, 'temp_MSCT.conf')
        # Copy into temp file
        shutil.copy(self.old_conf, self.new_conf)

    def tearDown(self):
        os.unlink(self.new_conf)

    def test_missing_section(self):
        self.remove_conf_section()
        regex = r"No section: 'Pushover'"
        self.assertRaisesRegexp(CP.NoSectionError, regex,
            _common.get_settings, self.new_conf)

    def remove_conf_section(self):
        # Get conf file content
        with open(self.new_conf) as conf_file:
                conf_content = conf_file.read()
        # Set up new file content
        regex = r"\[Pushover\](.|\n)*notify_name = \n"
        # Make updates
        conf_content = re.sub(regex, '', conf_content)
        # Write new file
        new_conf = open(self.new_conf, 'w')
        new_conf.write(conf_content)
        new_conf.close()
        return


class MissingOptionConfigTest(unittest.TestCase):

    def setUp(self):
        old_conf = _common.get_conf_file()
        conf_dir = os.path.dirname(old_conf)
        self.conf = os.path.join(conf_dir, 'temp_MOCT.conf')
        shutil.copy(old_conf, self.conf)
        self.remove_conf_option()

    def tearDown(self):
        os.unlink(self.conf)

    def test_missing_option(self):
        regex = r"No option 'user' in section: 'Deluge'"
        self.assertRaisesRegexp(CP.NoOptionError, regex,
            Config.parse_config, self.conf)

    def remove_conf_option(self):
        # Get conf file content
        with open(self.conf) as conf_file:
                conf_content = conf_file.read()
        # Set up new file content
        regex = r"(\[Deluge\]\n(.|\n)*)user =\s"
        # Make updates
        conf_content = re.sub(regex, r"\1", conf_content)
        # Write new file
        new_conf = open(self.conf, 'w')
        new_conf.write(conf_content)
        new_conf.close()


class MakeConfigTests(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = ('%s/.config/mediahandler/settings.conf' % 
                   os.path.expanduser("~")) 
        # New conf
        self.tmp_file = ''
        self.maxDiff = None

    def tearDown(self):
        folder = '%s/tmp' % os.path.dirname(self.conf)
        if os.path.exists(folder):
            shutil.rmtree(folder)
        if os.path.exists(self.tmp_file):
            os.unlink(self.tmp_file)

    def test_default_conf(self):
        new_conf = Config.make_config()
        self.assertEqual(new_conf, self.conf)

    @unittest.skipIf('SUDO_UID' in os.environ.keys(), 'for non-sudoers only')
    def test_bad_conf(self):
        self.tmp_file = _common.make_tmp_file('.conf')
        os.chmod(self.tmp_file, 0o000)
        regex = r'Configuration file cannot be opened'
        self.assertRaisesRegexp(
            Warning, regex, Config.make_config, self.tmp_file)

    def test_custom_conf(self):
        name = 'test-%s.conf' % _common.get_test_id()
        self.tmp_file = '%s/tmp/%s' % (os.path.dirname(self.conf), name)
        results = Config.make_config(self.tmp_file)
        self.assertEqual(self.tmp_file, results)
        # Check formatting
        expected = Config.parse_config(self.conf)
        settings = Config.parse_config(results)
        self.assertListEqual(settings.keys(), expected.keys())


def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
