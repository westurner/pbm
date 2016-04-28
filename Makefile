
.PHONY: clean-pyc clean-build docs clean \
	default test nosetest \
	debug rebuild ls-profiles \
	rebuild print-all print-by-date

default: test

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "dist - package"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	find . -name '.ropeproject' -print0 | xargs rm -rfv

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint:
	flake8 pbm tests

test:
	# python setup.py test
	#$(PROMIUMBOOKMARKS) -t
	nosetests ./tests/test_pbm.py ./tests/test_app.py

nosetest:
	nosetests --with-coverage ./pbm.py

test-all:
	tox

coverage:
	coverage run --source pbm setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

docs:
	rm -f docs/pbm.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ pbm
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

test-readme:
	pip install readme
	python setup.py check -r -s

build: clean test-readme
	python setup.py build

dist: build
	python setup.py sdist bdist_wheel
	ls -l dist

release: clean test-readme dist
	twine upload dist/*

# pbm Makefile
##############################################################################

UNAME_S:=$(shell uname -s)

#PROFILE_NAME:="Default"
PROFILE_NAME:=Profile\ 1

#CHROMIUM_DIR  (see also: $(pbm -l))  [make ls]
ifeq ($(UNAME_S),Linux)
CHROMIUM_DIR=$${HOME}/.config/google-chrome
endif
ifeq ($(UNAME_S),Darwin)
CHROMIUM_DIR=$${HOME}/Library/Application\ Support/Google/Chrome
endif

CHROMIUM_PROFILE=$(CHROMIUM_DIR)/$(PROFILE_NAME)
CHROMIUM_BOOKMARKS=$(CHROMIUM_PROFILE)/Bookmarks

PROMIUMBOOKMARKS=./pbm/main.py

debug:
	@echo "---"
	$(MAKE) ls-profiles
	@echo "---"
	@echo $(PROFILE_NAME)
	@echo $(CHROMIUM_PROFILE)
	ls $(CHROMIUM_PROFILE)

ls-profiles:
	$(PROMIUMBOOKMARKS) -l

l: ls-profiles
ls: ls-profiles

rebuild:
	$(PROMIUMBOOKMARKS) --overwrite $(CHROMIUM_BOOKMARKS)

print-all:
	$(PROMIUMBOOKMARKS) --print-all $(CHROMIUM_BOOKMARKS)

print-by-date:
	$(PROMIUMBOOKMARKS) --by-date $(CHROMIUM_BOOKMARKS)
