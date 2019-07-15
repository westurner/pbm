#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import pbm.plugins
import pbm.utils

class ChromeFolderPlugin(pbm.plugins.PromiumPlugin):
    folder_name = 'chrome'
    urls = [
        "chrome://bookmarks",
        "chrome://history",
        "chrome://extensions",
        "chrome://plugins",
        "chrome://settings",
        "chrome://flags",
        "chrome://apps",
        "chrome://downloads",
        "chrome://chrome",
        "chrome://chrome-urls",
    ]

    def preprocess_bookmarks(self, bookmarks_obj):
        return bookmarks_obj.remove_bookmark_bar_folders(self.folder_name)

    def postprocess_bookmarks(self, bookmarks_obj):
        # always overwrite the 'chrome' folder
        return bookmarks_obj.add_bookmark_bar_folder(
            folder_name=self.folder_name,
            folder_nodes=self.build_chrome_nodes(bookmarks_obj.ids))

    def build_chrome_nodes(self, ids):
        date_added = pbm.utils.get_datetime_now_longdate()
        return [({
            "type": 'url',
            "url": url,
            "id": next(ids),
            "name": url,
            "date_added": date_added,
            "date_modified": date_added,
            }) for url in self.urls]
