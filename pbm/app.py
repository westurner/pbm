#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
pbm/app.py -- pbmweb
"""

import json
import logging
import os.path

import tornado
import tornado.web
import tornado.ioloop

from jinja_tornado import JinjaApp, JinjaTemplateMixin

import pbm.main
import utils

log = logging.getLogger('pbm.app')

SECURE_USER_COOKIE_KEY = "user"


class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        return self.get_secure_cookie(SECURE_USER_COOKIE_KEY)

class BaseHandlerJinja(JinjaTemplateMixin, BaseHandler):
    pass


class MainHandler(BaseHandlerJinja):
    template_path = 'main.jinja'

    @tornado.web.authenticated
    def get(self):
        ctxt = ({
            'current_user': self.current_user,
            'urls': self._get_urls(self.current_user),
            'form_values': {}
        })
        return self.render(self.template_path, **ctxt)
        #self.write(htmlstr)

    def _get_urls(self, current_user=None):
        """Get a list of URLs for the current user

        Keyword Arguments:
            current_user (str|None): e.g. ``self.current_user``

        Returns:
            list[dict]: ``{'name': str, 'url': str}``
        """
        urls = [
            {'name': 'home',
             'url': '/', },
        ]
        if current_user is None:
            urls.extend([
                {'name': 'login',
                 'url': '/login', },
            ])
        else:
            urls.extend([
                {'name': 'bookmarks list #html',
                 'url': '/bookmarks/chrome/list'},
                {'name': 'bookmarks tree #html #rdfa',
                 'url': '/bookmarks/chrome/tree'},
                {'name': 'bookmarks tree #html #rdfa #js',
                 'url': '/bookmarks'},
                {'name': 'bookmark links #json',
                 'url': '/bookmarks/chrome/links.json'},
                {'name': 'starred bookmark links #json',
                 'url': '/bookmarks/chrome/starred.json'},
                {'name': 'brw',
                 'url': '/brw'},
                {'name': 'brw original',
                 'url': '/static/brw/index.html'},
                {'name': 'brw2: all links',
                 'url': '/static/brw/brw2.html#!/bookmarks/chrome/links.json'},
                {'name': 'brw2: starred',
                 'url': '/static/brw/brw2.html#!/q.json?stars=1'},
                {'name': 'bookmarks tree #json',
                 'url': '/bookmarks/chrome/json'},
                {'name': 'search',
                 'url': '/search'},
            ])
        urls.extend([
            {'name': 'about',
             'url': '/about'},
        ])
        if current_user:
            urls.extend([
                {'name': 'logout',
                 'url': '/logout'},
            ])
        return urls

class AboutHandler(BaseHandlerJinja):
    template_path = 'about.jinja'

    def get(self):
        return self.render(self.template_path)

class LoginHandler(BaseHandlerJinja):
    template_path = 'login.jinja'

    def get(self):
        log.debug(self.application.jinja_environment.loader.__dict__)
        self.render(self.template_path)

    @staticmethod
    def check_login(name, pass_):
        if not name:
            return False
        if not pass_:
            return False
        if not hasattr(name, '__len__'):
            return False
        if not hasattr(pass_, '__len__'):
            return False
        if len(name) <= 2:
            return False
        if name == pass_[::-1]:
            return True
        return False

    def post(self):
        name = self.get_argument("name")
        pass_ = self.get_argument("pass")
        auth_ok = self.check_login(name, pass_)

        if auth_ok:
            self.set_secure_cookie(SECURE_USER_COOKIE_KEY,
                                name)
            self.redirect("/")
        else:
            self.redirect("/login")


class LogoutHandler(BaseHandler):

    def get(self):
        self.clear_cookie('user')
        self.redirect('/')

    def post(self):
        self.clear_cookie('user')
        self.redirect("/")


class BookmarksBaseHandler(BaseHandler):

    def initialize(self,
                   bookmarks_file=None,
                   HTTP_ACCESS_CONTROL_ALLOW_ORIGIN=None):
        if bookmarks_file is None:
            bookmarks_file = self.settings['bookmarks_file']
            self.cb = self.settings['cb']
        else:
            self.cb = pbm.main.ChromiumBookmarks(bookmarks_file)

        if HTTP_ACCESS_CONTROL_ALLOW_ORIGIN:
            # HTTP CORS
            self.set_header('Access-Control-Allow-Origin',
                            HTTP_ACCESS_CONTROL_ALLOW_ORIGIN)


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


import collections


class BookmarksSearchJSONHandler(BookmarksBaseHandler):

    @staticmethod
    def iter_starred(cb, n_stars):
        dedupe = collections.OrderedDict()
        for bookmark in iter(cb):
            url = bookmark.get('url')
            if url.endswith('#'*n_stars):
                url_without = url.rstrip('#')
                dupelist = dedupe.setdefault(url_without, [])
                dupelist.append(bookmark)
        for key in dedupe:
            urls = dedupe[key]
            most_stars = urls[
                sorted(
                    ((len(bookmark.get('url', '')), i)
                     for (i, bookmark) in enumerate(urls)),
                    reverse=True)[0][1]]
            yield most_stars

    @staticmethod
    def iter_stringmatch(cb, term):
        for b in iter(cb):
            if (
                (term in b.get('url').lower())
                or
                (term in b.get('name').lower())):
                yield b

    @staticmethod
    def iter_search(self, cb, **kwargs):
        term = kwargs.get('q')
        stars = kwargs.get('stars', 0)
        if stars is None or stars < 0:
            stars = 0
        iterable = iter(cb)
        iterable = self.iter_starred(iterable, stars)  # dedupe
        if term:
            iterable = self.iter_stringmatch(iterable, term)
        return iterable

    @staticmethod
    def get_search_arguments(self):
        term = self.get_argument('q', default=None)
        try:
            stars = int(self.get_argument('stars', default=0))
        except AttributeError:
            stars = None
        return dict(q=term, stars=stars)

    def get_or_post(self):
        kwargs = self.get_search_arguments(self)
        bookmark_urls = list(self.iter_search(self, iter(self.cb), **kwargs))
        self.write(tornado.escape.json_encode(bookmark_urls))
        self.set_header('content-type', 'application/json')

    @tornado.web.authenticated
    def get(self):
        return self.get_or_post()

    @tornado.web.authenticated
    def post(self):
        return self.get_or_post()


import urllib


class SearchHandler(BookmarksSearchJSONHandler):
    template_path = 'search.jinja'

    def get_or_post(self):
        kwargs = self.get_search_arguments(self)
        dest = self.get_argument('dest', default='html')
        queryurl = '/q.json?' + urllib.urlencode(kwargs)
        if dest == 'json':
            self.redirect(queryurl)
        elif dest == 'brw':
            self.redirect('/static/brw/brw2.html#!' + queryurl)
        else:
            iterable = self.iter_search(self, iter(self.cb), **kwargs)
            t = utils.get_template(self.template_path)
            form_values = kwargs.copy()
            form_values['dest'] = dest
            htmlstr = t.render({
                'current_user': self.current_user,
                'bookmarks_iter': iterable,
                'form_values': form_values,
                'queryurl': queryurl,
                'range': range})
            self.write(htmlstr)

    @tornado.web.authenticated
    def get(self):
        return self.get_or_post()

    @tornado.web.authenticated
    def post(self):
        return self.get_or_post()


class BookmarksListHandler(BookmarksBaseHandler):
    template_path = 'bookmarks_list_partial.jinja'

    @tornado.web.authenticated
    def get(self):
        t = utils.get_template(self.template_path)
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
    template_path = 'bookmarks_tree_partial.jinja'

    @tornado.web.authenticated
    def get(self):
        t = utils.get_template(self.template_path)
        htmlstr = t.render({
            'bookmarks': self.cb,
            'bookmarks_iter': iter(self.cb),
            'format_longdate': format_longdate,
            'rdf_uri_escape': rdf_uri_escape})
        self.write(htmlstr)


class BookmarksHandler(BaseHandler):
    template_path = 'bookmarks.jinja'

    @tornado.web.authenticated
    def get(self):
        t = utils.get_template(self.template_path)
        htmlstr = t.render()
        self.write(htmlstr)

class BrwHandler(BaseHandler):
    template_path = 'brw.jinja'

    @tornado.web.authenticated
    def get(self):
      t = utils.get_template(self.template_path)
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
            os.path.dirname(__file__), '..', 'tests', 'data', 'Bookmarks'),

        # jinja2 (jinja_tornado)
        'template_path': os.path.join(
            os.path.dirname(__file__), 'templates'),
        'auto_reload': True,  # TODO: DEBUG
        'cache_size': 50,
        'autoescape': True
    })
    if config is not None:
        _conf.update(config)

    _conf['cb'] = pbm.main.ChromiumBookmarks(
        _conf['bookmarks_file'])

    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/about", AboutHandler),
        (r"/login", LoginHandler),
        (r"/logout", LogoutHandler),
        (r"/brw", BrwHandler),
        (r"/bookmarks", BookmarksHandler),
        (r"/bookmarks/chrome", BookmarksHandler),
        (r"/bookmarks/chrome/json", BookmarksJSONHandler),
        (r"/bookmarks/chrome/links.json", BookmarksLinksJSONHandler),
        (r"/bookmarks/chrome/search.json", BookmarksSearchJSONHandler),
        (r"/q.json", BookmarksSearchJSONHandler),
        (r"/search", SearchHandler),
        (r"/bookmarks/chrome/list", BookmarksListHandler),
        (r"/bookmarks/chrome/tree", BookmarksTreeHandler),
    ], **_conf)

    environment = JinjaApp.init_app(application)  # jinja_tornado

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
                   action='store',
                   help='default: localhost')
    prs.add_option('-P', '--port',
                   dest='port',
                   default='28881',
                   action='store',
                   help='default: 28881')

    prs.add_option('-o', '--open', '--open-browser',
                   dest='open_browser',
                   action='store_true',
                   help='Open a webbrowser to the pbmweb URL')

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
    if opts.open_browser:
        conf['open_browser'] = True
    app = make_app(conf)

    import tornado.httpserver
    try:
        url = 'http://{0.host}:{0.port}/'.format(opts)
        log.info("Serving at url: %s" % url)
        log.info("Conf:\%s", json.dumps(conf, indent=2))

        server = tornado.httpserver.HTTPServer(app)
        server.bind(opts.port, address=opts.host)
        server.start(n_procs)  # forks one process per cpu

        if conf.get('open_browser', None) is not None:
            import subprocess
            import sys
            cmd = [sys.executable, '-m', 'webbrowser', '-t']
            #subprocess.Popen(cmd)
            #webbrowser.open_new_tab(url)
            import os
            cmd = ' '.join(cmd) + ' ' + repr(url) + ' &'
            print(cmd)
            #os.system(cmd)
            subprocess.Popen(cmd, shell=True)
            log.info("Opened browser to: %s" % url)

        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.current().stop()
        server.stop()


    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main(argv=sys.argv[1:]))
