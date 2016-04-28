.. :changelog:

History
=======





release/0.6.2 (2016-04-28 18:16:24 -0500)
-----------------------------------------
::

   git log --reverse --pretty=format:'* %s [%h]' v0.6.1..release/0.6.2

* MRG: Merge tag 'v0.6.1' into develop [f69ab60]
* BUG,BLD: setup.py: install_requires jinja_tornado [189210d]
* BLD: src/jinja_tornado: upgrade [850198b]
* RLS: setup.py, __init__: v0.6.2 [5298786]


v0.6.1 (2016-04-28 16:28:14 -0500)
----------------------------------
::

   git log --reverse --pretty=format:'* %s [%h]' v0.6.0..v0.6.1

* MRG: Merge tag 'v0.6.0' into develop [c74bd7f]
* BUG,DOC: HISTORY.rst: escape \* [d14de7c]
* BLD: MANIFEST.in: recursive-include pbm/static *.html *.js [bd07338]
* BLD: Makefile: release w/ twine because HTTPS [56a72d3]
* RLS: setup.py, __init__: v0.6.1 [511ee6a]
* DOC: HISTORY.rst: 'git-changelog.py -r release/0.6.1 --hdr=- | pbcopy' [d884851]
* MRG: Merge branch 'release/0.6.1' [d5ddf17]


v0.6.0 (2016-04-28 16:11:26 -0500)
----------------------------------
::

   git log --reverse --pretty=format:'* %s [%h]' v0.5.3..v0.6.0

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
* DOC: HISTORY.rst: 0.6.0 [467eef1]
* RLS: setup.py, __init__.py: v0.6.0 [d8191b5]
* UBY: index.html: css [c44144f]
* MRG: Merge branch 'develop' of https://github.com/westurner/pbm into develop [df28218]
* BLD: src/jinja_tornado: upgrade [656c89d]
* BLD: pbm/static/brw: upgrade [a782e17]
* RLS: setup.py, __init__: v0.6.0 [dfa0da9]
* MRG: Merge branch 'release/0.6.0' of ssh://github.com/westurner/pbm into release/0.6.0 [60875ae]
* DOC: HISTORY.rst: 'git-changelog.py -r release/0.6.0 --hdr=- | pbcopy' [5345b84]
* MRG: Merge branch 'release/0.6.0' [73af3ea]


v0.5.3 (2015-04-23 21:12:41 -0500)
----------------------------------
::

   git log --reverse --pretty=format:'* %s [%h]' v0.5.2..v0.5.3

* Merge tag 'v0.5.2' into develop [c7d528f]
* BUG: app.py: main argv handling, logging [21a669e]
* DOC: v0.5.3 docs, version [cf2e2ee]
* Merge branch 'release/0.5.3' [ff5b2bd]


v0.5.2 (2015-04-23 20:53:01 -0500)
----------------------------------
::

   git log --reverse --pretty=format:'* %s [%h]' v0.5.1..v0.5.2

* Merge tag 'v0.5.1' into develop [b2f5992]
* DOC: __init__.py, setup.py, HISTORY.rst: v0.5.2 [0cb8e87]
* Merge branch 'release/0.5.2' [cfeed42]


v0.5.1 (2015-04-23 20:47:26 -0500)
----------------------------------
::

   git log --reverse --pretty=format:'* %s [%h]' v0.5.0..v0.5.1

* Merge tag 'v0.5.0' into develop [0ecf417]
* DOC: HISTORY.rst: v0.5.0, [a1111d4]
* DOC: README.rst [b6ac7ee]
* BUG,TST,REF: generate longdates, regular imports, test that queue['id'] is the max [fb1ab15]
* DOC: HISTORY.rst: v0.5.1 [ad04316]
* RLS: __init__.py: version v0.5.1 [a84d4e2]
* Merge branch 'release/0.5.1' [4cda097]


v0.5.0 (2015-04-23 15:05:47 -0500)
----------------------------------
::

   git log --reverse --pretty=format:'* %s [%h]' v0.4.1..v0.5.0

* ENH: main.py: Add --print-all output formatter [016a601]
* BUG,ENH: main.py encoding errors w/ getwriter, print_json_link_list [f26b867]
* ENH,TST: print_html_tree, tornado app, recursive RDFa template (todo: simplify) [102c5c8]
* ENH: /bookmarks (jstree, /bookmarks/dict), /bookmarks/list [4bea937]
* BUG: make window.open work with middle-click [4e7673d]
* ENH,REF,CLN: JSON handlers, ##searchterm! onhashchanged, css, [markdown](url://formatting) [578c0ff]
* BUG,REF: onhashchange sync ('bindings'), css [8145dc6]
* TST: tests/test_app.py: tornado.testing.AsyncHTTPTestCase [ba24573]
* REF: /bookmarks -> /bookmarks/chrome [ac47841]
* TST,REF: main function signature, explicit stdout, q [19f50a8]
* BUG: main() argv must default to sys.argv[1:] for console_script [3ee4438]
* TST: tests/data: current output [0b2384f]
* REF: utils.get_template, imports [3cfbaca]
* REF: -> pbm [c1e292e]
* REF: -> pbm [9d57407]
* REF: -> pbm [6481879]
* REF: -> pbm [abae5ed]
* RLS: setup.py, __init__.py: v0.5.0 [ab5e5e3]
* Merge branch 'release/0.5.0' [c6096e8]


v0.4.1 (2015-03-02 04:24:00 -0600)
----------------------------------
::

   git log --reverse --pretty=format:'* %s [%h]' v0.4.0..v0.4.1

* Merge tag 'v0.4.0' into develop [604f9d3]
* BLD: MANIFEST.in: exclude .ropeproject and .bak [86a9090]
* RLS: HISTORY.txt: v0.4.1 release notes [a93991d]
* BLD,CLN: MANIFEST.in, Makefile: clean [3617d0c]
* RLS: HISTORY.txt: v0.4.1 release notes [2c0300f]
* RLS: setup.py: v0.4.1 [2990c02]
* Merge branch 'release/v0.4.1' [f9a5a67]
* Merge tag 'vv0.4.1' into develop [357d223]


v0.4.0 (2015-03-02 04:11:08 -0600)
----------------------------------
::

   git log --reverse --pretty=format:'* %s [%h]' v0.3.0..v0.4.0

* Merge tag 'v0.3.0' into develop [08b5088]
* BLD: Makefile: make test -> nosetests ./tests/test_promiumbookmarks.py [c934e99]
* BUG: promiumbookmarks.plugins.PromiumPlugin: accept a conf={} argument [261a855]
* TST: test_promiumbookmarks: remove import of promiumbookmarks.plugins.other [91d8132]
* REF: promiumbookmarks/promiumbookmarks.py: factor BookmarksObject back into ChromiumBookmarks [4df13c9]
* DOC: promiumbookmarks.ChromiumBookmarks.walk_bookmarks: docstring [780da1f]
* BUG: promiumbookmarks.ChromiumBookmarks.bookmarks_list: bookmarks_list consume the iterable [1d1ab48]
* CLN: dbf plugin: cleanup and simplify [26e3c07]
* ENH: bookmarkletsfolder.py: add "notetab (800px)" bookmarklet (closes #2) [53582c9]
* BUG: promiumbookmarks.ChromiumBookmarks.walk_bookmarks: pass filterfunc through [ee41454]
* TST: tests/data/Bookmarks: set date_added to a nonzero date [c88f78b]
* BUG: set date_added to a nonzero date [326c4fe]
* ENH: Add plugins.DedupePlugin to deduplicate bookmarks on (url, date_added) [9369891]
* TST: Bookmarks [1620af5]
* TST: tests/data/Bookmarks: add starred, queued [ca7278e]
* DOC: README.rst: fix title underline [5c8dc9f]
* REF: promiumbookmarks.plugins plugin API [773ff26]
* ENH: plugins.starred: O instead of # (searchable) [aa95b9c]
* ENH: plugins.starred: prefix with X [783411d]
* BLD: Makefile: check readme syntax [1309ac4]
* RLS: HISTORY.txt: v0.4.0 release notes [39ef2b2]
* Merge branch 'release/0.4.0' [ca63866]


v0.3.0 (2015-02-08 02:50:29 -0600)
----------------------------------
::

   git log --reverse --pretty=format:'* %s [%h]' v0.2.5..v0.3.0

* Merge tag 'v0.2.5' into develop [2a1cfaa]
* CLN,ENH: refactoring, initial plugin support [aaf96dc]
* CLN: auto-lint [1b25145]
* ENH: refactor to plugins, move tests to test_promiumbookmarks.py, add allinone and starred plugins [67dc734]
* Merge with 0.2.5 [4dca76e]
* DOC: README.rst, HISTORY.rst: headings [5f0a8a1]
* RLS: setup.py: version 0.3.0 [b191c91]
* Merge branch 'release/0.3.0' [fcd8496]


v0.2.5 (2014-12-25 08:18:16 -0600)
----------------------------------
::

   git log --reverse --pretty=format:'* %s [%h]' v0.2.4..v0.2.5

* Merge tag 'v0.2.4' into develop [0a7ca31]
* BUG: Add support for "linux2" platform [eb7621d]
* RLS: setup.py, HISTORY.rst: v0.2.5 [6057e77]
* Merge branch 'release/0.2.5' [59df7fe]


v0.2.4 (2014-12-13 17:58:55 -0600)
----------------------------------
::

   git log --reverse --pretty=format:'* %s [%h]' v0.2.3..v0.2.4

* Merge tag 'v0.2.3' into develop [52555ac]
* DOC: pip install -e git+, Bookmarks Bar Folders RST Table (Riv.vim) [ad01158]
* RLS: version=0.2.4, keywords [7f1b08d]
* DOC: README.rst: Bookmarks Bar Folders table (Riv.vim) [fa12164]
* Merge branch 'release/0.2.4' [a582d44]


v0.2.3 (2014-12-13 17:37:45 -0600)
----------------------------------
::

   git log --reverse --pretty=format:'* %s [%h]' v0.2.2..v0.2.3

* Merge tag 'v0.2.2' into develop [adfe382]
* DOC: README.rst: https://pypi.python.org/pypi/promiumbookmarks [e5f6464]
* RLS: setup.py version=0.2.3 [2e36d52]
* Merge branch 'release/0.2.3' [7251ab5]


v0.2.2 (2014-12-13 17:33:12 -0600)
----------------------------------
::

   git log --reverse --pretty=format:'* %s [%h]' v0.2.1..v0.2.2

* Merge tag 'v0.2.1' into develop [d2390e9]
* BLD: MANIFEST.in: exclude tests/data/\*.bkp [634235a]
* RLS: setup.py version=0.2.2 [85b111e]
* Merge branch 'release/0.2.2' [92b79d9]


v0.2.1 (2014-12-13 17:27:52 -0600)
----------------------------------
::

   git log --reverse --pretty=format:'* %s [%h]' v0.2.0..v0.2.1

* Merge tag 'v0.2.0' into develop [b8e1f96]
* RLS,DOC,CLN: setup.py description, classifiers, README.rst, HISTORY.rst, .gitignore [8e2e0c6]
* Merge branch 'release/0.2.1' [dc8465a]


v0.2.0 (2014-12-13 17:10:04 -0600)
----------------------------------
::

   git log --reverse --pretty=format:'* %s [%h]' 0677946..v0.2.0

* CLN: plain refactor into ChromiumBookmarks(object) [9eef12b]
* ENH: Add ChromiumBookmarks.__init__, __iter__ and ChromiumBookmarks.reorganized [6cc0635]
* CLN: -> ChromiumBookmarks.reorganize_by_date [648f64e]
* CLN: update .gitignore [aa4bd44]
* ENH,DOC: CLI actions and options [8384381]
* CLN: move to chromium_bookmarks.py [5e9d0e6]
* CLN: pep8, lint, rename to chromium_bookmarks.py [2847bfd]
* BLD: Update Makefile [745b370]
* ENH: Add chrome://history and chrome://bookmarks links to bookmarks bar [cf12e50]
* ENH,DOC: bookmarklets, chrome:// URIs, docstrings, filterfunc param [05c7634]
* ENH,CLN: Add 'quicklinks' Bookmarks Bar folder passthrough [1d49949]
* ENH,BUG: date-based backups, merge defaults into 'bookmarklets', add a default 'queue' folder, filterfunc passthrough [577cd1c]
* PRF: optimize chrome_filterfunc [522a3e6]
* TST: test filenames, assertRaises(IOError) if ./Bookmarks does not exist [ac68e3e]
* BLD,CLN: Makefile, chromium_bookmarks.py -> promiumbookmarks.py [21d6dd1]
* CLN: chromium_bookmarks.py -> promiumbookmarks.py [6ce5194]
* CLN: .gitignore [87e0962]
* ENH: -l/-L to list Bookmarks [5090209]
* TST: Update test Bookmarks [fb0e632]
* ENH: get_chromedir, get_chromiumdir for (platform, release) [4d423d1]
* BLD: promiumbookmarks.py -> promiumbookmarks/promiumbookmarks.py [6655625]
* BLD: Add templated cookiecutter-pypackage [5038500]
* BLD: Makefile: merge with cookiecutter [57ce9dd]
* DOC: README.rst: Feature descriptions [a65ce02]
* BLD: setup.py: promiumbookmarks console_script entrypoint [935aaa5]
* DOC: README.rst: comment out travis badge for now [e3ea2b4]
* DOC: README.rst: feature descriptions [91d304f]
* DOC: README.rst: feature descriptions [886126d]
* DOC: README.rst: feature descriptions [2c53107]
* DOC: README.rst: Installation, Usage [5267be5]
* RLS: setup.py: version=0.2.0 [a06a2a2]
* Merge branch 'release/0.2.0' [87eece7]

