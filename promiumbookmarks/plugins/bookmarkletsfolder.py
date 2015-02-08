#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import promiumbookmarks.plugins as plugins

import logging
log = logging.getLogger()


class BookmarkletsFolderPlugin(plugins.PromiumPlugin):

    """
    Add a 'bookmarklets' folder with a default set of bookmarklets
    """

    def process_bookmarks(self, bookmarks_obj):
        bookmarks_dict = bookmarks_obj.bookmarks_dict
        ids = bookmarks_obj.ids

        _bookmarklets_folders = [
            x for x in bookmarks_dict['roots']['bookmark_bar']['children']
            if x and hasattr(x, 'name') and x.get('name') == 'bookmarklets']
        if len(_bookmarklets_folders) > 1:
            log.error("Found %d bookmarklets folders found. "
                      "Taking the first and dropping subsequent folders."
                      % len(_bookmarklets_folders))
            _bookmarklets_folder = _bookmarklets_folders[0]
        elif len(_bookmarklets_folders) == 1:
            _bookmarklets_folder = _bookmarklets_folders[0]
        else:
            _bookmarklets_folder = None

        # merge the 'bookmarklets' folder with the default set
        bookmarks_dict['roots']['bookmark_bar']['children'].append(
            self.build_bookmarklets_folder(
                ids,
                folder=_bookmarklets_folder))

        return bookmarks_obj

    @staticmethod
    def build_bookmarklets_folder(ids, folder=None):
        if folder is None:
            folder = {
                "type": 'folder',
                "id": ids.next(),
                "name": "bookmarklets",
                "date_added": 0,
                "date_modified": 0,
                "children": []}

        default_bookmarklets = [
            {"url":
             'data:text/html, <html style="font-family:Helvetica; background: #333; width: 400px; margin: 0 auto; color: white;" contenteditable><title>todo</title>==================<br>todo<br>==================<br>.',
             "type": 'url',
             "id": ids.next(),
             "name": "notetab",
             "date_added": 0,
             "date_modified": 0, },
            {"url":
             'javascript:function iprl5()%7Bvar d%3Ddocument,z%3Dd.createElement(%27scr%27%2B%27ipt%27),b%3Dd.body,l%3Dd.location%3Btry%7Bif(!b)throw(0)%3Bz.setAttribute(%27src%27,%27https://dabble.me/cast/bookmarklet.js%3F%27%2B(new Date().getTime()))%3Bb.appendChild(z)%3B%7Dcatch(e)%7Balert(%27Please wait until the page has loaded.%27)%3B%7D%7Diprl5()%3Bvoid(0)',
             "type": 'url',
             "id": ids.next(),
             "name": "vidcast",
             "date_added": 0,
             "date_modified": 0},
            {"url":
             'javascript:var i = document.createElement("iframe");i.src = window.location;i.setAttribute("width",window.innerWidth-20);i.setAttribute("height",window.innerHeight-20); i.style.position="fixed"; i.style.top=10; i.style.left=10; document.body.appendChild(i);',
             "type": 'url',
             "id": ids.next(),
             "name": "iframeify",
             "date_added": 0,
             "date_modified": 0},
        ]

        if folder.get('children'):
            keys = dict.fromkeys(
                (url.get('type'), url.get('name'), url.get('url'))
                for url in folder['children'])
            for url in default_bookmarklets:
                key = (url.get('type'), url.get('name'), url.get('url'))
                if key not in keys:
                    folder['children'].append(url)
        else:
            folder['children'] = default_bookmarklets
        return folder
