#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import collections
import logging
import re

import pbm.plugins
import pbm.utils

# TODO: Folder, URL, bookmarks_bar structure

URL_STAR_REGEX = re.compile(r'(.*?)([\#]*)$')

log = logging.getLogger(__name__)


def count_stars(chars):
    """
    Count the number of trailing '#' (~== '#+$')

    >>> count_stars("http://example.org/p?q#fragment####")
    <<< 4
    """
    count = 0
    for c in chars[::-1]:
        if c != '#':
            break
        count += 1
    return count


def split_starcount_fragment(urlstr):
    """
    Count the number of trailing '#' (~== '#+$')

    >>> count_stars("http://example.org/p?q#fragment####")
    <<< 4
    """
    base_url = urlstr
    starstr = None
    starcount = 0
    if urlstr:
        rgxm = URL_STAR_REGEX.match(urlstr)
        if rgxm:
            base_url, starstr = rgxm.groups()
            starcount = len(starstr)
    return base_url, starstr, starcount


class StarredFolderPlugin(pbm.plugins.PromiumPlugin):
    STARRED_FOLDER_TITLE = 'starred'
    folder_name = 'starred'

    def preprocess_bookmarks(self, bookmarks_obj):
        """
        Remove the 'starred' folder
        """
        return bookmarks_obj.remove_bookmark_bar_folders(self.folder_name)

    def postprocess_bookmarks(self, bookmarks_obj):
        """
        Collect bookmarks ending with one or more ``#`` characters
        into a 'starred' folder.

        # example: http://example.org/path?query#fragment[#*]
        """
        starred_folder_node = self.build_bookmarks_json(bookmarks_obj)
        return bookmarks_obj.add_bookmark_bar_folder(
            folder_name=self.folder_name,
            folder=starred_folder_node)

    @staticmethod
    def build_base_url_map(bookmarks_list):
        base_url_map = collections.OrderedDict()
        for bookmark in bookmarks_list:
            if 'url' in bookmark:
                base_url, starstr, starcount = split_starcount_fragment(
                    bookmark.get('url'))
                if starcount:
                    bookmark_dict = bookmark.copy()
                    bookmark_dict['base_url'] = base_url
                    bookmark_dict['starcount'] = starcount
                    base_url_map.setdefault(base_url, [])
                    base_url_map[base_url].append(bookmark_dict)
        return base_url_map

    @staticmethod
    def get_starred_bookmark(bookmarks_list):
        starcount_max = None
        starcount_max_bookmark = None
        # earliest_date_added = None
        # earliest = None
        latest_date_added = 0
        latest = None
        for b in bookmarks_list:
            (base_url, starstr, starcount) = (
                split_starcount_fragment(b.get('url')))
            if starcount_max is not None:
                if starcount > starcount_max:
                    starcount_max_bookmark = b
                    starcount_max = starcount
            else:
                starcount_max_bookmark = b
                starcount_max = starcount
            date_added = b.get('date_added')
            if date_added:
                date_added = int(date_added)
#                   if earliest_date_added:
#                       if date_added < earliest_date_added:
#                           earliest_date_added = date_added
#                           earliest = b
#                   else:
#                       earliest_date_added = date_added
#                       earliest = b
                if latest_date_added:
                    if date_added > latest_date_added:
                        latest_date_added = date_added
                        latest = b
                else:
                    latest_date_added = date_added
                    latest = b
            else:
                log.debug('date_added: 0')

        output = collections.OrderedDict()
        output['type'] = 'url'
        output['starcount'] = starcount_max
        output['url'] = starcount_max_bookmark.get('url')
        bookmark_name = starcount_max_bookmark.get('name')
        if starcount_max:
            bookmark_name = (
                "[X%s] %s" % (
                    starcount * 'O',
                    bookmark_name))
        output['name'] = bookmark_name
        output['date_added'] = latest_date_added
        output['date_modified'] = latest.get('date_modified')
        # starcount
        # starcount_max_bookmark,
        # earliest_date_added,
        # earliest
        # latest_date_added,
        # latest,
        return output

    @classmethod
    def build_bookmarks_json(cls, bookmarks_obj):
        base_url_map = cls.build_base_url_map(bookmarks_obj.bookmarks_list)
        bookmarks_urls = []
        latest_date_added = None
        latest = None
        for base_url, bookmarks_list in base_url_map.items():
            bookmark_dict = cls.get_starred_bookmark(bookmarks_list)
            bookmark_dict['id'] = bookmarks_obj.ids.next()
            bookmarks_urls.append(bookmark_dict)

            date_added = bookmark_dict.get('date_added')
            if latest_date_added:
                if date_added and date_added > latest_date_added:
                    latest_date_added = date_added
                    latest = bookmark_dict
            else:
                latest_date_added = date_added
                latest = bookmark_dict
        output = {
            'type': 'folder',
            'name': 'starred',
            'date_added': latest_date_added,
            'date_modified': latest.get('date_modified') if latest else None,
            'children': bookmarks_urls[::-1],  # show latest (in sequence) first
            'id': bookmarks_obj.ids.next(),
        }
        return output
