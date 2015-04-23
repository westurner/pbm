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


import jinja2
import os.path


def get_template(template):
    env = jinja2.Environment(autoescape=True)
    loader = jinja2.FileSystemLoader(
        os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
            'templates'))
    tmpl = loader.load(env, template)
    return tmpl
