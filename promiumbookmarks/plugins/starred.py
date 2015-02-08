#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import collections
import urlparse
from promiumbookmarks.promiumbookmarks import Folder
import promiumbookmarks.plugins as plugins

# TODO: Folder, URL, bookmarks_bar structure



class MultiStarredFolder(plugins.PromiumPlugin):

    def process_bookmarks(self, bookmarks_obj):
        """
        add_multiples_to_one_folder
        """
        urls_map = collections.OrderedDict()

        def get_base_url(bookmark):
            url = urlparse.urlparse(bookmark)
            if url.path.endswith('#'):
                return url.with_multi_fragments_replaced()

        for bookmark in bookmarks_obj.bookmarks_list:
            if bookmark['url'].endswith('#'):
                url_key = get_base_url(bookmark['url'])
                urls_map[url_key].append(bookmark)

        def count_hashtags(url):
            if not url:
                return
            count = [c for c in url[::-1] if c == '#']
            return count

        def get_longest(bookmarks):
            n = 0
            current = None
            for b in bookmarks:
                if len(b.url) > n:
                    n = len(b.url)
                    current = b
            return current

        urls = []
        for url_key, bookmarks in urls_map.items():
            longest = get_longest(bookmarks)
            count = count_hashtags(longest)
            urls.append({
                'type': 'url',
                'url': longest.url,
                "title": "(%d) %s [ XSTARS ]" % (count, longest.title),
                "date_added": longest.date_added,  # TODO: shortest.date_added
                "date_modified": longest.date_modified,
            })

        bookmarks_dict = bookmarks_obj.bookmarks_dict.copy()
        bookmarks_dict['bookmarks_bar']['multiples'] = Folder(
            children=urls)
        bookmarks_obj.bookmarks_dict = bookmarks_dict
        return bookmarks_obj
