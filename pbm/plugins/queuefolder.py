#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import pbm.plugins

import logging
log = logging.getLogger(__name__)

class QueueFolderPlugin(pbm.plugins.PromiumPlugin):
    folder_name = 'queue'

    def check_node_ids(self, bookmarks_obj):
        nodes = [n for n in
            bookmarks_obj.bookmarks_dict['roots']['bookmark_bar']['children']
            if n.get('name') == self.folder_name]
        # if len(nodes) > 1:
        #    raise Exception(nodes)
        for n in nodes:
            if n.get('children'):
                log.debug(("unprocessed queue", n))
                # raise Exception(n)

    def postprocess_bookmarks(self, bookmarks_obj):
        self.check_node_ids(bookmarks_obj)
        # remove any existing 'queue' folders and bookmarks
        # XXX: this assumes that other plugins have alread re-filed
        bookmarks_obj = bookmarks_obj.remove_bookmark_bar_folders(self.folder_name)
        return bookmarks_obj.add_bookmark_bar_folder(
            folder_name=self.folder_name)

