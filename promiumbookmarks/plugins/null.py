#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import logging

import promiumbookmarks.plugins as plugins

log = logging.getLogger(__name__)

class NullPlugin(plugins.PromiumPlugin):
    def preprocess_bookmarks(self, bookmarks_obj):
        return bookmarks_obj

    def process_bookmarks(self, bookmarks_obj):
        return bookmarks_obj

    def postprocess_bookmarks(self, bookmarks_obj):
        return bookmarks_obj
