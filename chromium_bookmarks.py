#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
chromium_bookmarks -- a tool to read, transform, and write Bookmarks JSON

* Sort all bookmarks into date-based folders in the Bookmarks Bar
* Add a 'Chrome' folder with links to Bookmarks, History, Extensions, Plugins

Usage:

.. code:: bash

    ./chromium_bookmarks.py --print-all ./path/to/Bookmarks
    ./chromium_bookmarks.py --by-date ./path/to/Bookmarks
    ./chromium_bookmarks.py --overwrite ./path/to/Bookmarks

"""

import codecs
import collections
import datetime
import itertools
import json
import logging
import os
import shutil

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
    def walk_bookmarks(node, filterfunc=None):
        """
        Walk a Chromium Bookmarks dict recursively; yielding folders and urls

        Args:
            node (dict): dict to traverse (type:url|folder, children:[]])

        Keyword Arguments:
            filterfunc (None, True, callable): default, all, True to include

        Yields:
            dict: (type: folder || url) dicts
        """
        _type = node.get('type')
        if _type == 'folder':
            if (filterfunc not in (None, True) and filterfunc(node)) or True:
                yield Folder.from_folder_node(node)
                for item in node['children']:
                    if not (item and hasattr(item, 'get') and 'type' in item):
                        continue
                    if filterfunc not in (None, True) and not filterfunc(item):
                        continue
                    _item_type = item.get('type')
                    if _item_type == 'folder':
                        for b in ChromiumBookmarks.walk_bookmarks(item):
                            yield b
                    elif _item_type == 'url':
                        yield URL.from_url_node(item)
        elif _type == 'url':
            yield URL.from_url_node(node)

    @classmethod
    def iter_bookmarks(cls, bookmarks_path, bookmarks_json=None,
                       filterfunc=None):
        """
        Args:
            bookmarks_path (path): path to Chromium Bookmarks JSON to read first

        Keyword Arguments:
            bookmarks_json (dict): an already loaded bookmarks dict
            filterfunc (None, True, callable): default, all, True to include

        Yields:
            iterable: chain(map(cls.walk_bookmarks, ['bookmarks_bar', 'other']))
        """
        if bookmarks_json is None:
            bookmarks_json = cls.read_bookmarks(bookmarks_path)
        return itertools.chain(
            cls.walk_bookmarks(bookmarks_json['roots']['bookmark_bar'],
                               filterfunc=filterfunc),
            cls.walk_bookmarks(bookmarks_json['roots']['other'],
                               filterfunc=filterfunc))

    def __iter__(self):
        """
        Returns:
            iterable: ChromiumBookmarks.iter_bookmarks(**self)
        """
        return ChromiumBookmarks.iter_bookmarks(
            self.bookmarks_path,
            bookmarks_json=self.bookmarks_json)


    @staticmethod
    def chrome_filterfunc(b):
        """
        Args:
            b (object): a Folder, Url, or bookmark folder or url dict
        Returns:
            bool: **False** to exclude this bookmark folder or url
        """
        url = getattr(b, 'url', hasattr(b, 'get') and b.get('url','') or '')
        if url.startswith('chrome://'):
            return False
        if url.startswith('javascript:'):
            return False
        if url.startswith('data:'):
            return False
        name = (getattr(b, 'name', hasattr(b, 'get')
                        and b.get('name', '') or ''))
        if name in ['chrome', 'bookmarklets', 'quicklinks']:
            return False
        return True

    @staticmethod
    def reorganize_by_date(bookmarks, filterfunc=None):
        """
        Reorganize bookmarks into date-based folders

        ::
            2014
                2014-08
                    2014-08-22

        Args:
            bookmarks (iterable{}): iterable of Chromium Bookmarks JSON

        Keyword Arguments:
            filterfunc (None, True, callable): default, all, True to include

        Returns:
            list[dict]: nested JSON-serializable bookmarks folder and url dicts
        """
        id_max = max(int(b.id) for b in bookmarks)
        ids = itertools.count(id_max + 1)

        # by default: include all items
        if filterfunc is True:
            filterfunc = lambda x: True
        elif filterfunc is None:
            filterfunc = ChromiumBookmarks.chrome_filterfunc

        bookmarks_iter = (b for b in bookmarks if filterfunc(b))

        bookmarks_by_day = itertools.groupby(
            sorted(bookmarks_iter, key=lambda x: x.date_added_),
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
            (x,
             list(iterable)) for (
                x,
                iterable) in bookmarks_by_day_month_year]

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
        """
        Apply a transformation function to Chromium Bookmarks JSON data,
        then write out the changes to a new file or the same file,
        prompting before overwriting by default.

        Args:
            bookmarks_path (str): path to bookmarks JSON file

        Keyword Arguments:
            dest (str): path to write bookmarks JSON file to
            prompt (bool): prompt before overwriting bookmarks JSON file
            func (callable): bookmarks transform func (default: None)

        Returns:
            str: block of indented JSON
        """
        bookmarks = list(
            ChromiumBookmarks.iter_bookmarks(
                bookmarks_path,
                filterfunc=ChromiumBookmarks.chrome_filterfunc
        ))

        ids = itertools.count(len(bookmarks))

        output = func(bookmarks)

        bookmarks_json = ChromiumBookmarks.read_bookmarks(bookmarks_path)
        if 'checksum' in bookmarks_json:
            bookmarks_json.pop('checksum')

        _quicklinks = [
            x for x in bookmarks_json['roots']['bookmark_bar']['children']
                if x and hasattr(x, 'get') and x.get('name') == 'quicklinks']

        _bookmarklets_folders = [
            x for x in bookmarks_json['roots']['bookmark_bar']['children']
                if x and hasattr(x, 'name') and x.get('name') == 'bookmarklets']
        if len(_bookmarklets_folders) > 1:
            log.error("Found %d bookmarklets folders found. "
                      "Taking the first and dropping subsequent folders."
                      % len(_bookmarklets_folders))
            _bookmarklets_folder = _bookmarklets_folders[0]
        elif len(_bookmarklets_folders) == 1:
            _bookmarklets_folder = _bookmarklets_folders[0]
        else:
            _bookmarklets_folder = None

        # add the year, year-month, year-month-day date-based folders
        bookmarks_json['roots']['bookmark_bar']['children'] = output

        # merge the 'bookmarklets' folder with the default set
        bookmarks_json['roots']['bookmark_bar']['children'].append(
            ChromiumBookmarks.build_bookmarklets_folder(
                ids,
                folder=_bookmarklets_folder))

        # always overwrite the 'chrome' folder
        bookmarks_json['roots']['bookmark_bar']['children'].append(
            ChromiumBookmarks.build_chrome_folder(ids))

        # if quicklinks folder[s] exist, copy them over
        if _quicklinks:
            bookmarks_json['roots']['bookmark_bar']['children'].extend(
                _quicklinks)

        # new bookmarks should default to the 'queue' folder
        bookmarks_json['roots']['bookmark_bar']['children'].append(
            {
                "type": 'folder',
                "id": ids.next(),
                "name": "queue",
                "date_added": 0,
                "date_modified": 0,
                "children": []})

        # the 'Other Bookmarks' folder is now empty
        bookmarks_json['roots']['other']['children'] = []

        output_json = json.dumps(bookmarks_json, indent=2)
        assert json.loads(output_json) == bookmarks_json
        return output_json

    @staticmethod
    def build_bookmarklets_folder(ids, folder=None):
        if folder is None:
            folder = {
                "type":'folder',
                "id": ids.next(),
                "name": "bookmarklets",
                "date_added": 0,
                "date_modified": 0,
                "children": []}

        default_bookmarklets = [
            {
                "url": 'data:text/html, <html style="font-family:Helvetica; background: #333; width: 400px; margin: 0 auto; color: white;" contenteditable><title>todo</title>==================<br>todo<br>==================<br>.',
                "type": 'url',
                "id": ids.next(),
                "name": "notetab",
                "date_added": 0,
                "date_modified": 0,
            },
            {
                "url": 'javascript:function iprl5()%7Bvar d%3Ddocument,z%3Dd.createElement(%27scr%27%2B%27ipt%27),b%3Dd.body,l%3Dd.location%3Btry%7Bif(!b)throw(0)%3Bz.setAttribute(%27src%27,%27https://dabble.me/cast/bookmarklet.js%3F%27%2B(new Date().getTime()))%3Bb.appendChild(z)%3B%7Dcatch(e)%7Balert(%27Please wait until the page has loaded.%27)%3B%7D%7Diprl5()%3Bvoid(0)',
                "type": 'url',
                "id": ids.next(),
                "name": "vidcast",
                "date_added": 0,
                "date_modified": 0
            },
            {
                "url": 'javascript:var i = document.createElement("iframe");i.src = window.location;i.setAttribute("width",window.innerWidth-20);i.setAttribute("height",window.innerHeight-20); i.style.position="fixed"; i.style.top=10; i.style.left=10; document.body.appendChild(i);',
                "type": 'url',
                "id": ids.next(),
                "name": "iframeify",
                "date_added": 0,
                "date_modified": 0
            }
        ]

        if folder.get('children'):
            keys = dict.fromkeys(
                (url.get('type'), url.get('name'), url.get('url'))
                for url in folder['children'])
            for url in default_bookmarklets:
                key = (url.get('type'), url.get('name'), url.get('url'))
                if key not in keys:
                    folder['children'].append(url)
        else:
            folder['children'] = default_bookmarklets
        return folder


    @staticmethod
    def build_chrome_folder(ids):
        return {
            "type":'folder',
            "id": ids.next(),
            "name": "chrome",
            "date_added": 0,
            "date_modified": 0,
            "children": [
                {
                    "url": "chrome://bookmarks",
                    "type":'url',
                    "id": ids.next(),
                    "name": "chrome://bookmarks",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://history",
                    "type":'url',
                    "id": ids.next(),
                    "name": "chrome://history",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://extensions",
                    "type":'url',
                    "id": ids.next(),
                    "name": "chrome://extensions",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://plugins",
                    "type":'url',
                    "id": ids.next(),
                    "name": "chrome://plugins",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://flags",
                    "type":'url',
                    "id": ids.next(),
                    "name": "chrome://flags",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://settings",
                    "type":'url',
                    "id": ids.next(),
                    "name": "chrome://settings",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://flags",
                    "type":'url',
                    "id": ids.next(),
                    "name": "chrome://flags",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://apps",
                    "type":'url',
                    "id": ids.next(),
                    "name": "chrome://apps",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://downloads",
                    "type":'url',
                    "id": ids.next(),
                    "name": "chrome://downloads",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://chrome",
                    "type":'url',
                    "id": ids.next(),
                    "name": "chrome://chrome",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://chrome-urls",
                    "type":'url',
                    "id": ids.next(),
                    "name": "chrome://chrome-urls",
                    "date_added": 0,
                    "date_modified": 0,
                },
            ],
        }

    @staticmethod
    def overwrite_bookmarks_json(data, bookmarks_path, prompt=True):
        """
        Overwrite Bookmarks JSON file

        Args:
            data (dict): JSON-serializable object(s)
            bookmarks_path (str): path to Bookmarks JSON file to write to

        Keyword Arguments:
            prompt (bool): prompt before overwriting

        Returns:
            bool: True
        """
        if os.path.exists(bookmarks_path):
            log.info("bookmarks_path exists: %r" % bookmarks_path)
            if prompt:
                yesno = raw_input("Overwrite y/[n]: ").lower().strip()
                if yesno not in ("y", "yes"):
                    raise Exception()
                    return False

        bookmarks_bkp_path = "%s.%s.bkp" % (
            bookmarks_path,
            datetime.datetime.now().strftime("%FT%T%z"))
        shutil.copy(bookmarks_path, bookmarks_bkp_path)

        with codecs.open(bookmarks_path, 'w', encoding='utf8') as f:
            f.write(data)

        bkp_file = bookmarks_path + '.bak'
        os.path.exists(bkp_file) and os.remove(bkp_file)
        return True

    def overwrite(self, dest=None, prompt=True):
        """
        Overwrite Bookmarks JSON file

        Args:
            data (dict): JSON-serializable object(s)

        Keyword Arguments:
            dest (str): path to Bookmarks JSON file to write to
                        (default: self.bookmarks_path)
            prompt (bool): prompt before overwriting

        Returns:
            bool: True
        """
        if dest is None:
            dest = self.bookmarks_path
        output = ChromiumBookmarks.rewrite_bookmarks_json(self.bookmarks_path)
        return ChromiumBookmarks.overwrite_bookmarks_json(
            output,
            self.bookmarks_path,
            prompt=prompt)


import unittest


class Test_chromium_bookmarks(unittest.TestCase):

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
            ChromiumBookmarks.walk_bookmarks(
                bookmarks['roots']['bookmark_bar']), ChromiumBookmarks.walk_bookmarks(
                bookmarks['roots']['other']))
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
            output = main('--print-all')
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
