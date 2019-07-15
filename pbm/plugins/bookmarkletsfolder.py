#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import pbm.plugins
import pbm.utils

import logging
log = logging.getLogger(__name__)


class BookmarkletsFolderPlugin(pbm.plugins.PromiumPlugin):

    """
    Add a 'bookmarklets' folder with a default set of bookmarklets
    """
    folder_name = 'bookmarklets'
    default_bookmarklets = [
        {"url":
            'data:text/html, <html style="font-family:Helvetica; background: #333; width: 400px; margin: 0 auto; color: white;" contenteditable><title>todo</title>==================<br>todo<br>==================<br>.',
            "name": "notetab (400px)"},
        {"url":
            'data:text/html, <html style="font-family:Helvetica; background: #333; width: 800px; margin: 0 auto; color: white;" contenteditable><title>todo</title>==================<br>todo<br>==================<br>.',
            "name": "notetab (800px)"},
        {"url":
            'javascript:function iprl5()%7Bvar d%3Ddocument,z%3Dd.createElement(%27scr%27%2B%27ipt%27),b%3Dd.body,l%3Dd.location%3Btry%7Bif(!b)throw(0)%3Bz.setAttribute(%27src%27,%27https://dabble.me/cast/bookmarklet.js%3F%27%2B(new Date().getTime()))%3Bb.appendChild(z)%3B%7Dcatch(e)%7Balert(%27Please wait until the page has loaded.%27)%3B%7D%7Diprl5()%3Bvoid(0)',
            "name": "vidcast"},
        {"url":
            'javascript:var i = document.createElement("iframe");i.src = window.location;i.setAttribute("width",window.innerWidth-20);i.setAttribute("height",window.innerHeight-20); i.style.position="fixed"; i.style.top=10; i.style.left=10; document.body.appendChild(i);',
            "name": "iframeify" },
    ]

    def preprocess_bookmarks(self, bookmarks_obj):
        return bookmarks_obj.remove_bookmark_bar_folders(self.folder_name)

    def process_bookmarks(self, bookmarks_obj):
        return bookmarks_obj.add_bookmark_bar_folder(
            folder_name=self.folder_name,
            folder_nodes=list(self.build_bookmarklets_nodes(bookmarks_obj.ids)),
            merge_and_update=False)

    def build_bookmarklets_nodes(self, ids):
        date_added = pbm.utils.get_datetime_now_longdate()
        for d in self.default_bookmarklets:
            yield {
                "type": 'url',
                "id": next(ids),
                "name": d['name'],
                "url": d['url'],
                "date_added": date_added,
                "date_modified": date_added }

    def merge_bookmarklets_folder(folder, ):
        if folder.get('children'):
            keys = dict.fromkeys(
                (url.get('type'), url.get('name'), url.get('url'))
                for url in folder['children'])
            for url in default_bookmarklets:
                key = (url.get('type'), url.get('name'), url.get('url'))
                if key not in keys:
                    folder['children'].append(url)
        else:
            folder['children'] = self.default_bookmarklets
        return folder
