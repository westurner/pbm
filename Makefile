
.PHONY: default test nosetest \
	debug rebuild ls-profiles \
	rebuild print-all print-by-date

#PROFILE_NAME:="Default"
#PROFILE_NAME:="Profile\ 1"
CHROMEDIR=$${HOME}/Library/Application\ Support/Google/Chrome
CHROMEPROFILE=$(CHROMEDIR)/$(PROFILE_NAME)
CHROMEBOOKMARKS=$(CHROMEPROFILE)/Bookmarks

default: test

test:
	python ./chromium_bookmarks.py -t

nosetest:
	nosetests --with-coverage ./chromium_bookmarks.py


debug:
	@echo "---"
	$(MAKE) ls-profiles
	@echo "---"
	@echo $(PROFILE_NAME)
	@echo $(CHROMEPROFILE)
	ls $(CHROMEPROFILE)

ls-profiles:
	ls -l $(CHROMEDIR)/*/Bookmarks

rebuild:
	python ./chromium_bookmarks.py --overwrite $(CHROMEBOOKMARKS)

print-all:
	python ./chromium_bookmarks.py --print-all $(CHROMEBOOKMARKS)

print-by-date:
	python ./chromium_bookmarks.py --by-date $(CHROMEBOOKMARKS)
