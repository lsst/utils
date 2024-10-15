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

import itertools
import unittest

from lsst.utils.iteration import chunk_iterable, ensure_iterable, isplit, sequence_to_string


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

    def test_empty_list(self):
        """Test that an empty list returns an empty string."""
        self.assertEqual(sequence_to_string([]), "")

    def test_single_element(self):
        """Test a list with a single element returns it as a string."""
        self.assertEqual(sequence_to_string([5]), "5")

    def test_consecutive_numbers(self):
        """Test a list of consecutive numbers with stride 1."""
        self.assertEqual(sequence_to_string([1, 2, 3, 4, 5]), "1..5")

    def test_non_consecutive_numbers(self):
        """Test a list of non-consecutive numbers."""
        self.assertEqual(sequence_to_string([1, 3, 5, 7]), "1..7:2")

    def test_mixed_sequences(self):
        """Test a list with both consecutive and non-consecutive numbers."""
        self.assertEqual(sequence_to_string([1, 2, 3, 5, 7, 8, 9]), "1..3^5^7..9")

    def test_stride_greater_than_one(self):
        """Test sequences where the stride is greater than one."""
        self.assertEqual(sequence_to_string([2, 4, 6, 8]), "2..8:2")

    def test_negative_numbers(self):
        """Test a list that includes negative numbers."""
        self.assertEqual(sequence_to_string([-5, -4, -3, -1, 0, 1]), "-5..-3^-1..1")

    def test_duplicate_numbers(self):
        """Test a list with duplicate numbers."""
        self.assertEqual(sequence_to_string([1, 2, 2, 3, 4]), "1..4")

    def test_strings_with_common_prefix(self):
        """Test a list of strings with a common prefix."""
        self.assertEqual(sequence_to_string(["node1", "node2", "node3"]), "node1..node3")

    def test_strings_without_common_prefix(self):
        """Test a list of strings without a common prefix."""
        self.assertEqual(sequence_to_string(["alpha", "beta", "gamma"]), "alpha^beta^gamma")

    def test_large_sequence(self):
        """Test a large sequence of consecutive numbers."""
        large_list = list(range(1, 101))
        self.assertEqual(sequence_to_string(large_list), "1..100")

    def test_mixed_types(self):
        """Test a list with mixed data types."""
        with self.assertRaises(TypeError):
            sequence_to_string([1, "2", 3])

    def test_wrong_types(self):
        """Test that passing floats raises an appropriate exception."""
        with self.assertRaises(TypeError):
            sequence_to_string([1, 2, 3, 1.2])

    def test_stride_calculation(self):
        """Test that the stride is correctly calculated for single strides."""
        self.assertEqual(sequence_to_string([1, 3, 5, 7, 9]), "1..9:2")

    def test_single_value_sequences(self):
        """Test sequences that should remain as single values."""
        self.assertEqual(sequence_to_string([1, 3, 6, 10]), "1^3^6^10")

    def test_overlapping_ranges(self):
        """Test a list with duplicate values"""
        self.assertEqual(sequence_to_string([1, 2, 2, 3, 4, 4, 5]), "1..5")

    def test_unordered_input(self):
        """Test that the function correctly handles unordered input."""
        self.assertEqual(sequence_to_string([5, 3, 1, 4, 2]), "1..5")

    def test_large_stride(self):
        """Test sequences with a large stride."""
        self.assertEqual(sequence_to_string([10, 20, 30, 40]), "10..40:10")

    def test_single_character_strings(self):
        """Test a list of single-character strings."""
        self.assertEqual(sequence_to_string(["a", "b", "c"]), "a^b^c")

    def test_strings_with_prefix(self):
        """Test a list of longer strings."""
        self.assertEqual(
            sequence_to_string(
                [
                    "node1",
                    "node2",
                    "node3",
                    "node5",
                ]
            ),
            "node1..node3^node5",
        )


if __name__ == "__main__":
    unittest.main()
