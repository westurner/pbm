default: test

test:
	python ./parse_bookmarks.py -t

nosetest:
	nosetests --with-coverage ./parse_bookmarks.py
