# utility functions (seeAlso: six, nine):

if hasattr(dict, 'iteritems'):
    def itervalues(x):
        return x.itervalues()

    def iterkeys(x):
        return x.iterkeys()

    def iteritems(x):
        return x.iteritems()
else:
    def itervalues(x):
        return x.values()

    def iterkeys(x):
        return x.keys()

    def iteritems(x):
        return x.items()


def json_default(o):
    if hasattr(o, 'to_json'):
        return o.to_json()
    elif hasattr(o, '__dict__'):
        return o.__dict__
    else:
        return o

