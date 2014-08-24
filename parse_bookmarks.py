#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
parse_bookmarks -- a tool for working with Chromium Bookmarks JSON

Usage::

    ./parse_bookmarks --print-all ./path/to/Bookmarks
    ./parse_bookmarks --by-date ./path/to/Bookmarks
    ./parse_bookmarks --overwrite ./path/to/Bookmarks
"""

import codecs
import collections
import datetime
import functools
import itertools
import logging
import os
import json

from collections import namedtuple

DATETIME_CONST = 2**8 * 3**3 * 5**2 * 79 * 853

log = logging.getLogger()
log.setLevel(logging.DEBUG)

def longdate_to_datetime(t):
    if t is None:
        return
    t = long(t)
    return datetime.datetime.utcfromtimestamp((t*1e-6)-DATETIME_CONST)


class URL(
    namedtuple(
        'URL',
        'type id name url '
        'date_added date_added_ date_modified date_modified_')):

    def to_json(self):
        x = self._asdict()
        x.pop('date_added_')
        x.pop('date_modified_')
        return x

    @classmethod
    def from_url_node(cls, node):
        return cls(
            type=node.get('type'),
            id=node.get('id'),
            name=node.get('name'),
            url=node.get('url'),
            date_added=node.get('date_added'),
            date_added_=longdate_to_datetime(
                node.get('date_added')),
            date_modified=node.get('date_modified'),
            date_modified_=longdate_to_datetime(
                node.get('date_modified'))
        )


class Folder(
    namedtuple(
        'Folder',
        'type id name date_added date_added_ date_modified date_modified_')):
    pass

    @classmethod
    def from_folder_node(cls, node):
        return cls(
            type=node.get('type'),
            id=node.get('id'),
            name=node.get('name'),
            date_added=node.get('date_added'),
            date_added_=longdate_to_datetime(
                node.get('date_added')),
            date_modified=node.get('date_modified'),
            date_modified_=longdate_to_datetime(
                node.get('date_modified')))



class ChromiumBookmarks(object):

    def __init__(self, bookmarks_path):
       self.bookmarks_path = bookmarks_path
       self.bookmarks_json = self.read_bookmarks(self.bookmarks_path)

    @staticmethod
    def read_bookmarks(path):
        with codecs.open(path, encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def parse_bookmarks(bookmarks):
        """
        mainfunc
        """

    @staticmethod
    def print_bookmarks(bookmarks):
        for x in bookmarks:
            print(x)

        for x in bookmarks['roots']:
            print(x)
            # synced, bookmark_bar, other

        for x in bookmarks['roots']['bookmark_bar']:
            print(x)

        for x in bookmarks['roots']['bookmark_bar']['children']:
            print(x)
        return True

    @staticmethod
    def walk_bookmarks(node):
        """
        Walk a Chromium Bookmarks(.json) recursively; yielding folders and urls

        Args:
            node (dict): dict to traverse (type:url|folder, children:[]])

        Returns:
            generator of (type: folder || url) dicts
        """
        _type = node.get('type')
        if _type == 'folder':
            yield Folder.from_folder_node(node)
            for item in node['children']:
                _item_type = item.get('type')
                if _item_type == 'folder':
                    for b in ChromiumBookmarks.walk_bookmarks(item):
                        yield b
                elif _item_type == 'url':
                    yield URL.from_url_node(item)
        elif _type == 'url':
            yield URL.from_url_node(node)


    @classmethod
    def iter_bookmarks(cls, bookmarks_path, bookmarks_json=None):
        if bookmarks_json is None:
            bookmarks_json = cls.read_bookmarks(bookmarks_path)
        return itertools.chain(
            cls.walk_bookmarks(bookmarks_json['roots']['bookmark_bar']),
            cls.walk_bookmarks(bookmarks_json['roots']['other']))

    def __iter__(self):
        return ChromiumBookmarks.iter_bookmarks(self.bookmarks_path,
                                        bookmarks_json=self.bookmarks_json)

    @staticmethod
    def reorganize_by_date(bookmarks):
        """
        Reorganize bookmarks into date-based folders

        2014
        2014-08
            2014-08-22

        Args:
            bookmarks (iterable{}): iterable of Chromium Bookmarks JSON

        Returns:
            iterable{}: iterable of Chromium Bookmarks JSON

        """
        id_max = max(int(b.id) for b in bookmarks)
        ids = itertools.count(id_max + 1)

        bookmarks_by_day = itertools.groupby(
            sorted(bookmarks, key=lambda x: x.date_added_),
            lambda x: (x.date_added_.year,
                    x.date_added_.month,
                    x.date_added_.day))
        bookmarks_by_day = [(x, list(iterable))
                            for (x, iterable) in bookmarks_by_day]

        bookmarks_by_day_month = itertools.groupby(bookmarks_by_day,
                                                lambda x: x[0][:2])
        bookmarks_by_day_month = [(x, list(iterable))
                                for (x, iterable) in bookmarks_by_day_month]

        bookmarks_by_day_month_year = itertools.groupby(bookmarks_by_day_month,
                                                        lambda x: x[0][0])
        bookmarks_by_day_month_year = [
            (x, list(iterable)) for (x, iterable) in bookmarks_by_day_month_year]

        output = []
        for year, by_year in bookmarks_by_day_month_year:
            year_folder = {
                "type": "folder",
                "id": ids.next(),
                "name": str(year),
                "children": [],
                "date_added": "13053368494256041",
                "date_modified": "0",
            }
            for month, by_day in by_year:
                month_folder = {
                    "type": "folder",
                    "id": ids.next(),
                    "name": '-'.join(str(s) for s in month),
                    "children": [],
                    "date_added": "13053368494256041",
                    "date_modified": "0",
                }
                for day, iterable in by_day:
                    day_folder = {
                        "type": "folder",
                        "id": ids.next(),
                        "name": '-'.join(str(s) for s in day),
                        "children": [],
                        "date_added": "13053368494256041",
                        "date_modified": "0",
                    }
                    for b in iterable:
                        if b.type == 'url':
                            day_folder['children'].append(b.to_json())
                    month_folder['children'].append(day_folder)
                year_folder['children'].append(month_folder)
            output.append(year_folder)

        return output

    def reorganized_by_date(self):
        return ChromiumBookmarks.reorganize_by_date(self)

    @staticmethod
    def rewrite_bookmarks_json(bookmarks_path, dest=None, prompt=True,
                               func=reorganized_by_date):
        bookmarks = list(ChromiumBookmarks.iter_bookmarks(bookmarks_path))
        output = func(bookmarks)

        bookmarks_json = ChromiumBookmarks.read_bookmarks(bookmarks_path)
        if 'checksum' in bookmarks_json:
            bookmarks_json.pop('checksum')
        bookmarks_json['roots']['bookmark_bar']['children'] = output
        bookmarks_json['roots']['other']['children'] = []
        output_json = json.dumps(bookmarks_json, indent=2)
        assert json.loads(output_json) == bookmarks_json
        return output_json

    @staticmethod
    def overwrite_bookmarks_json(data, bookmarks_path, prompt=True):
        # TODO: if os.path.exists, prompt

        if os.path.exists(bookmarks_path):
            log.info("bookmarks_path exists: %r" % bookmarks_path)
            if prompt:
                yesno = raw_input("Overwrite y/[n]: ").lower().strip()
                if yesno not in ("y", "yes"):
                    raise Exception()
                    return False

        with codecs.open(bookmarks_path, 'w', encoding='utf8') as f:
            f.write(data)

        bkp_file = bookmarks_path + '.bak'
        os.path.exists(bkp_file) and os.remove(bkp_file)
        return True

    def overwrite(self, dest=None, prompt=True):
        if dest is None:
            dest = self.bookmarks_path
        output = ChromiumBookmarks.rewrite_bookmarks_json(self.bookmarks_path)
        return ChromiumBookmarks.overwrite_bookmarks_json(output, self.bookmarks_path, prompt=prompt)


import unittest


class Test_parse_bookmarks(unittest.TestCase):

    def setUp(self):
        self.bookmarks_path = './testdata/Bookmarks'

    def log(self, *args):
        print(args)

    def test_11_read_bookmarks(self):
        bookmarks = ChromiumBookmarks.read_bookmarks(self.bookmarks_path)
        self.assertTrue(bookmarks)

    def a_test_21_print_bookmarks(self):
        bookmarks = ChromiumBookmarks.read_bookmarks(self.bookmarks_path)
        output = ChromiumBookmarks.print_bookmarks(bookmarks)
        self.assertTrue(output)

    def test_31_walk_bookmarks(self):
        bookmarks = ChromiumBookmarks.read_bookmarks(self.bookmarks_path)
        self.assertTrue(bookmarks)
        bookmarks = itertools.chain(
            ChromiumBookmarks.walk_bookmarks(bookmarks['roots']['bookmark_bar']),
            ChromiumBookmarks.walk_bookmarks(bookmarks['roots']['other'])
        )
        bookmarks = list(bookmarks)
        length = len(bookmarks)
        self.log("n: %d" % length)
        counts = collections.Counter(b.id for b in bookmarks)
        duplicates = [(k, v) for (k, v) in counts.iteritems() if v > 1]
        self.log("counts: %r" % duplicates)
        self.assertFalse(duplicates)

    def test_33_iter_bookmarks(self):
        bookmarks = list(ChromiumBookmarks.iter_bookmarks(self.bookmarks_path))
        self.assertTrue(bookmarks)

    def test_41_reorganize_by_date(self):
        bookmarks = list(ChromiumBookmarks.iter_bookmarks(self.bookmarks_path))
        output = ChromiumBookmarks.reorganize_by_date(bookmarks)
        self.assertTrue(output)
        json_output = json.dumps(output, indent=2)
        self.assertTrue(json_output)

    def test_51_rewrite_bookmarks(self):
        bookmarks = list(ChromiumBookmarks.iter_bookmarks(self.bookmarks_path))
        bookmarks_json = ChromiumBookmarks.rewrite_bookmarks_json(
            self.bookmarks_path)
        ChromiumBookmarks.overwrite_bookmarks_json(
            bookmarks_json, self.bookmarks_path,
            prompt=False)
        output_json = json.dumps(bookmarks_json, indent=2)
        self.assertTrue(json.loads(output_json), bookmarks_json)

    def test_60_get_option_parser(self):
        prs = get_option_parser()
        self.assertTrue(prs)

    def test_61_main(self):
        import sys
        __sys_argv = sys.argv
        sys.argv = [__file__]
        try:
            output = main()
            self.assertEqual(output, 0)
            output = main('-v')
            self.assertEqual(output, 0)
            # output = main('-h')
            # self.assertEqual(output, 0)
            # output = main('-t')
            # self.assertEqual(output, 0)
            output = main('./testdata/Bookmarks')
            self.assertEqual(output, 0)
        finally:
            sys.argv = __sys_argv

    def test_91_chromium_bookmarks(self):
        cb = ChromiumBookmarks(self.bookmarks_path)
        output = list(cb)
        self.assertTrue(output)
        output = cb.reorganized_by_date()
        self.assertTrue(output)

        output = cb.overwrite(prompt=False)
        self.assertTrue(output)


def get_option_parser():
    import optparse
    prs = optparse.OptionParser(usage="%prog : <-p|-d|-w> [options]")

    prs.add_option('-p', '--print-all',
                   dest='print_all',
                   action='store_true')

    prs.add_option('-d', '--by-date',
                   dest='reorganized_by_date',
                   action='store_true')

    prs.add_option('-w', '--overwrite',
                   dest='overwrite',
                   action='store_true',
                   help="Overwrite Bookmarks in place and rm Bookmarks.bak")
    prs.add_option('--skip-prompt',
                   dest='skip_prompt',
                   action='store_true',
                   help="Skip overwrite prompt")

    prs.add_option('-v', '--verbose',
                   dest='verbose',
                   action='store_true',)
    prs.add_option('-q', '--quiet',
                   dest='quiet',
                   action='store_true',)
    prs.add_option('-t', '--test',
                   dest='run_tests',
                   action='store_true',)
    return prs


def main(*args):
    import logging
    import sys
    import unittest

    prs = get_option_parser()
    args = args and list(args) or sys.argv[1:]
    (opts, args) = prs.parse_args(args)

    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf8')(sys.stderr)

    if not opts.quiet:
        logging.basicConfig()
        if opts.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    if opts.run_tests:
        tp = unittest.main(exit=False, argv=[__file__])
        return not bool(tp.result)

    opts.bookmarks_path = './Bookmarks'
    if len(args):
        opts.bookmarks_path = args[0]

    cb = ChromiumBookmarks(opts.bookmarks_path)

    if opts.print_all:
        for bookmark in cb:
            print(bookmark)
    if opts.reorganized_by_date:
        output = cb.reorganized_by_date()
        print(output)

    if opts.overwrite:
        cb.overwrite(prompt=(not opts.skip_prompt))

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
