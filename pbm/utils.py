# utility functions (seeAlso: six, nine):

import datetime
import os.path
import sys

import jinja2

if sys.version_info.major > 2:
    long = int

DATETIME_CONST = 2**8 * 3**3 * 5**2 * 79 * 853


def longdate_to_datetime(t_long):
    if t_long is None:
        return
    t_long = long(t_long)
    timestamp = (t_long * 1e-6) - DATETIME_CONST
    if timestamp < 0:
        return
    return datetime.datetime.utcfromtimestamp(timestamp)


def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()


def datetime_to_longdate(dt):
    return (unix_time(dt) + DATETIME_CONST) * 1000000.0


def get_datetime_now_longdate(dt=None):
    if dt is None:
        dt = datetime.datetime.now()
    return datetime_to_longdate(dt)



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


def get_template(template):
    loader = jinja2.FileSystemLoader(
        os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
            'templates'))
    env = jinja2.Environment(loader=loader, autoescape=True)
    tmpl = loader.load(env, template)
    return tmpl
