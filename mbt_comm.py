import os
import sys
from os.path import expanduser
from ipywidgets import widgets
from IPython.display import display, Javascript
#
#  GLOBALS
#
# projects path
OQ_MBT_HOME = None
OQ_MBT_DATA = None
OQ_MBT_SFX = '_mbt'

# message text widget handle
g_message = None

class StdoutToNull(object):
    def __init__(self, is_silent=True):
        self.is_silent = is_silent
        self.stdout = open(os.devnull, "w")

    def __enter__(self):
        if self.is_silent is False:
            return
        sys.stdout.flush()
        self.origin = sys.stdout
        sys.stdout = self.stdout

    def __exit__(self, type, value, traceback):
        if self.is_silent is False:
            return
        sys.stdout = self.origin
        self.stdout.close()

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


def metys_confirm(message, yes_cb, no_cb, context):
    wid_message = widgets.HTML(value=message, font_weight="bold")
    wid_yes = widgets.Button(description="YES")

    def close_widget(ctx):
        for wid in ctx.widgets:
            wid.close()

    def confirm_yes_cb(btn):
        ctx = btn._gem_ctx
        ctx.yes_cb(ctx.context)
        close_widget(ctx)

    def confirm_no_cb(btn):
        ctx = btn._gem_ctx
        ctx.no_cb(ctx.context)
        close_widget(ctx)

    wid_yes.on_click(confirm_yes_cb)
    wid_no = widgets.Button(description="NO")
    wid_no.on_click(confirm_no_cb)
    wid_yesno = widgets.HBox(children=[wid_yes, wid_no])
    wid_confirm_inner = widgets.VBox(children=[wid_message, wid_yesno])
    wid_confirm_inner.add_class('gem_confirm_inner')
    wid_confirm = widgets.HBox(children=[wid_confirm_inner])
    wid_confirm.add_class('gem_confirm')

    wid_no._gem_ctx = wid_yes._gem_ctx = Bunch(
        yes_cb=yes_cb, no_cb=no_cb, context=context,
        widgets=[wid_yes, wid_no, wid_yesno, wid_confirm_inner, wid_confirm])
    display(wid_confirm)


def init():
    global OQ_MBT_HOME, OQ_MBT_DATA, g_message

    if 'OQ_MBT_HOME' in os.environ:
        OQ_MBT_HOME = os.environ['OQ_MBT_HOME']
    else:
        OQ_MBT_HOME = os.path.join(expanduser("~"), '.oq_mbt')
        os.environ['OQ_MBT_HOME'] = OQ_MBT_HOME

    if not os.access(OQ_MBT_HOME, os.W_OK):
        raise OSError("Projects directory [%s] access denied." % OQ_MBT_HOME)

    if 'OQ_MBT_DATA' in os.environ:
        OQ_MBT_DATA = os.environ['OQ_MBT_DATA']
    else:
        OQ_MBT_DATA = expanduser("~")

    display(Javascript("""
        define('oq_getcells_module', [], function() {
            var oq_getcells_target = function (comm, msg) {
                comm.on_msg(function(m) {
                    var cells = IPython.notebook.get_cells();
                    var ret = [];
                    var ct = cells.length;
                    for (var i = 1 ; i < ct ; i++) {
                        ret.push({type: cells[i].cell_type, content: cells[i].get_text()});
                    }
                    comm.send(ret);
                });
            comm.on_close(function(m) {
                ;
                });
            }
            return {'oq_getcells_target': oq_getcells_target}
        })
    """))

    # message widget
    g_message = widgets.HTML(read_only=True, width="800px",
                             height="2em")
