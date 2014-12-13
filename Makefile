
# promiumbookmarks Makefile

.PHONY: default test nosetest \
	debug rebuild ls-profiles \
	rebuild print-all print-by-date

default: test

test:
	python ./promiumbookmarks.py -t

nosetest:
	nosetests --with-coverage ./promiumbookmarks.py

##############################################################################

#PROFILE_NAME:="Default"
PROFILE_NAME:=Profile\ 1
CHROMIUM_DIR=$${HOME}/Library/Application\ Support/Google/Chrome
CHROMIUM_PROFILE=$(CHROMIUM_DIR)/$(PROFILE_NAME)
CHROMIUM_BOOKMARKS=$(CHROMIUM_PROFILE)/Bookmarks

debug:
	@echo "---"
	$(MAKE) ls-profiles
	@echo "---"
	@echo $(PROFILE_NAME)
	@echo $(CHROMIUM_PROFILE)
	ls $(CHROMIUM_PROFILE)

ls-profiles:
	ls -l $(CHROMIUM_DIR)/*/Bookmarks

rebuild:
	python ./promiumbookmarks.py --overwrite $(CHROMIUM_BOOKMARKS)

print-all:
	python ./promiumbookmarks.py --print-all $(CHROMIUM_BOOKMARKS)

print-by-date:
	python ./promiumbookmarks.py --by-date $(CHROMIUM_BOOKMARKS)
