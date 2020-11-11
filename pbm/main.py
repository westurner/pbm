#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
pbm -- a tool to read, transform, and write Bookmarks JSON

* Sort all bookmarks into date-based folders in the Bookmarks Bar
* Add a 'Chrome' folder with links to Bookmarks, History, Extensions, Plugins

Usage:

.. code:: bash

    pbm --print-all ./path/to/Bookmarks
    pbm --by-date ./path/to/Bookmarks
    pbm --organize ./path/to/Bookmarks

"""

import collections
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

if sys.version_info.major > 2:
    unicode = str

import pbm.app
import pbm.utils as utils
import pbm.plugins as plugins



#logging.basicConfig(format="# %(levelname)s [%(name)s] %(message)s")
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class URL(
    namedtuple('URL', (
        'type',
        'id',
        'name',
        'url',
        'path',
        'date_added', 'date_added_',
        'date_modified', 'date_modified_'))):

    def get(self, attr, default=None):
        return getattr(self, attr, default)

    def to_json(self):
        x = self._asdict()
        x.pop('date_added_')
        x.pop('date_modified_')
        return x

    def to_csv_row(self):
        x = self._asdict()
        x.pop('date_added_')
        x.pop('date_modified_')
        return tuple(
            (x.replace('"', '\"') if hasattr(x, 'replace') else x)
            for x in x.values())


    @classmethod
    def from_dict(cls, node, **kwargs):
        return cls(
            type=node.get('type'),
            id=node.get('id'),
            name=node.get('name'),
            url=node.get('url'),
            path=kwargs.get('path', node.get('path')),
            date_added=node.get('date_added'),
            date_added_=utils.longdate_to_datetime(
                node.get('date_added')),
            date_modified=node.get('date_modified'),
            date_modified_=utils.longdate_to_datetime(
                node.get('date_modified'))
        )

    CONSOLE_FIELDS = [
        'type',
        'id',
        'name',
        'url',
        'path',
        'date_added_',
        'date_modified_'
    ]

    def _to_console_strs(self):
        for x in ['id']:
            yield u'# %-5s: %s' % (x, getattr(self, x))
        for attrlabel, x in [
                ('ctime', 'date_added_'),
                ('mtime', 'date_modified_')]:
            value = getattr(self, x)
            if value:
                yield u'# %-5s: %s' % (attrlabel, value.isoformat())
        for x in ['path', 'name']:
            value = getattr(self, x)
            if value:
                yield u'# %-5s: %s' % (x, value)
        yield unicode(self.url)

    def to_console_str(self):
        return u'\n'.join(self._to_console_strs())


class Folder(
    namedtuple('Folder', (
        'type',
        'id',
        'name',
        'path',
        'children',
        'date_added', 'date_added_',
        'date_modified', 'date_modified_'))):

    def get(self, attr, default=None):
        return getattr(self, attr, default)

    @classmethod
    def from_dict(cls, node, **kwargs):
        return cls(
            type=node.get('type'),
            id=node.get('id'),
            name=node.get('name'),
            path=kwargs.get('path', node.get('path')),
            children=node.get('children', []),
            date_added=node.get('date_added'),
            date_added_=utils.longdate_to_datetime(
                node.get('date_added')),
            date_modified=node.get('date_modified'),
            date_modified_=utils.longdate_to_datetime(
                node.get('date_modified')))

    def to_json(self):
        def default(o):
            if isinstance(o, URL):
                return o.to_json()
            elif isinstance(o, Folder):
                return o.to_json()
            else:
                return o
        log.debug(self.json.dumps(self, default=default, indent=2))


class PluginManager(object):

    @staticmethod
    def get_plugins():
        """
        mainfunc
        """
        import pkg_resources
        entry_points = pkg_resources.iter_entry_points(
            group='pbm_plugins')
        for ep in entry_points:
            yield ep.name, ep.load()

    @staticmethod
    def list_plugins():
        print('installed pbm.plugins entry_points\n'
              '-------------------------------------------------')
        _plugins = PluginManager.get_plugins()
        for name, cls in _plugins:
            print(name, cls)


class ChromiumBookmarks(object):

    skiplist = ['chrome', 'bookmarklets', 'quicklinks', 'starred']

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

        if skiplist is None:
            skiplist = self.skiplist
        self.skiplist = skiplist

        if ids is None:
            ids = self.get_ids()
        self.ids = ids

        if conf is None:
            conf = {}
        self.conf = conf

    def get_ids(self, bookmarks_list=None):
        if bookmarks_list is None:
            bookmarks_list = self.bookmarks_list
        bookmarks_list = list(bookmarks_list)
        id_max_len = len(bookmarks_list)
        start_at = 1
        if id_max_len:
            id_max = max(int(b.get('id', 0)) for b in bookmarks_list)
            if id_max > start_at:
                start_at = id_max + 1

        log.debug('start_at: %r', start_at)
        return itertools.count(start_at)
        # TODO: bookmarks_list is filtered, iter_bookmarks and __iter__ are not
        # TODO: find

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
            filterfunc=self.chrome_filterfunc))

    @staticmethod
    def read_bookmarks(path):
        with codecs.open(path, encoding='utf-8') as f:
            return json.load(f, object_pairs_hook=collections.OrderedDict)

    @staticmethod
    def print_bookmarks(bookmarks):
        for x in bookmarks:
            print(x)

        for x in bookmarks['roots']:
            print(x)
            # synced, bookmark_bar, other

        for x in bookmarks['roots']['bookmark_bar']:
            print(x)

        return True

    @property
    def bookmark_bar(self):
        return self.bookmarks_dict['roots']['bookmark_bar']['children']

    @bookmark_bar.setter
    def bookmark_bar(self, nodes):
        self.bookmarks_dict['roots']['bookmark_bar']['children'] = nodes

    def add_bookmark_bar_folder(
            self,
            folder_name=None,
            folder_nodes=None,
            folder=None,
            merge_and_update=False,
            location=None):
        bookmarks_obj = self
        date_added = pbm.utils.get_datetime_now_longdate()
        log.debug('add folder: %r', folder_name)
        id_ = next(bookmarks_obj.ids)
        log.debug('id: %r', id_)
        default_folder = collections.OrderedDict((
            ("type", 'folder'),
            ("id", id_),
            ("name", folder_name),
            ("date_added", date_added),
            ("date_modified", date_added),
            ("children", folder_nodes or [])
        ))
        if folder is None:
            folder = default_folder
        nodes = self.bookmark_bar
        if merge_and_update is False:
            if location is None:
                nodes.append(folder)
            else:
                nodes.insert(location, folder)
        elif merge_and_update:
            bookmarks_obj = self.remove_bookmark_bar_folders(folder_name)
            existing_folder_list = self.folders_before + [folder]
            folder_node = None

            if existing_folder_list == [folder]:
                folder_node = folder
            else:
                # merge all existing folders to min('date_added')
                all_folder_name_nodes = []
                min_attr = None
                min_attrname = 'date_added'
                min_attrcoalesce = float
                folder_node = None
                for node in existing_folder_list:
                    if node.get('type') != 'folder':
                        continue
                    _nodes = node.get('children')
                    if _nodes:
                        all_folder_name_nodes.extend(_nodes)
                        # TODO: recursive merge

                    _min_attr = node.get(min_attrname)
                    __min_attr = min_attrcoalesce(_min_attr)
                    if __min_attr:
                        if ((min_attr is None) or (__min_attr < min_attr)):
                            min_attr = __min_attr
                            folder_node = node
                folder_node['children'] = all_folder_name_nodes

            # Add the node to the folder
            if folder_node:
                if location is None:
                    nodes.append(folder_node)
                else:
                    nodes.insert(location, folder_node)
            else:
                raise Exception(('folder_node', folder_node))
        self.bookmark_bar = nodes
        return bookmarks_obj

    def walkpath(root, node, folder=None, path=None, depth=0):
        """
        DFS walk node and leaves, yielding nested Folder and URL objects

        Arguments:
            node (dict): .type, .name, .children[]

        Keyword Arguments:
            folder (str or None): current folder key
            path (list[str]): current traversal path
            depth (int): current traversal depth

        Yields:
            {Folder, URL}
        """

        if path is None:
            path = []
        if folder:
            path = path + [folder]
        if node.get('type') == 'folder':
            _path = path + [node]
            _node_children = []
            for x in node.get('children', []):
                if x.get('type') == 'url':
                    _node_children.append(URL.from_dict(x, path=path))
                elif x.get('type') == 'folder':
                    _path = path + [node]
                    _x_children = []
                    for subnode in x.get('children', []):
                        for recursed in ChromiumBookmarks.walkpath(
                                root,
                                subnode,
                                folder=x,
                                path=_path,
                                depth=depth + 1):
                            _x_children.append(recursed)  # yield recursed
                    x['children'] = _x_children
                    _node_children.append(Folder.from_dict(x, path=path))
            node['children'] = _node_children
            yield Folder.from_dict(node)
        elif node.get('type') == 'url':
            yield URL.from_dict(node, path=path)

    def remove_bookmark_bar_folders(self, folder_name):
        """

        Arguments:
            folder_name (str): folder key

        Returns:
            ChromiumBookmarks: (self)
        """
        bookmarks_obj = self
        nodes = self.bookmark_bar
        self.folders_before = [
            x for x in nodes
            if x and x.get('name') == folder_name]
        nodes = [x for x in nodes
                 if x and x.get('name') != folder_name]
        self.bookmark_bar = nodes
        return bookmarks_obj

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
                # yield Folder.from_dict(node)
                for item in node.get('children', []) or []:
                    if not (item and hasattr(item, 'get') and 'type' in item):
                        continue
                    if filterfunc not in (None, True) and not filterfunc(item):
                        continue
                    _item_type = item.get('type')
                    if _item_type == 'folder':
                        for b in ChromiumBookmarks.walk_bookmarks(
                                item, filterfunc=filterfunc):
                            yield b
                    elif _item_type == 'url':
                        yield URL.from_dict(item).to_json()
        elif _type == 'url':
            yield URL.from_dict(node).to_json()

    @classmethod
    def iter_bookmarks(
            cls,
            bookmarks_path=None,
            bookmarks_dict=None,
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
    def transform_bookmarks_dict(bookmarks_obj=None,
                                 bookmarks_path=None,
                                 conf=None,
                                 pluginstrs=None):
        """
        Apply a transformation function to Chromium Bookmarks JSON data.

        Keyword Arguments:
            bookmarks_obj (ChromiumBookmarks): bookmarks_obj ('.bookmarks_dict')
            bookmarks_path (str): path to bookmarks JSON file
            conf (dict): config dict (default:None)
            pluginstrs (list(str)): list of pluginstrs (default: None)

        Returns:
            str: block of indented JSON
        """
        if bookmarks_path is not None:
            bookmarks_obj = ChromiumBookmarks(
                bookmarks_path=bookmarks_path,
                conf=conf)
        elif bookmarks_obj is not None:
            bookmarks_obj = bookmarks_obj
        else:
            raise Exception("Must specify bookmarks_obj or bookmarks_path")

        pluginseq = plugins.PluginSequence(pluginstrs=pluginstrs)
        bookmarks_obj = pluginseq.run(bookmarks_obj)
        assert bookmarks_obj
        # log.debug(('bookmarks_obj',
        #           bookmarks_obj,
        #           bookmarks_obj.bookmarks_dict))

        # the 'Other Bookmarks' folder should be processed
        # so set it to empty
        bookmarks_dict = bookmarks_obj.bookmarks_dict
        bookmarks_dict['roots']['other']['children'] = []
        return bookmarks_dict

    @staticmethod
    def _json_default(o):
        if 0:
            return o
        elif isinstance(o, datetime.datetime):
            return o.isoformat()
        elif isinstance(o, URL):
            return o.to_json()
        elif isinstance(o, Folder):
            return o.to_json()
        return None

    @staticmethod
    def _to_json(bookmarks_dict):
        output_json = json.dumps(bookmarks_dict,
                                 default=ChromiumBookmarks._json_default,
                                 indent=2)
        assert json.loads(output_json) == bookmarks_dict
        return output_json

    def to_json(self):
        return self._to_json(self.bookmarks_dict)

    @staticmethod
    def organize_bookmarks_json(data, bookmarks_path, prompt=True):
        """
        Overwrite Bookmarks JSON file, prompt by default, and store a backup

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

        if os.path.exists(bookmarks_path):
            shutil.copy(bookmarks_path, bookmarks_bkp_path)

        with codecs.open(bookmarks_path, 'w', encoding='utf8') as f:
            f.write(data)

        bkp_file = bookmarks_path + '.bak'
        os.path.exists(bkp_file) and os.remove(bkp_file)
        return True

    def organize(self, dest=None, prompt=True):
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
        bookmarks_dict = self.transform_bookmarks_dict(
            bookmarks_obj=self,
            # bookmarks_path=self.bookmarks_path,
            conf=self.conf)
        bookmarks_json = self._to_json(bookmarks_dict)
        return self.organize_bookmarks_json(
            bookmarks_json,
            dest,
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
    elif platform.startswith('linux'):
        chromedir = os.path.expanduser(
            '~/.config/google-chrome')
        chromedirs = [chromedir,
                      os.path.expanduser('~/.config/google-chrome-unstable')]
    elif platform == 'win32':
        if release == 'XP':
            chromedir = os.path.expanduser(
                r'~\Local Settings\Application Data\Google\Chrome\User Data')
        else:
            chromedir = os.path.expanduser(
                r'~\AppData\Local\Google\Chrome\User Data')
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
                r'~\Local Settings\Application Data\Chromium\User Data')
        else:
            chromedir = os.path.expanduser(
                r'~\AppData\Local\Chromium\User Data')
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
    prs.add_option('--print-csv',
                   dest='print_csv',
                   action='store_true')

    prs.add_option('--print-json-link-list',
                   dest='print_json_link_list',
                   action='store_true')

    prs.add_option('--print-html', '--print-html-tree', '--html',
                   dest='print_html_tree',
                   action='store_true')

    prs.add_option('--print-html-link-list',
                   dest='print_html_link_list',
                   action='store_true')

    prs.add_option('-d', '--by-date', '--print-all-by-date',
                   dest='sort_by_date',
                   help='Sort by date_modified or date_added',
                   action='store_true')

    prs.add_option('-r', '--reverse',
                   dest='sort_reverse',
                   help='Reverse the sort order',
                   action='store_true',
                   default=False)

    prs.add_option('-w', '--organize', '--overwrite',
                   dest='organize',
                   action='store_true',
                   help="Organize Bookmarks")
    prs.add_option('-y', '--yes', '--skip-prompt',
                   dest='skip_prompt',
                   action='store_true',
                   help="Skip organize prompt")

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


def main(argv=None,
         stdout=None,
         stderr=None):
    import logging
    import sys
    import unittest

    prs = get_option_parser()
    args = argv and list(argv) or sys.argv[1:]
    (opts, args) = prs.parse_args(args)

    if sys.version_info.major < 3:
        if stdout is None:
            stdout = codecs.getwriter('utf8')(sys.stdout)
        if stderr is None:
            stderr = codecs.getwriter('utf8')(sys.stderr)

    if not opts.quiet:
        logging.basicConfig()
        if opts.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    if opts.run_tests:
        tp = unittest.main(exit=False, argv=[__file__])
        return not bool(tp.result)

    if opts.list_profile_bookmarks:
        for path in list_profile_bookmarks(opts.list_profile_bookmarks):
            print(path, file=stdout)
        return 0

    if opts.list_profile_bookmarks_show_backups:
        for path in list_profile_bookmarks(
                opts.list_profile_bookmarks_show_backups,
                show_backups=True):
            print(path, file=stdout)
        return 0

    opts.bookmarks_path = 'Bookmarks'
    if len(args):
        opts.bookmarks_path = args[0]

    cb = ChromiumBookmarks(opts.bookmarks_path)

    if (opts.print_all
            or opts.print_json_link_list
            or opts.print_html_tree
            or opts.print_csv):
        if opts.sort_by_date:
            sorted_bookmarks = sorted(
                cb,
                key=lambda x: (
                    x.get('date_modified', 0)
                    or x.get('date_added', 0)),
                reverse=opts.sort_reverse)
            bookmarks_iter = sorted_bookmarks
        else:
            bookmarks_iter = cb

        if opts.print_all:
            for bookmark in bookmarks_iter:
                url = URL.from_dict(bookmark)
                print(unicode(url.to_console_str()), file=stdout)
                print("# --------------------", file=stdout)

        elif opts.print_json_link_list:
            bookmark_urls = [b.get('url') for b in bookmarks_iter
                             if b.get('name', '').startswith('[XO')]
            print(json.dumps(bookmark_urls, indent=2), file=stdout)
        if opts.print_html_link_list or opts.print_html_tree:
            if opts.print_html_link_list:
                template_name = 'bookmarks_list_partial.jinja'
            elif opts.print_html_tree:
                template_name = 'bookmarks_tree_partial.jinja'

            t = utils.get_template(template_name)
            htmlstr = t.render({
                'bookmarks': cb,
                'bookmarks_iter': iter(cb),
                'format_longdate': pbm.app.format_longdate,
                'rdf_uri_escape': pbm.app.rdf_uri_escape})
            print(htmlstr, file=stdout)

        if opts.print_csv:
            for bookmark in bookmarks_iter:
                url = URL.from_dict(bookmark)
                print(url.to_csv_row())

    if opts.organize:
        cb.organize(prompt=(not opts.skip_prompt))

    return 0


if __name__ == "__main__":
    sys.exit(main(argv=sys.argv[1:]))
