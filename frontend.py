import os
import sys
import gc
from IPython.display import HTML
from IPython.display import display
import json
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
g_prjbox = None

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
        global g_prj, g_prjbox
        name = btn._gem_ctx.text.value
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
        g_prj = Project([], [])
        g_prj.title_set(newdir, name)
        if g_prjbox is not None:
            g_prjbox.children = [g_prj.widget_get()]
        btn._gem_ctx.destroy()
        del btn._gem_ctx

    @staticmethod
    def _close_cb(btn):
        # print "close_cb"
        btn._gem_ctx.destroy()
        del btn._gem_ctx

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
        self.create._gem_ctx = self
        self.create.on_click(self._create_cb)

        self.close = widgets.Button(description='Close', margin="8px")
        self.close._gem_ctx = self
        self.close.on_click(self._close_cb)
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
        global g_prj, g_prjbox

        if g_prj:
            g_prj.clean()
            del g_prj

        g_prj = Project.load(btn._gem_ctx.ddown.value)
        # print g_prjbox
        if g_prjbox is not None:
            g_prjbox.children = [g_prj.widget_get()]

        btn._gem_ctx.destroy()
        del btn._gem_ctx

    @staticmethod
    def _close_cb(btn):
        # print "close_cb"
        btn._gem_ctx.destroy()
        del btn._gem_ctx

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
        self.load._gem_ctx = self
        self.load.on_click(self._load_cb)

        self.close = widgets.Button(description='Close', margin="8px")
        self.close._gem_ctx = self
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


def SaveProject(siblings, box, btn):
    filename = os.path.join(g_prj.folder, 'project.json')
    with open(filename, "w") as outfile:
        json.dump(g_prj.to_dict(), outfile, sort_keys=True, indent=4)

        mtk_comm.g_message.value = "'%s' project saved correctly" % filename

    for sibling in siblings:
        getattr(getattr(sys.modules[__name__], sibling),
                "instance_reset")()


class Frontend():

    def __init__(self):
        global g_prj, g_prjbox

        mtk_comm.init()

        self.prj_siblings = ['NewProjectMenu', 'LoadProjectMenu']

        self.menubox = widgets.Box(children=[])

        self.new_prj = widgets.Button(description='New Project', margin="4px")
        self.new_prj.on_click(lambda btn: NewProjectMenu(
            self.prj_siblings, self.menubox, btn))

        self.load_prj = widgets.Button(description='Load Project',
                                       margin="4px")
        self.load_prj.on_click(lambda btn: LoadProjectMenu(self.prj_siblings,
                                                           self.menubox, btn))

        self.export_prj = widgets.Button(description='Save Project',
                                         margin="4px")
        self.export_prj.on_click(lambda btn: SaveProject(self.prj_siblings,
                                                         self.menubox, btn))

        self.box = widgets.HBox(children=[self.new_prj, self.load_prj,
                                          self.export_prj])

        self.vbox = widgets.VBox(children=[self.box, self.menubox])

        g_prjbox = widgets.Box(children=[])

    def show(self):
        global g_prjbox

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
        display(mtk_comm.g_message)
        display(self.vbox)
        display(g_prjbox)
