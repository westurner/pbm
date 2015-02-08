#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

class PromiumPlugin(object):
    def __init__(self, conf=None):
        if conf is None:
            conf = {}
        self.conf = conf

    def process_bookmarks(self, bookmarks_obj):
        return bookmarks_obj


