import os
from ipywidgets import widgets
from IPython.display import display

#
#  GLOBALS
#
# projects path
GEM_MATRIPY_HOME = None
GEM_MATRIPY_SFX = '_mbt'

# message text widget handle
g_message = None


class Bunch(object):
    def __init__(self, **kw):
        vars(self).update(kw)


def accordion_title_find(accord, name):
    for i in range(0, len(accord.children)):
        if accord.get_title(i) == name:
            return i
    return -1


def init():
    global GEM_MATRIPY_HOME, g_message

    if 'GEM_MATRIPY_HOME' in os.environ:
        GEM_MATRIPY_HOME = os.environ['GEM_MATRIPY_HOME']
    else:
        from os.path import expanduser
        GEM_MATRIPY_HOME = expanduser("~") + '/.matripyoska'
        os.environ['GEM_MATRIPY_HOME'] = GEM_MATRIPY_HOME

    if not os.access(GEM_MATRIPY_HOME, os.W_OK):
        print "Projects directory [%s] access denied." % GEM_MATRIPY_HOME
        raise os.PermissionError

    # message widget
    g_message = widgets.HTML(read_only=True, width="800px",
                             height="2em")
