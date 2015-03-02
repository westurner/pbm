#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import promiumbookmarks.main as pb
import promiumbookmarks.plugins as plugins

class ChromeFolderPlugin(plugins.PromiumPlugin):
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
        date_added = plugins.get_datetime_current()
        return [({
            "type": 'url',
            "url": url,
            "id": ids.next(),
            "name": url,
            "date_added": date_added,
            "date_modified": date_added,
            }) for url in self.urls]
