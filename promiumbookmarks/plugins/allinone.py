#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import collections
import urlparse
from promiumbookmarks.promiumbookmarks import Folder
import promiumbookmarks.plugins as plugins


class AdditionalAllFolder(plugins.PromiumPlugin):

    def process_bookmarks(self, bookmarks_obj):
        """
        add all (unfiltered) bookmarks to one folder
        """
        bookmarks_dict = bookmarks_obj.bookmarks_dict.copy()
        bookmarks_dict['bookmarks bar']['all'] = Folder(
            children=bookmarks_obj.bookmarks_list)
        bookmarks_obj.bookmarks_dict = bookmarks_dict
        return bookmarks_obj
