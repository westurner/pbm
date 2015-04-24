#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
pbm_app
"""

import json
import logging
import os.path

import tornado
import tornado.web
import tornado.ioloop

import pbm.main
import utils

log = logging.getLogger('pbm.app')


class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        return self.get_secure_cookie("user")


class MainHandler(BaseHandler):

    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
#        name = tornado.escape.xhtml_escape(self.current_user)
#        self.write("Hello, " + name)
        template_name = 'main.jinja'
        t = utils.get_template(template_name)
        htmlstr = t.render({'name': self.current_user})
        self.write(htmlstr)


class LoginHandler(BaseHandler):

    def get(self):
        self.render('templates/login.html')

    def post(self):
        self.set_secure_cookie("user", self.get_argument("name"))
        self.redirect("/")


class BookmarksBaseHandler(BaseHandler):

    def initialize(self, bookmarks_file=None):
        if bookmarks_file is None:
            bookmarks_file = self.settings['bookmarks_file']
            self.cb = self.settings['cb']
        else:
            self.cb = pbm.main.ChromiumBookmarks(bookmarks_file)


class BookmarksJSONHandler(BookmarksBaseHandler):

    @tornado.web.authenticated
    def get(self):
        indent = self.get_query_argument('indent', None)
        if indent:
            try:
                indent = int(indent)
                if indent not in (0, 1, 2, 4):
                    raise ValueError
            except ValueError:
                indent = None

        if not indent:
            self.write(self.cb.bookmarks_dict)
        else:
            self.set_header('content-type', 'application/json')
            self.write(json.dumps(self.cb.bookmarks_dict, indent=indent))


class BookmarksLinksJSONHandler(BookmarksBaseHandler):

    @tornado.web.authenticated
    def get(self):
        bookmark_urls = [b.get('url') for b in iter(self.cb)]
        self.write(tornado.escape.json_encode(bookmark_urls))
        self.set_header('content-type', 'application/json')


class BookmarksListHandler(BookmarksBaseHandler):

    @tornado.web.authenticated
    def get(self):
        template_name = 'bookmarks_list_partial.jinja'
        t = utils.get_template(template_name)
        htmlstr = t.render({
            'bookmarks': self.cb,
            'bookmarks_iter': iter(self.cb)})
        self.write(htmlstr)


def format_longdate(longdate):
    if longdate:
        return pbm.utils.longdate_to_datetime(longdate).isoformat() + "Z"
    return longdate


import urllib


def build_rdf_uri_quotechars_dict():
    quotechars = [chr(n) for n in xrange(0x0, 0x20)]
    quotechars += [c for c in """ <>"{}|^`\\"""]
    return dict.fromkeys(quotechars)


RDF_URI_QUOTECHARS_DICT = build_rdf_uri_quotechars_dict()


def rdf_uri_escape(url):

    def _quote_URI_chars(url):
        for char in url:
            if char in RDF_URI_QUOTECHARS_DICT:
                yield urllib.quote(char)
            else:
                yield char
    return u''.join(_quote_URI_chars(url))


class BookmarksTreeHandler(BookmarksBaseHandler):

    @tornado.web.authenticated
    def get(self):
        template_name = 'bookmarks_tree_partial.jinja'
        t = utils.get_template(template_name)
        htmlstr = t.render({
            'bookmarks': self.cb,
            'bookmarks_iter': iter(self.cb),
            'format_longdate': format_longdate,
            'rdf_uri_escape': rdf_uri_escape})
        self.write(htmlstr)


class BookmarksHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        template_name = 'bookmarks.jinja'
        t = utils.get_template(template_name)
        htmlstr = t.render()
        self.write(htmlstr)


def make_app(config=None, DEFAULT_COOKIE_SECRET="."):
    """
    mainfunc
    """
    _conf = dict()
    _conf.update({
        'cookie_secret': DEFAULT_COOKIE_SECRET,
        "static_path": os.path.join(os.path.dirname(__file__), 'static'),
        "login_url": "/login",
        "xsrf_cookies": True,

        'bookmarks_file': os.path.join(
            os.path.dirname(__file__), '..', 'tests/data/Bookmarks')
    })
    if config is not None:
        _conf.update(config)

    _conf['cb'] = pbm.main.ChromiumBookmarks(
        _conf['bookmarks_file'])

    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/login", LoginHandler),
        (r"/bookmarks/chrome", BookmarksHandler),
        (r"/bookmarks/chrome/json", BookmarksJSONHandler),
        (r"/bookmarks/chrome/links.json", BookmarksLinksJSONHandler),
        (r"/bookmarks/chrome/list", BookmarksListHandler),
        (r"/bookmarks/chrome/tree", BookmarksTreeHandler),
    ], **_conf)
    return application


import unittest


class Test_pbm_app(unittest.TestCase):

    def test_pbm_app(self):
        app = make_app()
        self.assertTrue(app)
        self.assertTrue(hasattr(app, 'settings'))
        self.assertIn('login_url', app.settings)
        self.assertIn('xsrf_cookies', app.settings)
        self.assertIn('bookmarks_file', app.settings)
        self.assertIn('cb', app.settings)

    def test_pbm_app_conf(self):
        app = make_app({'test': 'test'})
        self.assertTrue(app)
        self.assertTrue(hasattr(app, 'settings'))
        self.assertIn('test', app.settings)
        self.assertIn('login_url', app.settings)
        self.assertIn('xsrf_cookies', app.settings)
        self.assertIn('bookmarks_file', app.settings)
        self.assertIn('cb', app.settings)


def main(argv=None):
    import optparse
    import sys

    prs = optparse.OptionParser(usage="%prog : args")

    prs.add_option('-f', '--file',
                   dest='bookmarks_file',
                   action='store')

    prs.add_option('-H', '--host',
                   dest='host',
                   default='localhost',
                   action='store')
    prs.add_option('-P', '--port',
                   dest='port',
                   default='28881',
                   action='store')

    prs.add_option('-r', '--reload', '--autoreload',
                   dest='autoreload',
                   action='store_true')

    prs.add_option('-D', '--debug',
                   dest='debug',
                   action='store_true')

    prs.add_option('-v', '--verbose',
                   dest='verbose',
                   action='store_true',)
    prs.add_option('-q', '--quiet',
                   dest='quiet',
                   action='store_true',)
    prs.add_option('-t', '--test',
                   dest='run_tests',
                   action='store_true',)
    args = list(argv) if argv is not None else sys.argv[1:]
    (opts, args) = prs.parse_args(args=args)

    loglevel = logging.INFO
    if opts.quiet:
        loglevel = logging.ERROR
    if opts.verbose:
        loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel)

    if opts.run_tests:
        import sys
        sys.argv = [sys.argv[0]] + args
        import unittest
        return unittest.main()

    n_procs = 0  # one per CPU
    conf = {}
    if opts.bookmarks_file:
        conf['bookmarks_file'] = opts.bookmarks_file
    if opts.autoreload:
        conf['autoreload'] = True
        n_procs = 1
    if opts.debug:
        conf['debug'] = True
        n_procs = 1
    app = make_app(conf)

    import tornado.httpserver
    try:
        log.info("Serving at http://%s:%s/", opts.host, opts.port)
        log.info("conf: %r", conf)
        server = tornado.httpserver.HTTPServer(app)
        server.bind(opts.port)  # TODO: host
        server.start(n_procs)  # forks one process per cpu
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.current().stop()
        server.stop()
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main(argv=sys.argv[1:]))
