#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'jinja2'
]

test_requirements = [
    'tornado',
    'jinja2'
]

setup(
    name='pbm',
    version='0.5.2',
    description=(
        'pbm works with Chrome and Chromium bookmarks JSON.'),
    long_description=readme + '\n\n' + history,
    author='Wes Turner',
    author_email='wes@wrd.nu',
    url='https://github.com/westurner/pbm',
    packages=[
        'pbm',
    ],
    package_dir={'pbm':
                 'pbm'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='pbm bookmarks chrome chromium',
    classifiers=[
        "Programming Language :: Python :: 2",
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Browsers',
        'Topic :: Utilities',

    ],
    entry_points="""
    [console_scripts]
    pbm = pbm.main:main
    pbmweb = pbm.app:main

    [pbm_plugins]
    null = pbm.plugins.null:NullPlugin
    allinone = pbm.plugins.allinone:AdditionalAllFolderPlugin
    bookmarkletsfolder = pbm.plugins.bookmarkletsfolder:BookmarkletsFolderPlugin
    chromefolder = pbm.plugins.chromefolder:ChromeFolderPlugin
    datefolder = pbm.plugins.datefolders:DateFolderPlugin
    dedupe = pbm.plugins.dedupe:DedupePlugin
    queuefolder = pbm.plugins.queuefolder:QueueFolderPlugin
    quicklinks = pbm.plugins.quicklinks:QuicklinksFolderPlugin
    starred = pbm.plugins.starred:StarredFolderPlugin
    """,
    test_suite='tests',
    tests_require=test_requirements
)
