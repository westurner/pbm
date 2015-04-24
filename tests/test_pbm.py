#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pbm
----------------------------------

Tests for `pbm` module.
"""

import unittest

import pbm
import pbm.main as pb

import collections
import itertools
import json
import logging

log = logging.getLogger(__name__)

pbm

class TestPromiumbookmarks(unittest.TestCase):

    def setUp(self):
        self.bookmarks_path = './tests/data/Bookmarks'

    def log(self, *args):
        print(args)

    def tearDown(self):
        pass

    def test_00_imports(self):
        import pbm.main as pb
        self.assertTrue(pb)
        import pbm.plugins as plugins
        self.assertTrue(plugins)
        import pbm.plugins.datefolders as dbf
        self.assertTrue(dbf)

    def test_01_list_bookmarks(self):
        from pbm.main import list_profile_bookmarks
        output = list_profile_bookmarks()
        self.assertTrue(hasattr(output, '__iter__'))
        output = list(output)
        self.assertTrue(len(output))
        output = list_profile_bookmarks(show_backups=True)
        self.assertTrue(hasattr(output, '__iter__'))
        output = list(output)
        self.assertTrue(len(output))

    def test_11_read_bookmarks(self):
        from pbm.main import ChromiumBookmarks
        bookmarks = ChromiumBookmarks.read_bookmarks(self.bookmarks_path)
        self.assertTrue(bookmarks)

    def a_test_21_print_bookmarks(self):
        from pbm.main import ChromiumBookmarks
        bookmarks = ChromiumBookmarks.read_bookmarks(self.bookmarks_path)
        output = ChromiumBookmarks.print_bookmarks(bookmarks)
        self.assertTrue(output)

    def check_bookmarks_list(self, bookmarks):
        bookmarks = list(bookmarks)
        length = len(bookmarks)
        self.log(('n', length))
        counts = collections.Counter(b.get('id') for b in bookmarks)
        duplicates = [(k, v) for (k, v) in counts.iteritems() if v > 1]
        self.log(("duplicate id counts:", repr(duplicates)))
        #self.assertFalse(duplicates)

    def test_30_check_bookmarks_list_ids(self):
        import pbm.main as pb
        bookmarks_obj = pb.ChromiumBookmarks(bookmarks_path=self.bookmarks_path)
        self.check_bookmarks_list(bookmarks_obj.bookmarks_list)

    def test_31_walk_bookmarks(self):
        from pbm.main import ChromiumBookmarks
        bookmarks = ChromiumBookmarks.read_bookmarks(self.bookmarks_path)
        self.assertTrue(bookmarks)
        bookmarks = itertools.chain(
            ChromiumBookmarks.walk_bookmarks(
                bookmarks['roots']['bookmark_bar']),
            ChromiumBookmarks.walk_bookmarks(
                bookmarks['roots']['other']))
        self.check_bookmarks_list(bookmarks)

    def test_33_iter_bookmarks(self):
        from pbm.main import ChromiumBookmarks
        bookmarks = list(ChromiumBookmarks.iter_bookmarks(self.bookmarks_path))
        self.assertTrue(bookmarks)

    def test_41_reorganize_by_date(self):
        from pbm.main import ChromiumBookmarks
        bookmarks_obj = ChromiumBookmarks(bookmarks_path=self.bookmarks_path)
        self.assertTrue(bookmarks_obj)
        log.debug(self.bookmarks_path)
        bookmarks_list = bookmarks_obj.bookmarks_list
        self.assertTrue(bookmarks_list)
        import pbm.plugins.datefolders as dbf
        bookmarks_list = dbf.DateBasedFoldersPlugin.reorganize_by_date(bookmarks_obj)
        self.assertTrue(bookmarks_list)
        bookmarks_obj.bookmarks_dict['roots']['bookmark_bar']['children'] = (
            bookmarks_list)
        json_output = bookmarks_obj.to_json()
        self.assertTrue(json_output)
        json_output = json.dumps(bookmarks_obj.bookmarks_dict, indent=2)
        self.assertTrue(json_output)

    def test_51_rewrite_bookmarks(self):
        from pbm.main import ChromiumBookmarks
        bookmarks_dict = ChromiumBookmarks.transform_bookmarks_dict(
            bookmarks_path=self.bookmarks_path)
        bookmarks_json = ChromiumBookmarks._to_json(bookmarks_dict)
        ChromiumBookmarks.organize_bookmarks_json(
            bookmarks_json,
            self.bookmarks_path + '.test51.bak',
            prompt=False)
        output_json = json.dumps(bookmarks_dict, indent=2)
        self.assertTrue(json.loads(output_json), bookmarks_dict)

    def test_60_get_option_parser(self):
        from pbm.main import get_option_parser
        prs = get_option_parser()
        self.assertTrue(prs)

    def test_61_main(self):
        from pbm.main import main
        import sys
        __sys_argv = sys.argv
        sys.argv = [__file__]

        try:
            with self.assertRaises(IOError):
                output = main()
                self.assertEqual(output, 0)
                output = main(['-v'])
                self.assertEqual(output, 0)
                output = main(['--print-all'])
                self.assertEqual(output, 0)

            TEST_BOOKMARKS = './tests/data/Bookmarks'
            output = main(['-v', TEST_BOOKMARKS])
            self.assertEqual(output, 0)
            output = main(['--print-all', TEST_BOOKMARKS])
            self.assertEqual(output, 0)
            output = main(['--print-json-link-list', TEST_BOOKMARKS])
            self.assertEqual(output, 0)
            output = main(['--print-html-link-list', TEST_BOOKMARKS])
            self.assertEqual(output, 0)
            output = main(['--print-html-tree', TEST_BOOKMARKS])
            self.assertEqual(output, 0)
        finally:
            sys.argv = __sys_argv

    def test_81_plugins(self):
        import pbm.plugins.null
        import pbm.plugins.dedupe
        import pbm.plugins.bookmarkletsfolder
        import pbm.plugins.chromefolder
        import pbm.plugins.datefolders
        import pbm.plugins.quicklinks
        import pbm.plugins.allinone
        import pbm.plugins.starred
        import pbm.plugins.queuefolder

    def test_82_plugins_strlist(self):
        import pbm.plugins as plugins
        DEFAULT_PLUGINS = [
            'null',
            'dedupe',
            'bookmarkletsfolder',
            'chromefolder',
            'datefolders',
            'quicklinks',
            'starred',
            'allinone',
            'queuefolder',
        ]
        _plugins = plugins.PluginSequence.load_plugins(
            pluginstrs=[])
        self.assertEqual(_plugins, [])

        _plugins = plugins.PluginSequence.load_plugins(
            pluginstrs=DEFAULT_PLUGINS)
        self.assertTrue(_plugins)

        _plugins = plugins.PluginSequence.load_plugins()
        self.assertTrue(_plugins)

    def test_97_pbm(self):
        from pbm.main import ChromiumBookmarks
        cb = ChromiumBookmarks(self.bookmarks_path)
        output = list(cb)
        self.assertTrue(output)

        output = cb.organize(dest=self.bookmarks_path + '.test97.bak',
                             prompt=False)
        self.assertTrue(output)

    def test_99_pbm(self):
        from pbm.main import ChromiumBookmarks
        cb = ChromiumBookmarks(self.bookmarks_path)
        output = list(cb)
        self.assertTrue(output)

        output = cb.organize(dest=self.bookmarks_path + '.test99.bak',
                             prompt=False)
        self.assertTrue(output)

        cb2 = ChromiumBookmarks(self.bookmarks_path + '.test99.bak')
        cbdict = cb2.bookmarks_dict
        queue_folders = [x for x in cbdict['roots']['bookmark_bar']['children']
                         if x.get('name') == 'queue']
        self.assertEqual(len(queue_folders), 1, queue_folders)

        queue = queue_folders[0]

        max_node = None
        max_id = 0
        for bm in iter(cb2):
            idstr = bm.get('id', 0)
            _id = long(idstr)
            if _id > max_id:
                max_id = _id
                max_node = bm

        self.assertGreaterEqual(queue['id'], max_id) # , max_node)

#   class Test0PluginManager(unittest.TestCase):
#       def test_00_get_plugins(self):
#           from pbm.main import PluginManager
#           output = PluginManager.get_plugins()
#           self.assertTrue(output)
#           x = list(output)
#           self.assertTrue(x)
#
#       def test_00_list_plugins(self):
#           from pbm.main import PluginManager
#           output = PluginManager.list_plugins()
#           self.assertTrue(output)
#           x = list(output)
#           self.assertTrue(x)

import os
import pbm.plugins as plugins

class PluginTestCase(unittest.TestCase):

    bookmarks_path = os.path.join('tests', 'data', 'Bookmarks')
    pluginstrs = ['null',]  # .NullPlugin
    conf = {}
    folder_name = None

    def setUp(self):
        self.pluginseq = plugins.PluginSequence(
            pluginstrs=self.pluginstrs)
        self.bookmarks_obj = pb.ChromiumBookmarks(
            bookmarks_path=self.bookmarks_path)

    # def tearDown(self):
    #    pass

    def test_000_plugin_interface(self):
        plugin_funcs = plugins.PromiumPlugin.PLUGIN_FUNCS
        for plugin in self.pluginseq.plugins:
            self.assertTrue(
                any(hasattr(plugin, func)
                    for func in plugin_funcs))

    def test_00_plugin_conf(self):
        bookmarks_obj = self.bookmarks_obj
        list_count = len(bookmarks_obj.bookmarks_list)
        self.assertTrue(bookmarks_obj)
        self.assertTrue(hasattr(bookmarks_obj, 'bookmarks_dict'))
        bookmarks_dict = bookmarks_obj.bookmarks_dict
        self.assertTrue(bookmarks_dict)
        self.assertTrue(hasattr(bookmarks_obj, 'bookmarks_list'))
        if list_count:
            bookmarks_list = bookmarks_obj.bookmarks_list
            self.assertTrue(bookmarks_list)

    def test_10_build_pluginseq(self):
        bookmarks_obj = self.pluginseq.run(
            self.bookmarks_obj,
            pluginstrs=self.pluginstrs)
        self.assertTrue(bookmarks_obj)
        #self.assertTrue(bookmarks_obj.bookmarks_dict)
        #self.assertTrue(bookmarks_obj.bookmarks_list)

    def get_bookmark_bar_nodes(self):
        return (
            self.bookmarks_obj
            .bookmarks_dict['roots']['bookmark_bar']['children'])

    def get_bookmark_bar_foldernames(self):
        return [x.get('name') for x in self.get_bookmark_bar_nodes()]

    def get_Other_Bookmarks_foldernames(self):
        return [x.get('name') for x in (
                self.bookmarks_obj.bookmarks_dict['roots']
                .get('Other Bookmarks', {})
                .get('children', []))]

    def test_10_folderexists_after(self):
        if self.folder_name:
            folder_name = self.folder_name
            #self.assertIn(folder_name, self.get_bookmark_bar_foldernames())
            self.bookmarks_obj = self.pluginseq.run(self.bookmarks_obj)
            self.assertIn(folder_name, self.get_bookmark_bar_foldernames())


class TestChromeFolderPlugin(PluginTestCase):
    pluginstrs = ['chromefolder']
    folder_name = 'chrome'


class TestDateBasedFoldersPlugin(PluginTestCase):
    pluginstrs = ['datefolders']

    def test_10_bookmarks_list(self):
        self.assertTrue(self.bookmarks_obj.bookmarks_list)

    def test_20_folderexists(self):
        self.assertTrue(self.bookmarks_obj.bookmarks_list)
        log.debug(self.bookmarks_obj.bookmarks_list)
        self.bookmarks_obj = self.pluginseq.run(self.bookmarks_obj)
        self.assertIn('2014', self.get_bookmark_bar_foldernames())


class TestBookmarkletsFolderPlugin(PluginTestCase):
    pluginstrs = ['bookmarkletsfolder']
    folder_name = 'bookmarklets'


class TestQueueFolderPlugin(PluginTestCase):
    pluginstrs = ['queuefolder']
    folder_name = 'queue'


class TestQuicklinksFolderPlugin(PluginTestCase):
    pluginstrs = ['quicklinks']
    # folder_name = 'quicklinks'


class TestAdditionalAllFolderPlugin(PluginTestCase):
    pluginstrs = ['allinone']
    folder_name__ = 'all'


class TestStarredFolderPlugin(PluginTestCase):
    pluginstrs = ['starred']
    folder_name = 'starred'

    def test_20_one_starred_folder_with_children(self):
        self.assertTrue(self.bookmarks_obj.bookmarks_list)
        log.debug(self.bookmarks_obj.bookmarks_list)
        self.bookmarks_obj = self.pluginseq.run(self.bookmarks_obj)
        starred_folders = [x for x in self.bookmarks_obj.bookmark_bar
                   if x.get('name') == self.folder_name]
        self.assertEqual(len(starred_folders), 1)
        starred = starred_folders[0]
        self.assertTrue(starred)
        self.assertTrue(starred.get('children',[]))


class TestAll(PluginTestCase):
    pluginstrs = pb.plugins.PluginSequence.DEFAULT_PLUGINS

    def test_20_queue_folder_at_end(self):
        self.assertTrue(self.bookmarks_obj.bookmarks_list)
        log.debug(self.bookmarks_obj.bookmarks_list)
        self.bookmarks_obj = self.pluginseq.run(self.bookmarks_obj)
        queue_folders = [x for x in self.bookmarks_obj.bookmark_bar
                   if x.get('name') == 'queue']
        self.assertEqual(len(queue_folders), 1)
        queue = queue_folders[0]
        self.assertTrue(queue)
        self.assertEqual(queue.get('children'), [])


        by_id = collections.OrderedDict()
        for x in self.bookmarks_obj:
            id_ = x.get('id')
            by_id.setdefault(id_, [])
            by_id[id_].append(x)

        for id_, nodes in by_id.items():
            self.assertEqual(len(nodes), 1, (len(nodes), nodes))


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
