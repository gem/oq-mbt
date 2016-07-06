import os
from os.path import expanduser
from ipywidgets import widgets
from IPython.display import display

#
#  GLOBALS
#
# projects path
OQ_MBT_HOME = None
OQ_MBT_DATA = None
OQ_MBT_SFX = '_mbt'

# message text widget handle
g_message = None


class Bunch(object):
    def __init__(self, **kw):
        vars(self).update(kw)


def message_set(msg):
    if g_message is not None:
        g_message.value = msg


def message_show():
    display(g_message)


def accordion_title_find(accord, name):
    for i in range(0, len(accord.children)):
        if accord.get_title(i) == name:
            return i
    return -1


def init():
    global OQ_MBT_HOME, OQ_MBT_DATA, g_message

    if 'OQ_MBT_HOME' in os.environ:
        OQ_MBT_HOME = os.environ['OQ_MBT_HOME']
    else:
        OQ_MBT_HOME = os.path.join(expanduser("~"), '.oq_mbt')
        os.environ['OQ_MBT_HOME'] = OQ_MBT_HOME

    if not os.access(OQ_MBT_HOME, os.W_OK):
        print "Projects directory [%s] access denied." % OQ_MBT_HOME
        raise os.PermissionError

    if 'OQ_MBT_DATA' in os.environ:
        OQ_MBT_DATA = os.environ['OQ_MBT_DATA']
    else:
        OQ_MBT_DATA = expanduser("~")

    # message widget
    g_message = widgets.HTML(read_only=True, width="800px",
                             height="2em")
