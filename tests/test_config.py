#!/usr/bin/python
#
# This file is a part of EM Media Handler Testing Module
# Copyright (c) 2014 Erin Morelli
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

    # _find_module success case
    def test_find_module_success(self):
        mod_yes = Config._find_module('mediahandler', 'util')
        self.assertTrue(mod_yes)

    # _find_module failure case
    def test_find_module_failure(self):
        module = _common.random_string(8)
        submod = _common.random_string(5)
        regex = "Module %s.%s is not installed" % (module, submod)
        self.assertRaisesRegexp(ImportError, regex,
                                Config._find_module, module, submod)


class InitLoggingTests(unittest.TestCase):

    def setUp(self):
        # Unique test ID
        self.id = _common.get_test_id()
        # Temp file
        self.log_file = _common.temp_file()

    def tearDown(self):
        # Remove tmp file
        if self.log_file != '':
            os.unlink(self.log_file)

    def test_init_logging(self):
        # Use custom settings
        settings = {
            'Logging': {
                'log_file': self.log_file,
                'level': 20,
            },
            'Deluge': {
                'enabled': False,
            },
        }
        # Send to logging config
        Config.init_logging(settings)
        # Make messages
        logging.error("Error message %s", self.id)
        logging.info("Info message %s", self.id)
        logging.debug("Debug message %s", self.id)
        # Read logfile
        with open(self.log_file) as log:
            log_content = log.read()
        # Regexes
        error = r"ERROR - Error message %s\n" % self.id
        info = r"INFO - Info message %s\n" % self.id
        debug = r"DEBUG- Debug message %s\n" % self.id
        # Look for them
        self.assertTrue(os.path.isfile(self.log_file))
        self.assertRegexpMatches(log_content, error)
        self.assertRegexpMatches(log_content, info)
        self.assertNotRegexpMatches(log_content, debug)


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
        self.assertIs(string_null, None)
        # Valid case
        string_reg = Config._get_valid_string(self.parser, 'Deluge', 'host')
        self.assertTrue(string_reg)

    def test_valid_number(self):
        # Empty string case
        num_null = Config._get_valid_number(self.parser, 'Audiobooks', 'folder')
        self.assertIs(num_null, None)
        # Valid case
        num_reg = Config._get_valid_number(self.parser, 'Deluge', 'port')
        self.assertEqual(num_reg, 58846)


class FileValidationConfigTests(unittest.TestCase):

    def setUp(self):
        self.tmp_file = ''
        # Get original conf file
        self.old_conf = _common.get_conf_file()
        # Setup temp conf path
        conf_dir = os.path.dirname(self.old_conf)
        self.new_conf = os.path.join(conf_dir, 'temp_FVCT.conf')
        # Copy into temp file
        shutil.copy(self.old_conf, self.new_conf)

    def tearDown(self):
        os.unlink(self.new_conf)
        if self.tmp_file != '':
            os.unlink(self.tmp_file)

    def test_valid_file(self):
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.new_conf),
            suffix='.log',
            delete=False)
        self.tmp_file = get_file.name
        get_file.close()
        self.modify_conf_file_options(self.tmp_file)
        parser = CP.ConfigParser()
        parser.read(self.new_conf)
        # Empty string case
        file_null = Config._get_valid_file(parser, 'Deluge', 'user')
        self.assertIs(file_null, None)
        # Valid case
        file_good = Config._get_valid_file(parser, 'Music', 'log_file')
        self.assertEqual(file_good, self.tmp_file)
        # Invalid case
        regex = "Path to file provided for 'Logging: log_file' does not exist:"
        self.assertRaisesRegexp(CP.Error, regex,
                                Config._get_valid_file, parser, 'Logging', 'log_file')

    def test_valid_folder(self):
        tmp_folder = tempfile.gettempdir()
        self.modify_conf_folder_options(tmp_folder)
        parser = CP.ConfigParser()
        parser.read(self.new_conf)
        # Empty string case
        folder_null = Config._get_valid_file(parser, 'Deluge', 'pass')
        self.assertIs(folder_null, None)
        # Valid case
        folder_good = Config._get_valid_file(parser, 'TV', 'folder')
        self.assertEqual(folder_good, tmp_folder)
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
        return

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
        return


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
        return


def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
