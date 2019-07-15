#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import pbm.plugins
import pbm.utils

import logging
log = logging.getLogger(__name__)


class AdditionalAllFolderPlugin(pbm.plugins.PromiumPlugin):
    folder_name__ = 'all'

    def preprocess_bookmarks(self, bookmarks_obj):
        bookmarks_dict = bookmarks_obj.bookmarks_dict

        bookmarks_dict['roots'].setdefault('other', {
            'type': 'folder',
            'id': next(bookmarks_obj.ids),
            'date_added': pbm.utils.get_datetime_now_longdate(),
            'date_modified': pbm.utils.get_datetime_now_longdate(),
            'name': 'Other Bookmarks',
            'children': []})
        nodes = bookmarks_dict['roots']['other']['children']
        nodes = [n for n in nodes if n.get('name') != self.folder_name__]
        bookmarks_dict['roots']['other']['children'] = nodes
        return bookmarks_obj

    def duplicate_list(self, bookmarks_obj):
        for bookmark in bookmarks_obj.bookmarks_list:
            b = bookmark.copy()
            b['id'] = next(bookmarks_obj.ids)
            yield b

    def postprocess_bookmarks(self, bookmarks_obj):
        """
        add all (unfiltered) bookmarks to one folder
        """
        datetime_current = pbm.utils.get_datetime_now_longdate()
        all_folder = (
            {'type': 'folder',
             'id': next(bookmarks_obj.ids),
             'name': 'all',
             'children': list(self.duplicate_list(bookmarks_obj)),
             'date_added': datetime_current,
             'date_modified': datetime_current})
        (bookmarks_obj
         .bookmarks_dict['roots']['other']['children'].append(all_folder))
        return bookmarks_obj
