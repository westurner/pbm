#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
promiumbookmarks_app
"""

import os.path

import tornado
import tornado.web
import tornado.ioloop

import promiumbookmarks.main

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")


class MainHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
        name = tornado.escape.xhtml_escape(self.current_user)
        self.write("Hello, " + name)


class LoginHandler(BaseHandler):
    def get(self):
        self.render('templates/login.html')

    def post(self):
        self.set_secure_cookie("user", self.get_argument("name"))
        self.redirect("/")


class BookmarksListHandler(BaseHandler):
    def get(self):
        cb = promiumbookmarks.main.ChromiumBookmarks('./tests/data/Bookmarks')
        template_name = 'bookmarks_list_partial.jinja'
        t = promiumbookmarks.main.get_template(template_name)
        htmlstr = t.render({
            'bookmarks': cb,
            'bookmarks_iter': iter(cb)})
        self.write(htmlstr)


def format_longdate(longdate):
    if longdate:
        return promiumbookmarks.main.longdate_to_datetime(longdate).isoformat() + "Z"
    return longdate


def startswith_data_js(url):
    if url.startswith('data:') or url.startswith('javascript:'):
        return True
    return False


import urllib


def sanitize_bookmark_url(url):
    quotechars = [chr(n) for n in xrange(0x0, 0x20)]
    quotechars += [c for c in """ <>"{}|^`\\"""]
    quotechars_dict = dict.fromkeys(quotechars)

    def _quote_URI_chars(url):
        for char in url:
            if char in quotechars_dict:
                yield urllib.quote(char)
            else:
                yield char
    return u''.join(_quote_URI_chars(url))


class BookmarksTreeHandler(BaseHandler):
    def get(self):
        bookmarks_file = self.settings['bookmarks_file']
        cb = promiumbookmarks.main.ChromiumBookmarks(bookmarks_file)
        template_name = 'bookmarks_tree_partial.jinja'
        t = promiumbookmarks.main.get_template(template_name)
        htmlstr = t.render({
            'bookmarks': cb,
            'bookmarks_iter': iter(cb),
            'format_longdate': format_longdate,
            'startswith_data_js': startswith_data_js,
            'sanitize_bookmark_url': sanitize_bookmark_url})
        self.write(htmlstr)


class BookmarksHandler(BaseHandler):
    def get(self):
        template_name = 'bookmarks.jinja'
        t = promiumbookmarks.main.get_template(template_name)
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

    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/login", LoginHandler),
        (r"/bookmarks", BookmarksHandler),
        (r"/bookmarks/list", BookmarksListHandler),
        (r"/bookmarks/dict", BookmarksTreeHandler),
    ], **_conf)
    return application


import unittest
class Test_promiumbookmarks_app(unittest.TestCase):
    def test_promiumbookmarks_app(self):
        pass


def main(argv=[__name__]):
    import optparse
    import logging

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

    prs.add_option('-v', '--verbose',
                    dest='verbose',
                    action='store_true',)
    prs.add_option('-q', '--quiet',
                    dest='quiet',
                    action='store_true',)
    prs.add_option('-t', '--test',
                    dest='run_tests',
                    action='store_true',)

    (opts, args) = prs.parse_args(args=argv[1:])

    if not opts.quiet:
        logging.basicConfig()

        if opts.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    if opts.run_tests:
        import sys
        sys.argv = [sys.argv[0]] + args
        import unittest
        return unittest.main()

    conf = {}
    if opts.bookmarks_file:
        conf['bookmarks_file'] = opts.bookmarks_file
    app = make_app(conf)

    import tornado.httpserver
    try:
        server = tornado.httpserver.HTTPServer(app)
        server.bind(opts.port) ## TODO: host
        server.start(0)  # forks one process per cpu
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.current().stop()
        server.stop()
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main(argv=sys.argv))
