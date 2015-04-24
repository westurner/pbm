#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import collections
import datetime
import importlib
import inspect
import logging


import pbm.utils as utils
iteritems = utils.iteritems

log = logging.getLogger(__name__)


class PromiumPlugin(object):

    PLUGIN_FUNCS = [
        'preprocess_bookmarks',
        'process_bookmarks',
        'postprocess_bookmarks'
    ]

    def __init__(self, conf=None):
        if conf is None:
            conf = {}
        self.conf = conf

    def preprocess_bookmarks(self, bookmarks_obj):
        return bookmarks_obj

    def process_bookmarks(self, bookmarks_obj):
        return bookmarks_obj

    def postprocess_bookmarks(self, bookmarks_obj):
        return bookmarks_obj


TRACE = logging.DEBUG + 1
logging.addLevelName('TRACE', TRACE)


class PluginSequence(object):
    DEFAULT_PLUGINS = [
        'null',
        'bookmarkletsfolder',
        'chromefolder',
        'datefolders',
        'dedupe',
        'quicklinks',
        'starred',
        'allinone',
        'queuefolder',
    ]

    PLUGIN_FUNCS = PromiumPlugin.PLUGIN_FUNCS

    def __init__(self, pluginstrs=None, conf=None):
        if conf is None:
            conf = {}
        self.conf = conf
        self.pluginstrs = pluginstrs
        self.plugins = None
        if pluginstrs is not None:
            self.plugins = self.load_plugins(pluginstrs=pluginstrs)


    @classmethod
    def load_module(cls, pluginstr,
                    default_modprefix='pbm.plugins',
                    default_modname='pbm'):
        if '.' not in pluginstr:
            pluginmodstr = '%s.%s' % (default_modprefix, pluginstr)
            modname = default_modname
        else:
            pluginmodstr = pluginstr  # XXX: allow dotted names
            modname = pluginstr.split('.', 1)[0]
        _module = importlib.import_module(pluginmodstr, modname)
        #log.log(TRACE, ('load_module',
                        #pluginmodstr,
                        #_module.__name__,
                        #_module.__file__))
        return _module

    @classmethod
    def load_plugins(cls, pluginstrs=None):
        if pluginstrs is None:
            pluginstrs = cls.DEFAULT_PLUGINS
        plugins_dict = collections.OrderedDict()
        for pluginstr in pluginstrs:
            _module = cls.load_module(pluginstr)
            # _module = cls.load_plugins_from_module(pluginstr)

            # load all PromiumPlugin that end with 'Plugin'
            for key in dir(_module):
                if key.endswith('Plugin'):
                    Plugin = getattr(_module, key)
                    # if not isinstance(Plugin, PromiumPlugin):
                    #     continue
                    pluginclsstr = "%s.%s" % (_module.__name__, Plugin.__name__)
                    # log.debug(('load_plugin', pluginclsstr, _module.__name__))
                    plugins_dict[pluginclsstr] = Plugin
                    # else:
                    #    print(("DIR", dir(mod)))
        plugins = plugins_dict.values()
        log.info(('plugin_modules', plugins))
        return plugins

    @classmethod
    def load_plugins_from_module(cls, pluginstr):
        return cls.load_plugins([pluginstr])


    def run(self, bookmarks_obj, plugins_list=None, pluginstrs=None):
        """
        run bookmarks_obj through a series of plugins

        Args:
            bookmarks_obj (ChromiumBookmarks): bookmarks object
        Keyword Arguments:
            plugins_list (list): list of plugin classes
            pluginstrs (list[str]): list of module names
                                    which contain a ``*Plugin``
        Returns:
            ChromiumBookmarks: transformed bookmarks_obj
        """

        assert bookmarks_obj

        if plugins_list is None:
            if pluginstrs is None:
                pluginstrs = self.DEFAULT_PLUGINS
                plugins_list = self.load_plugins(pluginstrs)
            else:
                plugins_list = self.load_plugins(pluginstrs)

        # collect Plugin.PLUGIN_FUNCS into a sequence dict
        plugins_dict = collections.OrderedDict()
        seq_dict = collections.OrderedDict()
        for i, Plugin_cls in enumerate(plugins_list):
            key = (i, Plugin_cls)
            plugin = plugins_dict[key] = Plugin_cls(self.conf)
            for fn_name in self.PLUGIN_FUNCS:
                _fn = getattr(plugin, fn_name, None)
                if _fn:
                    list_ = seq_dict.setdefault(fn_name, [])
                    list_.append(((key, fn_name), _fn))

        # run each function in the sequence dict
        # and make assertions
        for fn_name, seq in iteritems(seq_dict):
            log.debug(('sequence.step', fn_name))
            for key, _fn in seq:
                mrostr = inspect.getmro(_fn.__class__)
                if not hasattr(bookmarks_obj, 'bookmarks_dict'):
                    raise Exception((_fn, bookmarks_obj))

                log.debug(('sequence.step.%s' % fn_name, _fn))
                bookmarks_obj_2 = _fn(bookmarks_obj)
                if not bookmarks_obj_2:
                    raise Exception(mrostr, bookmarks_obj_2)
                if not hasattr(bookmarks_obj_2, 'bookmarks_dict'):
                    raise Exception((_fn, bookmarks_obj_2))

                # XXX
                #log.debug(('sequence.step.%s' % fn_name, _fn,
                #           bookmarks_obj_2.bookmarks_dict))
                bookmarks_obj = bookmarks_obj_2

        return bookmarks_obj


__all__ = ['PromiumPlugin', 'DEFAULT_PLUGINS', 'PluginSequence',
           'get_datetime_now_longdate']
