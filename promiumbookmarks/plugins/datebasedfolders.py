#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

# from promiumbookmarks.promiumbookmarks import PromiumPlugin

import itertools
import promiumbookmarks.promiumbookmarks as pb
import promiumbookmarks.plugins as plugins

class DateBasedFoldersPlugin(plugins.PromiumPlugin):

    def process_bookmarks(self, bookmarks_obj):
        bookmarks = bookmarks_obj.bookmarks_list
        bookmarks_dict = bookmarks_obj.bookmarks_dict
        output = self.reorganize_by_date(bookmarks)

        # add the year, year-month, year-month-day date-based folders
        bookmarks_dict['roots']['bookmark_bar']['children'] = output
        return bookmarks_obj

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
            filterfunc = pb.ChromiumBookmarks.chrome_filterfunc

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
