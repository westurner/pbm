#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
test_app.py -- test pbm.app tornado application
"""

from contextlib import contextmanager

import tornado.testing
from urlobject import URLObject

from pbm.app import make_app
from pbm.app import BaseHandler


@contextmanager
def nop_auth(username="testuser"):
    __get_current_user = BaseHandler.get_current_user

    def _(*args, **kwargs):
        if username is None:
            return None
        return {'name': username}

    try:
        BaseHandler.get_current_user = _
        yield
    finally:
        BaseHandler.get_current_user = __get_current_user


import urllib


class Test_app(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        return make_app()

    def GET(self, url, data=None, headers=None):
        data = data if data is not None else {}
        headers = headers if headers is not None else {}
        url_ = "{}?{}".format(url, urllib.urlencode(data))
        return self.fetch(url_, method='GET', headers=headers)

    def POST(self, url, data=None, headers=None):
        data = data if data is not None else {}
        headers = headers if headers is not None else {}
        data['_xsrf'] = 'testtest'
        body = urllib.urlencode(data)
        headers['Cookie'] = "_xsrf=testtest"
        return self.fetch(url, method='POST', headers=headers, body=body)

    def test_main_without_nop_auth(self):
        resp = self.fetch('/')
        self.assertEqual(resp.code, 200)
        self.assertEqual(URLObject(resp.effective_url).path, '/login')

        with nop_auth(None):
            resp = self.fetch('/')
            self.assertEqual(resp.code, 200)
            self.assertEqual(URLObject(resp.effective_url).path, '/login')

    def test_login(self):
        resp = self.fetch('/login')
        self.assertEqual(resp.code, 200)
        self.assertIn('name="_xsrf"', resp.body)

    def test_main_as_testuser(self):
        with nop_auth():
            resp = self.fetch('/')
            self.assertEqual(resp.code, 200)
            self.assertEqual(URLObject(resp.effective_url).path, '/')
            self.assertIn('<a class="mainlinkR" href="/bookmarks/chrome', resp.body)
            # raise Exception((resp, dir(resp)))

    def test_bookmarks(self):
        with nop_auth():
            resp = self.fetch('/bookmarks/chrome')
            self.assertEqual(resp.code, 200)
            self.assertIn('''<div id="jstree">''', resp.body)

    def test_bookmarks_json(self):
        with nop_auth():
            resp = self.fetch('/bookmarks/chrome/json')
            self.assertEqual(resp.code, 200)
            self.assertIn('''bookmark_bar''', resp.body)
            import json
            data = json.loads(resp.body)
            self.assertTrue(data)
            self.assertTrue(isinstance(data, dict))

    def test_bookmarks_list(self):
        with nop_auth():
            resp = self.fetch('/bookmarks/chrome/list')
            self.assertEqual(resp.code, 200)
            self.assertIn('''typeof="#BookmarksList"''', resp.body)

    def test_bookmarks_links_json(self):
        with nop_auth():
            resp = self.fetch('/bookmarks/chrome/links.json')
            self.assertEqual(resp.code, 200)
            self.assertIn('''data:text/html, <html style''', resp.body)
            import json
            data = json.loads(resp.body)
            self.assertTrue(data)
            self.assertTrue(isinstance(data, list))

    def test_bookmarks_tree(self):
        with nop_auth():
            resp = self.fetch('/bookmarks/chrome/tree')
            self.assertEqual(resp.code, 200)
            self.assertIn('''typeof="pb:BookmarksTree"''', resp.body)

    def test_bookmarks_tree_rdfa(self):
        with nop_auth():
            resp = self.fetch('/bookmarks/chrome/tree')
            self.assertEqual(resp.code, 200)
            self.assertIn('''typeof="pb:BookmarksTree"''', resp.body)
            import rdflib
            import rdflib.tools.rdfpipe
            import StringIO
            input_format = 'rdfa'
            graph = rdflib.ConjunctiveGraph()
            graph.parse(StringIO.StringIO(resp.body), format=input_format)
            self.assertTrue(graph)

            for output_format in ['xml', 'n3']:  # json-ld
                output = graph.serialize(format=output_format)
                self.assertTrue(output)

            try:
                import rdflib_jsonld
                rdflib_jsonld
                output_format = 'json-ld'
                output = graph.serialize(format=output_format, auto_compact=True)
                self.assertTrue(output)
            except ImportError:
                pass
                # TODO: skipif

    def get_post_tst(self, url, data, func):
        with nop_auth():
            resp_get = self.GET(url, data)
            func(self, resp_get)

            resp_post = self.POST(url, data)
            func(self, resp_post)

    def test_search_00(self):
        url = '/search'
        data = {}

        def testfunc(self, resp):
            self.assertEqual(resp.code, 200)
            self.assertIn('<title>search | pbm</title>', resp.body)
            self.assertIn('upgrade', resp.body)
            # TODO: this lists every bookmark
        self.get_post_tst(url, data, testfunc)

    def test_search_01_html(self):
        url = '/search'
        data = {'q': 'upgrade', 'dest': 'html'}

        def testfunc(self, resp):
            self.assertIn('<title>search | pbm</title>', resp.body)
            self.assertIn('upgrade', resp.body)
        self.get_post_tst(url, data, testfunc)

    def test_search_02_json(self):
        url = '/search'
        data = {'q': 'upgrade', 'dest': 'json'}

        def testfunc(self, resp):
            self.assertEqual(resp.code, 200)
            url = URLObject(resp.effective_url)
            self.assertEqual(url.path, '/q.json')
            self.assertEqual(url.query, 'q=upgrade&stars=0')
        self.get_post_tst(url, data, testfunc)

    def test_search_03_brw(self):
        url = '/search'
        data = {'q': 'upgrade', 'dest': 'brw'}

        def testfunc(self, resp):
            self.assertEqual(resp.code, 200)
            url = URLObject(resp.effective_url)
            self.assertEqual(url.path, '/static/brw/brw2.html')
            self.assertEqual(url.fragment, '!/q.json?q=upgrade&stars=0')
            self.assertIn('<title>brw2</title>', resp.body)
        self.get_post_tst(url, data, testfunc)

    def test_search_chrome_bookmarks_search_json(self):
        url = '/bookmarks/chrome/search.json'
        data = {}

        def testfunc(self, resp):
            self.assertEqual(resp.code, 200)
        self.get_post_tst(url, data, testfunc)

    def test_search_qjson_00(self):
        url = '/q.json'
        data = {}

        def testfunc(self, resp):
            self.assertEqual(resp.code, 200)
            self.assertIn('upgrade', resp.body)
        self.get_post_tst(url, data, testfunc)

    def test_search_qjson_01_q(self):
        url = '/q.json'
        data = {'q': 'upgrade'}

        def testfunc(self, resp):
            self.assertEqual(resp.code, 200)
            self.assertIn('upgrade', resp.body)
        self.get_post_tst(url, data, testfunc)

    def test_search_qjson_02_stars(self):
        url = '/q.json'
        data = {'stars': 3}

        def testfunc(self, resp):
            self.assertEqual(resp.code, 200)
            self.assertIn('https://wrdrd.github.io/####', resp.body)
        self.get_post_tst(url, data, testfunc)

    def test_search_qjson_03_q_stars(self):
        url = '/q.json'
        data = {'q': 'zero', 'stars': 3}

        def testfunc(self, resp):
            self.assertEqual(resp.code, 200)
            self.assertEqual('[]', resp.body)
        self.get_post_tst(url, data, testfunc)

    def test_search_qjson_04_q_stars(self):
        url = '/q.json'
        data = {'q': '', 'stars': 0}

        def testfunc(self, resp):
            self.assertEqual(resp.code, 200)
            self.assertIn('upgrade', resp.body)
        self.get_post_tst(url, data, testfunc)
