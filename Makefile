default: test

test:
	python ./chromium_bookmarks.py -t

nosetest:
	nosetests --with-coverage ./chromium_bookmarks.py
