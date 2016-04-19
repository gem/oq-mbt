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
