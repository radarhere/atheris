# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for RegEx match generation."""


import unittest
from atheris import gen_match


class RegexMatchGeneration(unittest.TestCase):

  def test_plain(self) -> None:
    match = gen_match("abc")
    self.assertEqual(match, "abc")

  def test_alternate1(self) -> None:
    match = gen_match("abc|def")
    self.assertIn(match, ["abc", "def"])

  def test_alternate2(self) -> None:
    pattern = r"(abc|\d+)"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_oneof(self) -> None:
    match = gen_match("[abc]abc")
    self.assertIn(match, ["aabc", "babc", "cabc"])

  def test_repeat_star(self) -> None:
    pattern = "abc*d"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_non_greedy_repeat_star(self) -> None:
    pattern = "abc*?d"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_repeat_plus(self) -> None:
    pattern = "abc+d"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_non_greedy_repeat_plus(self) -> None:
    pattern = "abc+?d"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_notoneof(self) -> None:
    match = gen_match("[^abc]def")
    if len(match) != 4:
      raise AssertionError(f"Unexpected generated match {match}")
    if not match.endswith("def"):
      raise AssertionError(f"Unexpected generated match {match}")
    if match[0] in "abc":
      raise AssertionError(f"Unexpected generated match {match}")

  def test_noncapturing(self) -> None:
    pattern = r"(?:abc){3,}"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_noncapturing2(self) -> None:
    pattern = r"(?:abc){,3}"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_lookahead_at_end(self) -> None:
    pattern = r"a(?=bc)"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)
    self.assertEqual(match, "abc")

  def test_lookbehind_at_beginning(self) -> None:
    pattern = r"(?<=a)bc"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)
    self.assertEqual(match, "abc")

  def test_ignores_lookahead_in_middle(self) -> None:
    pattern = r"xy(?=a)z"
    match = gen_match(pattern)
    self.assertEqual(match, "xyz")

  def test_ignores_lookbehind_in_middle(self) -> None:
    pattern = r"xy(?<=a)z"
    match = gen_match(pattern)
    self.assertEqual(match, "xyz")

  def test_ignores_negative_lookahead_in_middle(self) -> None:
    pattern = r"xy(?!z)z"
    match = gen_match(pattern)
    self.assertEqual(match, "xyz")

  def test_ignores_negative_lookbehind_in_middle(self) -> None:
    pattern = r"xy(?<!z)z"
    match = gen_match(pattern)
    self.assertEqual(match, "xyz")

  def test_unicode(self) -> None:
    match = gen_match("•")
    self.assertEqual(match, "•")

  def test_plain_bytes(self) -> None:
    match = gen_match(b"abc")
    self.assertEqual(match, b"abc")

  def test_non_ascii_non_utf8_bytes(self) -> None:
    pattern = b"ab*c\x80\x80de*f"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_utf8(self) -> None:
    match = gen_match("•".encode("utf-8"))
    self.assertEqual(match, b"\xe2\x80\xa2")

  def test_digits(self) -> None:
    pattern = r"\d"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_not_digits(self) -> None:
    pattern = r"\D"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_word(self) -> None:
    pattern = r"\w"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_not_word(self) -> None:
    pattern = r"\W"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_space(self) -> None:
    pattern = r"\s"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_not_space(self) -> None:
    pattern = r"\S"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_wildcard(self) -> None:
    pattern = r"a.bc"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_range_with_fixed_chars(self) -> None:
    pattern = r"[a-z1]bc"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_range(self) -> None:
    pattern = r"[a-z]bc"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_negative_range(self) -> None:
    pattern = r"[^a-z]bc"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)

  def test_negative_range_with_fixed_chars(self) -> None:
    pattern = r"[^a-z\\]bc"
    match = gen_match(pattern)
    self.assertRegex(match, pattern)


if __name__ == "__main__":
  unittest.main()
