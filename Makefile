
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
	flake8 promiumbookmarks tests

test:
	# python setup.py test
	$(PROMIUMBOOKMARKS) -t

nosetest:
	nosetests --with-coverage ./promiumbookmarks.py

test-all:
	tox

coverage:
	coverage run --source promiumbookmarks setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

docs:
	rm -f docs/promiumbookmarks.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ promiumbookmarks
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

# promiumbookmarks Makefile
##############################################################################

#PROFILE_NAME:="Default"
PROFILE_NAME:=Profile\ 1
CHROMIUM_DIR=$${HOME}/Library/Application\ Support/Google/Chrome
CHROMIUM_PROFILE=$(CHROMIUM_DIR)/$(PROFILE_NAME)
CHROMIUM_BOOKMARKS=$(CHROMIUM_PROFILE)/Bookmarks

PROMIUMBOOKMARKS=./promiumbookmarks/promiumbookmarks.py

debug:
	@echo "---"
	$(MAKE) ls-profiles
	@echo "---"
	@echo $(PROFILE_NAME)
	@echo $(CHROMIUM_PROFILE)
	ls $(CHROMIUM_PROFILE)

ls-profiles:
	$(PROMIUMBOOKMARKS) -l

rebuild:
	$(PROMIUMBOOKMARKS) --overwrite $(CHROMIUM_BOOKMARKS)

print-all:
	$(PROMIUMBOOKMARKS) --print-all $(CHROMIUM_BOOKMARKS)

print-by-date:
	$(PROMIUMBOOKMARKS) --by-date $(CHROMIUM_BOOKMARKS)
