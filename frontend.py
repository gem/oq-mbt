import os
import sys
import gc
from IPython.display import HTML
from IPython.display import display, clear_output
from IPython.core.getipython import get_ipython

from ipywidgets import widgets

# from mtk_comm import (g_message, mtk_comm.GEM_MATRIPY_HOME, GEM_MATRIPY_SFX)
import mtk_comm

from project import Project

#text = widgets.Text()
#display(text)

#def handle_submit(sender):
#    print(text.value)
#
#text.on_submit(handle_submit)
# from IPython.display import display

g_prj = None


class NewProjectMenu(object):
    _instance = None

    def __new__(cls, *args, **kargv):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kargv)
            cls._instance._is_inited = False
            cls._instance.box = None
        return cls._instance

    @staticmethod
    def _create_cb(btn):
        global g_prj
        name = btn._gem_context.text.value
        newdir = os.path.join(mtk_comm.GEM_MATRIPY_HOME,
                              name
                              + mtk_comm.GEM_MATRIPY_SFX)
        if os.path.isdir(newdir):
            mtk_comm.g_message.value = "'%s' project already exists" % name
            return

        try:
            os.mkdir(newdir)
        except:
            mtk_comm.g_message.value = "'%s' project creation failed" % name
            return

        mtk_comm.g_message.value = "'%s' project created" % name
        g_prj.title_set(name)
        g_prj.show()
        btn._gem_context.destroy()
        del btn._gem_context

    @staticmethod
    def _close_cb(btn):
        # print "close_cb"
        btn._gem_context.destroy()
        del btn._gem_context

    def __init__(self, siblings, box, *args):
        mtk_comm.g_message.value = ''
        for sibling in siblings:
            if sibling == type(self).__name__:
                continue
            getattr(getattr(sys.modules[__name__], sibling),
                    "instance_reset")()

        if self._instance._is_inited:
            return

        self.text = widgets.Text(description='Name: ', margin="8px")
        self.create = widgets.Button(description='Create', margin="8px")
        self.create._gem_context = self
        self.create.on_click(self._create_cb)

        self.close = widgets.Button(description='Close', margin="8px")
        self.close._gem_context = self
        self.close.on_click(self._close_cb)
        # self.close.on_click(self._close_cb)
        self.box = widgets.Box(children=[self.text, self.create, self.close],
                               border_style="solid", border_width="1px",
                               border_radius="8px", width="400px")
        box.children = (self.box,)
        self._instance._is_inited = True

    @classmethod
    def instance_set(cls, value):
        cls._instance = value

    @classmethod
    def instance_reset(cls):
        if cls._instance is not None:
            if cls._instance.box is not None:
                cls._instance.box.close()
                cls._instance.box = None
            cls._instance = None

    def destroy(self):
        if self.box is not None:
            self.box.close()
            self.box = None
        self.instance_reset()


class LoadProjectMenu(object):
    _instance = None

    def __new__(cls, *args, **kargv):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kargv)
            cls._instance._is_inited = False
            cls._instance.box = None
        return cls._instance

    @staticmethod
    def _load_cb(btn):
        global g_prj

        g_prj.load(btn._gem_context.ddown.value)
        g_prj.show()

        btn._gem_context.destroy()
        del btn._gem_context

    @staticmethod
    def _close_cb(btn):
        # print "close_cb"
        btn._gem_context.destroy()
        del btn._gem_context

    def __init__(self, siblings, box, *args):
        mtk_comm.g_message.value = ''
        for sibling in siblings:
            if sibling == type(self).__name__:
                continue
            getattr(getattr(sys.modules[__name__], sibling),
                    "instance_reset")()

        if self._instance._is_inited:
            return

        self.load = widgets.Button(description='Load', margin="8px")
        self.load._gem_context = self
        self.load.on_click(self._load_cb)

        self.close = widgets.Button(description='Close', margin="8px")
        self.close._gem_context = self
        self.close.on_click(self._close_cb)

        for (_, all_dirs, _) in os.walk(mtk_comm.GEM_MATRIPY_HOME):
            break

        prjs = [x for x in all_dirs if x.endswith(mtk_comm.GEM_MATRIPY_SFX)]
        prjs_items = {}
        for prj in prjs:
            prjs_items[prj[:-4]] = prj
        self.ddown = widgets.Dropdown(
            options=prjs_items,
            description='Projects:',
            margin="8px"
        )

        self.box = widgets.Box(children=[self.ddown, self.load, self.close],
                               border_style="solid", border_width="1px",
                               border_radius="8px", width="400px")
        box.children = (self.box,)
        self._instance._is_inited = True

    @classmethod
    def instance_set(cls, value):
        cls._instance = value

    @classmethod
    def instance_reset(cls):
        if cls._instance is not None:
            if cls._instance.box is not None:
                cls._instance.box.close()
                cls._instance.box = None
            cls._instance = None

    def destroy(self):
        if self.box is not None:
            self.box.close()
            self.box = None
        self.instance_reset()


def ExportProject(siblings, box, btn):
    for sibling in siblings:
        getattr(getattr(sys.modules[__name__], sibling),
                "instance_reset")()


def main():
    global g_prj
    display(HTML('''<script>
    code_show=true;
    function code_toggle() {
     if (code_show){
     $('div.input').hide();
     } else {
     $('div.input').show();
     }
     code_show = !code_show
    }
    $( document ).ready(code_toggle);
    </script>
    <a href="javascript:code_toggle()">Source toggle.</a>''')) 

    if 'GEM_MATRIPY_HOME' in os.environ:
        mtk_comm.GEM_MATRIPY_HOME = os.environ['GEM_MATRIPY_HOME']
    else:
        from os.path import expanduser
        mtk_comm.GEM_MATRIPY_HOME = expanduser("~") + '/.matripyoska'
        os.environ['GEM_MATRIPY_HOME'] = mtk_comm.GEM_MATRIPY_HOME

    if not os.access(mtk_comm.GEM_MATRIPY_HOME, os.W_OK):
        print "Projects directory [%s] access denied." % mtk_comm.GEM_MATRIPY_HOME
        raise os.PermissionError

    # message widget
    mtk_comm.g_message = widgets.HTML(read_only=True, width="800px",
                             height="2em")
    display(mtk_comm.g_message)

    prj_siblings = ['NewProjectMenu', 'LoadProjectMenu']

    menubox = widgets.Box(children=[])

    new_prj = widgets.Button(description='New Project', margin="4px")
    new_prj.on_click(lambda btn: NewProjectMenu(prj_siblings, menubox, btn))

    load_prj = widgets.Button(description='Load Project', margin="4px")
    load_prj.on_click(lambda btn: LoadProjectMenu(prj_siblings, menubox, btn))

    export_prj = widgets.Button(description='Export Project', margin="4px")
    export_prj.on_click(lambda btn: ExportProject(prj_siblings, menubox, btn))

    box = widgets.HBox(children=[new_prj, load_prj, export_prj])

    vbox = widgets.VBox(children=[box, menubox])
    display(vbox)

    g_prj = Project()

