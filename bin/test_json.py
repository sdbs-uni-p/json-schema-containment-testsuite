#! /usr/bin/env python3
# This file is used to check the JSON Schema validation of our test suite
from __future__ import print_function
from pprint import pformat
import argparse
import errno
import fnmatch
import json
import os
import random
import shutil
import sys
import textwrap
import unittest
import warnings

if getattr(unittest, "skipIf", None) is None:
    unittest.skipIf = lambda cond, msg: lambda fn: fn

try:
    import jsonschema.validators
except ImportError:
    jsonschema = None

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir).rstrip("__pycache__"),
)
SUITE_ROOT_DIR = os.path.join(ROOT_DIR, "tests")

with open(os.path.join(ROOT_DIR, "test-schema.json"), 'r') as schema:
    TESTSUITE_SCHEMA = json.load(schema)


def files(paths):
    for path in paths:
        with open(path, 'r') as test_file:
            yield json.load(test_file)


def groups(paths):
    for test_file in files(paths):
        for group in test_file:
            yield group


def cases(paths):
    for test_group in groups(paths):
        yield test_group


def collect(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for filename in fnmatch.filter(files, "*.json"):
            yield os.path.join(root, filename)


class SanityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Looking for tests in %s" % SUITE_ROOT_DIR)
        cls.test_files = list(collect(SUITE_ROOT_DIR))
        print("Found %s test files" % len(cls.test_files))
        assert cls.test_files, "Didn't find the test files!"

    def test_all_files_are_valid_json(self):
        for path in self.test_files:
            with open(path, 'r') as test_file:
                try:
                    json.load(test_file)
                except ValueError as error:
                    self.fail("%s contains invalid JSON (%s)" % (path, error))

    @unittest.skipIf(jsonschema is None, "Validation library not present!")
    def test_all_schemas_are_valid(self):
        for schema in os.listdir(SUITE_ROOT_DIR):
            schema_validator = jsonschema.validators.validators.get(schema)
            if schema_validator is not None:
                test_files = collect(os.path.join(SUITE_ROOT_DIR, schema))
                for case in cases(test_files):
                    try:
                        schema_validator.check_schema(case["schema1"])
                        schema_validator.check_schema(case["schema2"])
                    except jsonschema.SchemaError as error:
                        self.fail("%s contains an invalid schema (%s)" %
                                  (case, error))
            else:
                warnings.warn("No schema validator for %s" % schema)

    @unittest.skipIf(jsonschema is None, "Validation library not present!")
    def test_suites_are_valid(self):
        Validator = jsonschema.validators.validator_for(TESTSUITE_SCHEMA)
        validator = Validator(TESTSUITE_SCHEMA)
        for tests in files(self.test_files):
            try:
                validator.validate(tests)
            except jsonschema.ValidationError as error:
                self.fail(str(error))

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(SanityTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())