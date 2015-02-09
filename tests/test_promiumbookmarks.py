#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_promiumbookmarks
----------------------------------

Tests for `promiumbookmarks` module.
"""

import unittest

from promiumbookmarks import promiumbookmarks
promiumbookmarks

import collections
import itertools
import json


class TestPromiumbookmarks(unittest.TestCase):

    def setUp(self):
        self.bookmarks_path = './tests/data/Bookmarks'

    def log(self, *args):
        print(args)

    def tearDown(self):
        pass

    def test_00_imports(self):
        import promiumbookmarks.promiumbookmarks as pb
        pb
        import promiumbookmarks.plugins.datebasedfolders as dbf
        dbf

    def test_01_list_bookmarks(self):
        from promiumbookmarks.promiumbookmarks import list_profile_bookmarks
        output = list_profile_bookmarks()
        self.assertTrue(hasattr(output, '__iter__'))
        output = list(output)
        self.assertTrue(len(output))
        output = list_profile_bookmarks(show_backups=True)
        self.assertTrue(hasattr(output, '__iter__'))
        output = list(output)
        self.assertTrue(len(output))

    def test_11_read_bookmarks(self):
        from promiumbookmarks.promiumbookmarks import ChromiumBookmarks
        bookmarks = ChromiumBookmarks.read_bookmarks(self.bookmarks_path)
        self.assertTrue(bookmarks)

    def a_test_21_print_bookmarks(self):
        from promiumbookmarks.promiumbookmarks import ChromiumBookmarks
        bookmarks = ChromiumBookmarks.read_bookmarks(self.bookmarks_path)
        output = ChromiumBookmarks.print_bookmarks(bookmarks)
        self.assertTrue(output)

    def test_31_walk_bookmarks(self):
        from promiumbookmarks.promiumbookmarks import ChromiumBookmarks
        bookmarks = ChromiumBookmarks.read_bookmarks(self.bookmarks_path)
        self.assertTrue(bookmarks)
        bookmarks = itertools.chain(
            ChromiumBookmarks.walk_bookmarks(
                bookmarks['roots']['bookmark_bar']),
            ChromiumBookmarks.walk_bookmarks(
                bookmarks['roots']['other']))
        bookmarks = list(bookmarks)
        length = len(bookmarks)
        self.log("n: %d" % length)
        counts = collections.Counter(b.id for b in bookmarks)
        duplicates = [(k, v) for (k, v) in counts.iteritems() if v > 1]
        self.log("counts: %r" % duplicates)
        self.assertFalse(duplicates)

    def test_33_iter_bookmarks(self):
        from promiumbookmarks.promiumbookmarks import ChromiumBookmarks
        bookmarks = list(ChromiumBookmarks.iter_bookmarks(self.bookmarks_path))
        self.assertTrue(bookmarks)

    def test_41_reorganize_by_date(self):
        from promiumbookmarks.promiumbookmarks import ChromiumBookmarks
        bookmarks = list(ChromiumBookmarks.iter_bookmarks(self.bookmarks_path))
        import promiumbookmarks.plugins.datebasedfolders as dbf
        print(dir(dbf))
        output = dbf.DateBasedFoldersPlugin.reorganize_by_date(bookmarks)
        self.assertTrue(output)
        json_output = json.dumps(output, indent=2)
        self.assertTrue(json_output)

    def test_51_rewrite_bookmarks(self):
        from promiumbookmarks.promiumbookmarks import ChromiumBookmarks
        bookmarks_dict = ChromiumBookmarks.transform_bookmarks_dict(
            self.bookmarks_path)
        bookmarks_json = ChromiumBookmarks.to_json(bookmarks_dict)
        ChromiumBookmarks.overwrite_bookmarks_json(
            bookmarks_json, self.bookmarks_path,
            prompt=False)
        output_json = json.dumps(bookmarks_dict, indent=2)
        self.assertTrue(json.loads(output_json), bookmarks_dict)

    def test_60_get_option_parser(self):
        from promiumbookmarks.promiumbookmarks import get_option_parser
        prs = get_option_parser()
        self.assertTrue(prs)

    def test_61_main(self):
        from promiumbookmarks.promiumbookmarks import main
        import sys
        __sys_argv = sys.argv
        sys.argv = [__file__]

        try:
            with self.assertRaises(IOError):
                output = main()
                self.assertEqual(output, 0)
                output = main('-v')
                self.assertEqual(output, 0)
                output = main('--print-all')
                self.assertEqual(output, 0)

            output = main('-v', './tests/data/Bookmarks')
            self.assertEqual(output, 0)
            output = main('--print-all', './tests/data/Bookmarks')
            self.assertEqual(output, 0)
        finally:
            sys.argv = __sys_argv

    def test_81_plugins(self):
        import promiumbookmarks.plugins.null
        import promiumbookmarks.plugins.dedupe
        import promiumbookmarks.plugins.bookmarkletsfolder
        import promiumbookmarks.plugins.chromefolder
        import promiumbookmarks.plugins.datebasedfolders
        import promiumbookmarks.plugins.allinone
        import promiumbookmarks.plugins.starred

    def test_91_promiumbookmarks(self):
        from promiumbookmarks.promiumbookmarks import ChromiumBookmarks
        cb = ChromiumBookmarks(self.bookmarks_path)
        output = list(cb)
        self.assertTrue(output)

        import promiumbookmarks.plugins.datebasedfolders as dbf
        output = dbf.DateBasedFoldersPlugin().reorganize_by_date(output)
        self.assertTrue(output)

        output = cb.overwrite(prompt=False)
        self.assertTrue(output)


#   class Test0PluginManager(unittest.TestCase):
#       def test_00_get_plugins(self):
#           from promiumbookmarks.promiumbookmarks import PluginManager
#           output = PluginManager.get_plugins()
#           self.assertTrue(output)
#           x = list(output)
#           self.assertTrue(x)
#
#       def test_00_list_plugins(self):
#           from promiumbookmarks.promiumbookmarks import PluginManager
#           output = PluginManager.list_plugins()
#           self.assertTrue(output)
#           x = list(output)
#           self.assertTrue(x)

if __name__ == '__main__':
    unittest.main()
