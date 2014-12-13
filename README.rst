===============================
promiumbookmarks
===============================

.. image:: https://badge.fury.io/py/promiumbookmarks.png
    :target: http://badge.fury.io/py/promiumbookmarks

.. image:: https://travis-ci.org/westurner/promiumbookmarks.png?branch=master
        :target: https://travis-ci.org/westurner/promiumbookmarks

.. image:: https://pypip.in/d/promiumbookmarks/badge.png
        :target: https://pypi.python.org/pypi/promiumbookmarks


promiumbookmarks works with Chromium bookmarks JSON

* Free software: BSD license

.. * Documentation: https://promiumbookmarks.readthedocs.org.

Features
--------

* List Chrome and Chromium Bookmarks JSON files (``-l`` / ``-L``)
* Print all bookmarks (``--print-all``)
* Reorganize bookmarks into date-based folders in the Bookmarks Bar
  (``--by-date``, ``--overwrite``)
* Add default folders:

  * ``2014`` -- year, year-month, year-month-day folders
  * ``bookmarklets`` -- Bookmarklets (will be merged with a default set)
  * ``chrome`` -- Select ``chrome://`` URLs
  * ``quicklinks`` -- Custom quicklinks (optional; will not be modified)
  * ``queue`` -- default folder for new bookmarks
