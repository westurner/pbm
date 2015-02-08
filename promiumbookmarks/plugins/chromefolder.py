#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import promiumbookmarks.plugins as plugins

class ChromeFolderPlugin(plugins.PromiumPlugin):
    def process_bookmarks(self, bookmarks_obj):
        bookmarks_dict = bookmarks_obj.bookmarks_dict
        ids = bookmarks_obj.ids

        # always overwrite the 'chrome' folder
        bookmarks_dict['roots']['bookmark_bar']['children'].append(
            self.build_chrome_folder(ids))

        return bookmarks_obj

    @staticmethod
    def build_chrome_folder(ids):
        return {
            "type": 'folder',
            "id": ids.next(),
            "name": "chrome",
            "date_added": 0,
            "date_modified": 0,
            "children": [
                {
                    "url": "chrome://bookmarks",
                    "type": 'url',
                    "id": ids.next(),
                    "name": "chrome://bookmarks",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://history",
                    "type": 'url',
                    "id": ids.next(),
                    "name": "chrome://history",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://extensions",
                    "type": 'url',
                    "id": ids.next(),
                    "name": "chrome://extensions",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://plugins",
                    "type": 'url',
                    "id": ids.next(),
                    "name": "chrome://plugins",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://flags",
                    "type": 'url',
                    "id": ids.next(),
                    "name": "chrome://flags",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://settings",
                    "type": 'url',
                    "id": ids.next(),
                    "name": "chrome://settings",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://flags",
                    "type": 'url',
                    "id": ids.next(),
                    "name": "chrome://flags",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://apps",
                    "type": 'url',
                    "id": ids.next(),
                    "name": "chrome://apps",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://downloads",
                    "type": 'url',
                    "id": ids.next(),
                    "name": "chrome://downloads",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://chrome",
                    "type": 'url',
                    "id": ids.next(),
                    "name": "chrome://chrome",
                    "date_added": 0,
                    "date_modified": 0,
                },
                {
                    "url": "chrome://chrome-urls",
                    "type": 'url',
                    "id": ids.next(),
                    "name": "chrome://chrome-urls",
                    "date_added": 0,
                    "date_modified": 0,
                },
            ],
        }
