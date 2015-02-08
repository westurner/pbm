#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import promiumbookmarks.plugins as plugins

class NullPlugin(plugins.PromiumPlugin):
    def process_bookmarks(self, bookmarks_obj):
        return bookmarks_obj
