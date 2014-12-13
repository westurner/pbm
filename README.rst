===============================
promiumbookmarks
===============================

.. image:: https://badge.fury.io/py/promiumbookmarks.png
    :target: http://badge.fury.io/py/promiumbookmarks

.. .. image:: https://travis-ci.org/westurner/promiumbookmarks.png?branch=master
..        :target: https://travis-ci.org/westurner/promiumbookmarks

.. image:: https://pypip.in/d/promiumbookmarks/badge.png
        :target: https://pypi.python.org/pypi/promiumbookmarks


promiumbookmarks works with Chrome and Chromium bookmarks JSON.

* Free software: BSD license
* Source: https://github.com/westurner/promiumbookmarks
* PyPI: https://pypi.python.org/pypi/promiumbookmarks

.. * Documentation: https://promiumbookmarks.readthedocs.org.

Features
--------

* List Chrome and Chromium Bookmarks JSON files (``-l`` / ``-L``)
* Print all bookmarks (``--print-all``)
* Reorganize all bookmarks into the Bookmarks Bar (``--overwrite``)
  

Bookmarks Bar Folders
~~~~~~~~~~~~~~~~~~~~~~~

+------------------+-------------------------------------------------------------+
|   Name           | Description                                                 |
+------------------+-------------------------------------------------------------+
| yearly           | date-based folders: ``YYYY`` > ``YYYY-MM`` > ``YYYY-MM-DD`` |
+------------------+-------------------------------------------------------------+
| ``bookmarklets`` | bookmarklets (additions will be merged with a default set)  |
+------------------+-------------------------------------------------------------+
| ``chrome``       | select ``chrome://`` URLs                                   |
+------------------+-------------------------------------------------------------+
| ``quicklinks``   | custom quicklinks (optional; copied as-is)                  |
+------------------+-------------------------------------------------------------+
| ``queue``        | default folder for new bookmarks                            |
+------------------+-------------------------------------------------------------+


Installation
--------------
Install from PyPI with pip:

.. code:: bash

   pip install promiumbookmarks

Development:

.. code:: bash

   pip install -e git+ssh://git@github.com/westurner/promiumbookmarks#egg=promiumbookmarks


Usage
-------
List available ``Bookmarks`` files in Chrome and Chromium User Data
directories:

.. code:: bash

   promiumbookmarks -l  # or -L to also list Bookmarks.%FT%T%z.bkp backups

Reorganize all bookmarks into Bookmarks Bar folders:

.. code:: bash

   promiumbookmarks --overwrite ./path/to/Bookmarks  # e.g. a path from -l
