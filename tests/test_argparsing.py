# This file is part of utils.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import logging
import unittest

from lsst.utils.argparsing import AppendDict

log = logging.getLogger("test_argparsing")


class AppendDictTestSuite(unittest.TestCase):
    """Test suite for AppendDict action."""

    def setUp(self):
        super().setUp()

        self.testbed = argparse.ArgumentParser()

    def test_default_none_positional(self):
        self.testbed.add_argument("test", action=AppendDict, nargs="*")

        namespace = self.testbed.parse_args([])
        self.assertEqual(namespace.test, {})

        namespace = self.testbed.parse_args("baz=bak".split())
        self.assertEqual(namespace.test, {"baz": "bak"})

    def test_default_none_keyword(self):
        self.testbed.add_argument("--test", action=AppendDict)

        namespace = self.testbed.parse_args([])
        self.assertEqual(namespace.test, {})

        namespace = self.testbed.parse_args("--test baz=bak".split())
        self.assertEqual(namespace.test, {"baz": "bak"})

    def test_default_empty_positional(self):
        self.testbed.add_argument("test", action=AppendDict, default={}, nargs="*")

        namespace = self.testbed.parse_args([])
        self.assertEqual(namespace.test, {})

        namespace = self.testbed.parse_args("baz=bak".split())
        self.assertEqual(namespace.test, {"baz": "bak"})

    def test_default_empty_keyword(self):
        self.testbed.add_argument("--test", action=AppendDict, default={})

        namespace = self.testbed.parse_args([])
        self.assertEqual(namespace.test, {})

        namespace = self.testbed.parse_args("--test baz=bak".split())
        self.assertEqual(namespace.test, {"baz": "bak"})

    def test_default_non_empty_positional(self):
        self.testbed.add_argument("test", action=AppendDict, default={"foo": "bar"}, nargs="*")

        namespace = self.testbed.parse_args([])
        self.assertEqual(namespace.test, {"foo": "bar"})

        namespace = self.testbed.parse_args("baz=bak".split())
        self.assertEqual(namespace.test, {"foo": "bar", "baz": "bak"})

        namespace = self.testbed.parse_args("foo=fum".split())
        self.assertEqual(namespace.test, {"foo": "fum"})

    def test_default_non_empty_keyword(self):
        self.testbed.add_argument("--test", action=AppendDict, default={"foo": "bar"})

        namespace = self.testbed.parse_args([])
        self.assertEqual(namespace.test, {"foo": "bar"})

        namespace = self.testbed.parse_args("--test baz=bak".split())
        self.assertEqual(namespace.test, {"foo": "bar", "baz": "bak"})

        namespace = self.testbed.parse_args("--test foo=fum".split())
        self.assertEqual(namespace.test, {"foo": "fum"})

    def test_default_invalid(self):
        with self.assertRaises(TypeError):
            self.testbed.add_argument("test", action=AppendDict, default="bovine")
        with self.assertRaises(TypeError):
            self.testbed.add_argument("test", action=AppendDict, default=[])

    def test_multi_append(self):
        self.testbed.add_argument("--test", action=AppendDict)

        namespace = self.testbed.parse_args("--test foo=bar --test baz=bak".split())
        self.assertEqual(namespace.test, {"foo": "bar", "baz": "bak"})

    def test_multi_nargs_append(self):
        self.testbed.add_argument("--test", action=AppendDict, nargs="*")

        namespace = self.testbed.parse_args("--test foo=bar fee=fum --test baz=bak --test".split())
        self.assertEqual(namespace.test, {"foo": "bar", "fee": "fum", "baz": "bak"})

    def test_emptyvalue(self):
        self.testbed.add_argument("test", action=AppendDict)

        namespace = self.testbed.parse_args("foo=".split())
        self.assertEqual(namespace.test, {"foo": ""})

    def test_nopair(self):
        self.testbed.add_argument("test", action=AppendDict)

        with self.assertRaises(ValueError):
            self.testbed.parse_args("foo".split())

        with self.assertRaises(ValueError):
            self.testbed.parse_args("assertion=beauty=truth".split())
