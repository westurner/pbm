===============================
pbm
===============================

.. image:: https://badge.fury.io/py/pbm.png
    :target: http://badge.fury.io/py/pbm

.. .. image:: https://travis-ci.org/westurner/pbm.png?branch=master
..        :target: https://travis-ci.org/westurner/pbm

.. image:: https://pypip.in/d/pbm/badge.png
        :target: https://pypi.python.org/pypi/pbm


pbm works with Chrome and Chromium bookmarks JSON.

* Free software: BSD license
* Source: https://github.com/westurner/pbm
* PyPI: https://pypi.python.org/pypi/pbm

.. * Documentation: https://pbm.readthedocs.org.

Features
========

* List Chrome and Chromium Bookmarks JSON files (``-l`` / ``-L``)
* Print all bookmarks (``--print-all``)
* Reorganize all bookmarks into the Bookmarks Bar (``--organize``)
  

Bookmarks Bar Folders
-----------------------

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
| ``starred``      | bookmarks ending in one or more ``#`` are copied here       |
|                  | searchably prefixed with ``[XO]``, ``[XOOOO]``              |
+------------------+-------------------------------------------------------------+
| ``queue``        | default folder for new bookmarks                            |
+------------------+-------------------------------------------------------------+


Installation
==============
Install from PyPI with pip:

.. code:: bash

   pip install pbm

Development:

.. code:: bash

   pip install -e git+ssh://git@github.com/westurner/pbm#egg=pbm


Usage
=======
List available ``Bookmarks`` files in Chrome and Chromium User Data
directories:

.. code:: bash

   pbm -l  # or -L to also list Bookmarks.%FT%T%z.bkp backups

Reorganize all bookmarks into Bookmarks Bar folders:

.. code:: bash

   bmarks=$(pbm -l | grep "Profile 1" | head -n1)
   pbm --organize "${bmarks}"
