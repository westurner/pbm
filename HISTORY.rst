.. :changelog:

History
=======

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
