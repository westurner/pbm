#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
]

test_requirements = [
]

setup(
    name='promiumbookmarks',
    version='0.2.3',
    description=(
        'promiumbookmarks works with Chrome and Chromium bookmarks JSON.'),
    long_description=readme + '\n\n' + history,
    author='Wes Turner',
    author_email='wes@wrd.nu',
    url='https://github.com/westurner/promiumbookmarks',
    packages=[
        'promiumbookmarks',
    ],
    package_dir={'promiumbookmarks':
                 'promiumbookmarks'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='promiumbookmarks',
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
    promiumbookmarks = promiumbookmarks.promiumbookmarks:main
    """,
    test_suite='tests',
    tests_require=test_requirements
)
