#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import collections
import logging
import pbm.plugins as plugins

log = logging.getLogger(__name__)


class QuicklinksFolderPlugin(plugins.PromiumPlugin):
    DEFAULT_NODE_PREFIX = 'quicklinks'

    def __init__(self, conf=None, node_prefix=None):
        self.conf = conf if conf else {}
        if node_prefix is None:
            node_prefix = self.DEFAULT_NODE_PREFIX
        self.node_prefix = node_prefix
        self.quicklinks = []

    def preprocess_bookmarks(self, bookmarks_obj):
        quicklinks = self.get_quicklinks(bookmarks_obj=bookmarks_obj)
        log.debug(('quicklinks', quicklinks))
        self.quicklinks = quicklinks
        return bookmarks_obj.remove_bookmark_bar_folders('quicklinks')

    def postprocess_bookmarks(self, bookmarks_obj):
        # extend quicklinks nodes
        bookmarks_obj.bookmarks_dict['roots']['bookmark_bar']['children'].extend(
            self.build_nodes(bookmarks_obj.ids))
        return bookmarks_obj

    def match_prefix(self, name):
        if not name:
            return False
        return name.startswith(self.node_prefix)

    def get_quicklinks(self, nodes=None, node_prefix=None, bookmarks_obj=None):
        if nodes is None:
            nodes = bookmarks_obj.bookmark_bar
        if node_prefix is None:
            node_prefix = self.node_prefix
        node_list = [
            x for x in nodes
            if x and hasattr(x, 'get')
            and self.match_prefix(x.get('name', ''))]
        return node_list

    def build_nodes(self, ids):
        def _build_quicklinks_nodes(ids, nodes, node_prefix):
            datetime_current = plugins.get_datetime_current()
            for node in nodes:
                _type = node.get('type', 'folder')
                _id = ids.next()  # node.get('id')
                _date_added = node.get('date_added', datetime_current)
                _node = collections.OrderedDict((
                    ("type", _type),
                    ("id", _id),
                    ("name", node.get('name', node_prefix)),
                ))
                if _type == 'url':
                    _node['url'] = node.get('url')
                elif _type == 'folder':
                    _node["children"] = node.get('children', [])
                _node["date_added"] = _date_added
                _node["date_modified"] = node.get('date_modified', _date_added)
                yield _node
        return list(
            _build_quicklinks_nodes(ids, self.quicklinks, self.node_prefix))
