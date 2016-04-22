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
