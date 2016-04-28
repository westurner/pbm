.. :changelog:

History
=======

0.6.0 (2015-12-05)
-------------------

* Jinja2 templates, navlinks, CSS
* ``/about``
* ``--open``
* ``brw.jinja``

::

   git log --reverse --pretty=format:'* %s [%h]' v0.5.3..develop

* Merge tag 'v0.5.3' into develop [d330a7e]
* ENH: app.py: add HTTP_ACCESS_CONTROL_ALLOW_ORIGIN (optional CORS) [a17eb19]
* CLN: rm filenames ending with ' ' from sed -i' ' [17459bd]
* BLD: setup.py, requirements.txt: add tornado as a dependency (for pbmweb) [b670e1c]
* UBY: main.py: -y/--yes/--skip-prompt [91ff556]
* BUG: pbm/main.py: ./Bookmarks -> Bookmarks (toward path.py/pathlib compat) [47838d0]
* BLD: setup.py, requirements-test.txt: test deps: urlobject, rdflib [fb41197]
* DOC: setup.py: package description [6c934cc]
* TST,CLN: remove old /bookmarks/chrome/dict route [482f141]
* REF: app.py: cls.template_path [e77b2b2]
* BLD: pbm/static/brw: git submodule [1aa753f]
* ENH: templates/main.jinja: link to //static/brw/index.html [4aa0804]
* TST,UBY: pbm/main.py: logging.basicConfig(format=) [d50b31d]
* BLD: Makefile: UNAME_S:=$(shell uname -s) [2a70f57]
* CLN: .gitignore: add vim .swp, .swo [c177f25]
* ENH: views, /logout, navlinks, /about, --open [ba9f16b]
* BLD: pbm/static/brw: :fast_forward: to 3cb3d6f [4698efe]


0.5.3 (2015-04-23)
-------------------
* BUG: app.py: main argv handling, logging

0.5.2 (2015-04-23)
-------------------
* RLS: version v0.5.2

0.5.1 (2015-04-23)
-------------------
* BUG: main.py: don't call .get_ids() (queue folder id to max)
* BUG: \*: Fix id renumbering (Note: This is still relatively unsolved)
* BUG: utils.py: generate longdates
* TST: tests/test_pbm.py: test that queue['id'] is the max
* REF: \*: regular imports
* RLS: HISTORY.txt: v0.5.0, v0.5.1

0.5.0 (2015-04-23)
-------------------
* BUG: main.py: encoding errors when piping to e.g. cat (default: UTF-8)
* ENH: main.py: ``--print-json-link-list``
* ENH: main.py: ``--print-html-tree``
* ENH: main.py: ``--print-all``
* ENH: app.py: tornado app w/ stub login auth, csrf, secure cookies
* ENH: templates/bookmarks_list.jinja: HTML: ``/bookmarks/chrome/list``
* ENH: app.py: ``/bookmarks/chrome/json`` JSON (``~ cat ./Bookmarks``)
* ENH: templates/bookmarks.jinja: JS: ``/bookmarks/chrome`` jstree
* ENH: templates/bookmarks.jinja: JS: #searchterm! onhashchanged
* ENH: templates/bookmarks.jinja: CSS: Bootstrap
* ENH: templates/bookmarks.jinja: CSS: show a:visited
* ENH: templates/bookmarks.jinja: CSS: [markdown](url://formatting)
* ENH: templates/bookmarks_tree.jinja: HTML+RDFa: ``/bookmarks/chrome/tree`` recursive RDFa template
* REF: utils.get_template, imports
* TST,REF: main function signature, explicit stdout, q
* TST: tests/data: current output
* TST: tests/test_app.py: tornado.testing.AsyncHTTPTestCase
* REF: -> pbm

0.4.1 (2015-03-02)
-------------------
* BLD: Makefile, MANIFEST.in: rm .ropeproject, exclude.bak

0.4.0 (2015-03-02)
-------------------
* ENH: plugins.starred: prefix with X
* ENH: plugins.starred: O instead of # (searchable)
* REF: pbm.plugins plugin API
* ENH: add "notetab (800px)" bookmarklet

0.3.0 (2015-02-08)
-------------------

* ENH: Refactor to pbm.plugins
* TST: Move tests to tests/test_pbm.py
* DOC: README.rst, HISTORY.txt: headings

0.2.5 (2014-12-25)
-------------------

* BUG: Add support for "linux2" platform

0.2.4 (2014-12-13
------------------

* DOC: README.rst, setup.py: fix pip install editable command, keywords

0.2.3 (2014-12-13)
-------------------

* DOC: README.rst: link to PyPI package

0.2.2 (2014-12-13)
-------------------

* BLD: MANIFEST.in: ``exclude tests/data *.bkp``

0.2.1 (2014-12-13)
-------------------

* DOC: README.rst, setup.py: Update description and trove classifiers

0.2.0 (2014-12-13)
---------------------

* RLS: First release on PyPI
