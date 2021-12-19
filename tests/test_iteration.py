# This file is part of utils.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# Use of this source code is governed by a 3-clause BSD-style
# license that can be found in the LICENSE file.
#

import itertools
import unittest

from lsst.utils.iteration import chunk_iterable, ensure_iterable, isplit


class IterationTestCase(unittest.TestCase):
    """Tests for `iterable` helper."""

    def testIterable(self):
        test_data = (
            # Boolean indicates to test that we know it's
            # meant to be returned unchanged.
            (0, False),
            ("hello", False),
            ({1: 2, 3: 4}, False),
            ([0, 1, 2], True),
            (["hello", "world"], True),
            ({"a", "b", "c"}, True),
        )

        for data, is_iterable in test_data:
            iterator = ensure_iterable(data)
            if not is_iterable:
                # Turn into a list so we can check against the
                # expected result.
                data = [data]
            for original, from_iterable in itertools.zip_longest(data, iterator):
                self.assertEqual(original, from_iterable)

    def testChunking(self):
        """Chunk iterables."""
        simple = list(range(101))
        out = []
        n_chunks = 0
        for chunk in chunk_iterable(simple, chunk_size=10):
            out.extend(chunk)
            n_chunks += 1
        self.assertEqual(out, simple)
        self.assertEqual(n_chunks, 11)

        test_dict = {k: 1 for k in range(101)}
        n_chunks = 0
        for chunk in chunk_iterable(test_dict, chunk_size=45):
            # Subtract 1 for each key in chunk
            for k in chunk:
                test_dict[k] -= 1
            n_chunks += 1
        # Should have matched every key
        self.assertEqual(sum(test_dict.values()), 0)
        self.assertEqual(n_chunks, 3)

    def testIsplit(self):
        # Test compatibility with str.split
        seps = ("\n", " ", "d")
        input_str = "ab\ncd ef\n"

        for sep in seps:
            for input in (input_str, input_str.encode()):
                test_sep = sep.encode() if isinstance(input, bytes) else sep
                isp = list(isplit(input, sep=test_sep))
                ssp = input.split(test_sep)
                self.assertEqual(isp, ssp)


if __name__ == "__main__":
    unittest.main()
