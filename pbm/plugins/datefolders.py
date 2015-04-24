#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

# from pbm.pbm import PromiumPlugin

import collections
import datetime
import itertools
import logging

import pbm.main
import pbm.plugins
import pbm.utils

log = logging.getLogger(__name__)


class DateBasedFoldersPlugin(pbm.plugins.PromiumPlugin):

    """
    Organize bookmarks into year, year-month, year-month-day date-based folders

    ::
        2014
            2014-08
                2014-08-22

    .. note:: This plugin should be called first, as it overwrites
        bookmark_bar
    """

    def process_bookmarks(self, bookmarks_obj):
        # log.debug(('dbmarksobj',
        #  bookmarks_obj.bookmarks_dict, bookmarks_obj.bookmarks_list))
        datefolder_nodes = self.reorganize_by_date(bookmarks_obj)
        bookmark_bar = (
            bookmarks_obj.bookmarks_dict['roots']['bookmark_bar']['children'])
        existing_folders = collections.OrderedDict(
            (x.get('name'), x) for x in bookmark_bar)
        prev_n = None
        for node in datefolder_nodes:
            if node.get('type') == 'folder':
                new_name = node.get('name')
                existing = existing_folders.get(new_name)
                if existing:
                    n = bookmark_bar.index(existing)
                    bookmark_bar[n] = node
                    prev_n = n
                else:
                    n = prev_n + 1 if prev_n else 0
                    bookmark_bar.insert(n, node)
            # log.debug(('DATEFOLDER node', n, node))
        # log.debug(('datefolder_nodes', datefolder_nodes))
        return bookmarks_obj

    @staticmethod
    def reorganize_by_date(bookmarks_obj, filterfunc=None):
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
        # by default: include all items
        if filterfunc is True:
            def filterfunc(x):
                True
        elif filterfunc is None:
            filterfunc = pbm.main.ChromiumBookmarks.chrome_filterfunc

        # id_max = max(int(b.get('id')) for b in bookmarks)
        # ids = itertools.count(id_max + 1)
        ids = bookmarks_obj.ids

        bookmarks_iter_filtered = (
            pbm.main.URL.from_dict(b) for b in
            bookmarks_obj.bookmarks_list
            if filterfunc(b))

        def longdate_ymd_key(x):
            log.debug(('longdate_', x.date_added_))
            return (x.date_added_.year,
                    x.date_added_.month,
                    x.date_added_.day)

        bookmarks_list = sorted(bookmarks_iter_filtered,
                                key=lambda x: x.date_added_)
        log.info(('bookmarks_list_abc', bookmarks_list))
        if not bookmarks_list:
            return []

        bookmarks_by_day = itertools.groupby(
            bookmarks_list,
            lambda x: longdate_ymd_key(x))

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

        nodes = []
        for year, by_year in bookmarks_by_day_month_year:
            _date = pbm.utils.datetime_to_longdate(
                datetime.datetime(int(year), 1, 1))
            year_folder = {
                "type": "folder",
                "id": ids.next(),
                "name": str(year),
                "children": [],
                "date_added": _date,
                "date_modified": _date,
            }
            for month, by_day in by_year:
                _date = pbm.utils.datetime_to_longdate(
                    datetime.datetime(int(year), int(month[-1]), 1))
                month_folder = {
                    "type": "folder",
                    "id": ids.next(),
                    "name": '-'.join(str(s) for s in month),
                    "children": [],
                    "date_added": _date,
                    "date_modified": _date,
                }
                for day, iterable in by_day:
                    _date = pbm.utils.datetime_to_longdate(
                        datetime.datetime(int(year), int(month[-1]), int(day[-1])))
                    day_folder = {
                        "type": "folder",
                        "id": ids.next(),
                        "name": '-'.join(str(s) for s in day),
                        "children": [],
                        "date_added": _date,
                        "date_modified": _date,
                    }
                    for b in iterable:
                        if b.type == 'url':
                            day_folder['children'].append(b.to_json())
                    month_folder['children'].append(day_folder)
                year_folder['children'].append(month_folder)
            nodes.append(year_folder)
        log.debug(('date_nodes', nodes))
        return nodes
