#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
promiumbookmarks -- a tool to read, transform, and write Bookmarks JSON

* Sort all bookmarks into date-based folders in the Bookmarks Bar
* Add a 'Chrome' folder with links to Bookmarks, History, Extensions, Plugins

Usage:

.. code:: bash

    ./promiumbookmarks.py --print-all ./path/to/Bookmarks
    ./promiumbookmarks.py --by-date ./path/to/Bookmarks
    ./promiumbookmarks.py --overwrite ./path/to/Bookmarks

"""

import codecs
import datetime
import glob
import itertools
import json
import logging
import os
import platform as _platform_
import shutil
import sys

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


class PluginManager(object):

    @staticmethod
    def get_plugins():
        """
        mainfunc
        """
        import pkg_resources
        entry_points = pkg_resources.iter_entry_points(
            group='promiumbookmarks_plugins')
        for ep in entry_points:
            yield ep.name, ep.load()

    @staticmethod
    def list_plugins():
        print('installed promiumbookmarks.plugins entry_points\n'
              '-------------------------------------------------')
        plugins = PluginManager.get_plugins()
        for name, cls in plugins:
            print(name, cls)


class ChromiumBookmarks(object):

    skiplist = ['chrome', 'bookmarklets', 'quicklinks']

    def __init__(self, bookmarks_path=None,
                 bookmarks_dict=None,
                 skiplist=None,
                 ids=None,
                 conf=None):
        self.bookmarks_path = bookmarks_path
        if bookmarks_dict is not None:
            self.bookmarks_dict = bookmarks_dict
        else:
            if bookmarks_path:
                self.bookmarks_dict = self.read_bookmarks(self.bookmarks_path)
            else:
                raise Exception("must specify either bookmarks_dict or "
                                "bookmarks_path")

        if 'checksum' in self.bookmarks_dict:
            self.bookmarks_dict.pop('checksum')

        if skiplist is not None:
            self.skiplist = skiplist

        if ids is None:
            ids = self.get_ids()
        self.ids = ids

        if conf is None:
            conf = {}
        self.conf = conf

    def get_ids(self):
        return itertools.count(len(list(self.bookmarks_list)))
        # TODO: bookmarks_list is filtered, iter_bookmarks and __iter__ are not

    @property
    def bookmarks_list(self):
        return ChromiumBookmarks.iter_bookmarks(
            bookmarks_dict=self.bookmarks_dict,
            filterfunc=ChromiumBookmarks.chrome_filterfunc)

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
            namedtuple: Folder or URL namedtuples
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
    def iter_bookmarks(cls, bookmarks_path=None, bookmarks_dict=None,
                       filterfunc=None):
        """
        Args:
            bookmarks_path (path): path to Chromium Bookmarks JSON to read first

        Keyword Arguments:
            bookmarks_dict (dict): an already loaded bookmarks dict
            filterfunc (None, True, callable): default, all, True to include

        Yields:
            iterable: chain(map(cls.walk_bookmarks, ['bookmarks_bar', 'other']))
        """
        if bookmarks_dict is None:
            if bookmarks_path is None:
                raise Exception("must specify either bookmarks_dict "
                                "or bookmarks_list")
            bookmarks_dict = cls.read_bookmarks(bookmarks_path)
        return itertools.chain(
            cls.walk_bookmarks(bookmarks_dict['roots']['bookmark_bar'],
                               filterfunc=filterfunc),
            cls.walk_bookmarks(bookmarks_dict['roots']['other'],
                               filterfunc=filterfunc))

    def __iter__(self):
        """
        Returns:
            iterable: ChromiumBookmarks.iter_bookmarks(**self)
        """
        return self.iter_bookmarks(
            self.bookmarks_path,
            bookmarks_dict=self.bookmarks_dict)

    @property
    def bookmarks_list(self):
        return list(self.iter_bookmarks(
            bookmarks_dict=self.bookmarks_dict,
            filterfunc=ChromiumBookmarks.chrome_filterfunc))

    @staticmethod
    def urlskip(url):
        # strip apps, bookmarklets, and data URIs
        if url.startswith('chrome:'):
            return False
        if url.startswith('javascript:'):
            return False
        if url.startswith('data:'):
            return False
        return True

    @staticmethod
    def folderskip(name, skiplist=None, addl_skiplist=None):
        if skiplist is None:
            skiplist = ChromiumBookmarks.skiplist
        if addl_skiplist:
            skiplist.extend(addl_skiplist)
        if name in skiplist:
            return False
        return True

    @staticmethod
    def chrome_filterfunc(b, skiplist=None, addl_skiplist=None):
        """
        Args:
            b (object): a Folder, Url, or bookmark folder or url dict
        Keyword Arguments:
            skiplist (list): list of folder names to skip
                             (default: None: chrome, bookmarklets, quicklinks)
            addl_skiplist (list): additional list of folder names to skip
                             (skiplist.append(addl_skiplist))
        Returns:
            bool: **False** to exclude this bookmark folder or url
        """
        def lookup(obj, attr, default=None):
            return getattr(obj, attr,
                           hasattr(obj, 'get') and obj.get(attr, default)
                           or default)
        type_ = lookup(b, 'type', '')
        if type_ == 'url':
            url = lookup(b, 'url', '')
            return ChromiumBookmarks.urlskip(url)
        elif type_ == 'folder':
            name = lookup(b, 'name', '')
            return ChromiumBookmarks.folderskip(name)
        else:
            log.debug("Unknown type: %r" % (type_, b))
        return True

    @staticmethod
    def transform_bookmarks_dict(bookmarks_path, conf=None):
        """
        Apply a transformation function to Chromium Bookmarks JSON data.

        Args:
            bookmarks_path (str): path to bookmarks JSON file

        Keyword Arguments:
            func (callable): bookmarks transform func (default: None)

        Returns:
            str: block of indented JSON
        """
        bookmarks_obj = ChromiumBookmarks(
            bookmarks_path=bookmarks_path,
            conf=conf)

        bookmarks_dict = bookmarks_obj.bookmarks_dict

        # get any folders named quicklinks
        _quicklinks = [
            x for x in bookmarks_dict['roots']['bookmark_bar']['children']
            if x and hasattr(x, 'get') and x.get('name') == 'quicklinks']

        import plugins.bookmarkletsfolder as bf
        import plugins.datebasedfolders as dbf
        import plugins.chromefolder as cf

        bookmarks_obj = (
            dbf.DateBasedFoldersPlugin(conf).process_bookmarks(bookmarks_obj))
        bookmarks_obj = (
            bf.BookmarkletsFolderPlugin(conf).process_bookmarks(bookmarks_obj))
        bookmarks_obj = (
            cf.ChromeFolderPlugin(conf).process_bookmarks(bookmarks_obj))

        # if quicklinks folder[s] exist, copy them over
        if _quicklinks:
            bookmarks_dict['roots']['bookmark_bar']['children'].extend(
                _quicklinks)

        # new bookmarks should default to the 'queue' folder
        bookmarks_dict['roots']['bookmark_bar']['children'].append(
            {
                "type": 'folder',
                "id": bookmarks_obj.get_ids().next(),
                "name": "queue",
                "date_added": 0,
                "date_modified": 0,
                "children": []})

        # the 'Other Bookmarks' folder is now empty
        bookmarks_dict['roots']['other']['children'] = []
        return bookmarks_dict

    @staticmethod
    def do_plugins(bookmarks_obj, conf=None):
        """
        Process bookmarks plugins

        Arguments:
            bookmarks_obj (BookmarksObject): bookmarks object to mutate

        Keyword Arguments:
            conf (dict): dictionary of configuration options

        Returns:
            BookmarksObject: mutated bookmarks_obj
        """
        if conf is None:
            conf = dict(load_plugins=True)
        load_plugins = conf.get('load_plugins')
        if load_plugins:
            plugin_classes = [x[1] for x in PluginManager.get_plugins()]
            available_plugins = plugin_classes
            log.debug("available_plugins=%s" % available_plugins)

            if load_plugins is True:
                plugins_to_load = available_plugins
            else:
                plugins_to_load = [
                    x for x in available_plugins if x.__name__ in load_plugins]

            for Plugin in plugins_to_load:
                log.debug("Plugin: %s" % Plugin)
                plugin = Plugin(conf)
                bookmarks_obj = plugin.process_bookmarks(bookmarks_obj)
            return bookmarks_obj
        else:
            raise Exception("conf['load_plugins'] is not True or a list")

    @staticmethod
    def to_json(bookmarks_dict):
        output_json = json.dumps(bookmarks_dict, indent=2)
        assert json.loads(output_json) == bookmarks_dict
        return output_json

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
        bookmarks_dict = self.transform_bookmarks_dict(self.bookmarks_path)
        bookmarks_json = self.to_json(bookmarks_dict)
        return self.overwrite_bookmarks_json(
            bookmarks_json,
            self.bookmarks_path,
            prompt=prompt)


def get_chromedir(platform, release):
    """
    Args:
        platform (str): a sys.platform str

    Returns:
        str: path to Chrome User Data Directory

    http://www.chromium.org/user-experience/user-data-directory
    """
    chromedirs = None
    if platform == 'darwin':
        chromedir = os.path.expanduser(
            '~/Library/Application Support/Google/Chrome')
    elif platform.startswith('linux2'):
        chromedir = os.path.expanduser(
             '~/.config/google-chrome')
        chromedirs = [chromedir,
                      os.path.expanduser('~/.config/google-chrome-unstable')]
    elif platform == 'win32':
        if release == 'XP':
            chromedir = os.path.expanduser(
                '~\Local Settings\Application Data\Google\Chrome\User Data')
        else:
            chromedir = os.path.expanduser(
                '~\AppData\Local\Google\Chrome\User Data')
    else:
        raise NotImplementedError("Unknown platform: %r" % platform)
    if chromedirs:
        return chromedirs
    return [chromedir]


def get_chromiumdir(platform, release):
    """
    Args:
        platform (str): a sys.platform str

    Returns:
        str: path to Chromium User Data Directory

    http://www.chromium.org/user-experience/user-data-directory
    """
    if platform == 'darwin':
        chromedir = os.path.expanduser(
            '~/Library/Application Support/Chromium')
    elif platform.startswith('linux'):
        chromedir = os.path.expanduser(
             '~/.config/chromium')
    elif platform == 'win32':
        if release == 'XP':
            chromedir = os.path.expanduser(
                '~\Local Settings\Application Data\Chromium\User Data')
        else:
            chromedir = os.path.expanduser(
                '~\AppData\Local\Chromium\User Data')
    else:
        raise NotImplementedError("Unknown platform: %r" % platform)
    return [chromedir]


def list_profile_bookmarks(prefix=None,
                           platform=None,
                           release=None,
                           show_backups=False):
    """
    List chromium Bookmark files

    Keyword Arguments:
        platform (str): default: sys.platform
        release (str): default: platform.release()
        show_backups (bool): if True, list 'Bookmarks*' else 'Bookmarks'

    Yields:
        str: Bookmarks path
    """
    if platform is None:
        platform = sys.platform
    if release is None:
        release = _platform_.release()

    if show_backups:
        glob_suffix = '*' + os.path.sep + 'Bookmarks*'
    else:
        glob_suffix = '*' + os.path.sep + 'Bookmarks'

    if prefix in (None, True):
        chromedirs = get_chromedir(platform, release)
        chromiumdirs = get_chromiumdir(platform, release)
        dirs = chromedirs + chromiumdirs
    else:
        dirs = [prefix]
    log.debug("Listing profile Bookmarks in: %r" % dirs)
    for d in dirs:
        _glob_pattern = d + os.path.sep + glob_suffix
        for x in glob.glob(_glob_pattern):
            yield x


def get_option_parser():
    import optparse
    prs = optparse.OptionParser(usage="%prog : [-l|-L] [-p|-d|-w] [options]")

    prs.add_option('-l', '--list-bookmarks',
                   help="List profiles with Bookmarks",
                   dest='list_profile_bookmarks',
                   action='store_true')
    prs.add_option('-L', '--list-bookmarks-backups',
                   help="List profiles with Bookmarks",
                   dest='list_profile_bookmarks_show_backups',
                   action='store_true')

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

    if opts.list_profile_bookmarks:
        for path in list_profile_bookmarks(opts.list_profile_bookmarks):
            print(path)
        return 0

    if opts.list_profile_bookmarks_show_backups:
        for path in list_profile_bookmarks(
                opts.list_profile_bookmarks_show_backups,
                show_backups=True):
            print(path)
        return 0

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
    sys.exit(main())
