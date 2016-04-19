import os
import sys
import gc
from IPython.display import HTML
from IPython.display import display, clear_output
from IPython.core.getipython import get_ipython

from ipywidgets import widgets
#text = widgets.Text()
#display(text)

#def handle_submit(sender):
#    print(text.value)
#
#text.on_submit(handle_submit)
# from IPython.display import display

#
#  GLOBALS
#
# projects path
GEM_MATRIPY_HOME = None
GEM_MATRIPY_SFX = '_mbt'

# message text widget handle
g_message = None
g_project = None


def g_project_set(value):
    global g_project

    if g_project is None:
        return
    g_project.value = 'Project: ' + value


def load_project(name):
    global g_message

    prjdir = os.path.join(GEM_MATRIPY_HOME,
                          name)

    if not os.path.isdir(prjdir) and g_message:
        g_message.value = "'%s' project not exists" % name
        return

    if not os.path.isfile(os.path.join(prjdir, 'project.json')):
        # all parts must be initialized with defaults and 
        # the json file must be created
        pass
    else:
        # here the loading of project
        pass


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
        name = btn._gem_context.text.value
        newdir = os.path.join(GEM_MATRIPY_HOME,
                              name
                              + GEM_MATRIPY_SFX)
        if os.path.isdir(newdir):
            g_message.value = "'%s' project already exists" % name
            return

        try:
            os.mkdir(newdir)
        except:
            g_message.value = "'%s' project creation failed" % name
            return

        g_message.value = "'%s' project created" % name
        g_project_set(name)
        btn._gem_context.destroy()
        del btn._gem_context

    @staticmethod
    def _close_cb(btn):
        # print "close_cb"
        btn._gem_context.destroy()
        del btn._gem_context

    def __init__(self, siblings, *args):
        global g_message

        g_message.value = ''
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
        display(self.box)
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
        load_project(btn._gem_context.ddown.value)
        g_project_set(btn._gem_context.ddown.value[:-4])
        btn._gem_context.destroy()
        del btn._gem_context

    @staticmethod
    def _close_cb(btn):
        # print "close_cb"
        btn._gem_context.destroy()
        del btn._gem_context

    def __init__(self, siblings, *args):
        global g_message

        g_message.value = ''
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

        for (_, all_dirs, _) in os.walk(GEM_MATRIPY_HOME):
            break

        prjs = [x for x in all_dirs if x.endswith(GEM_MATRIPY_SFX)]
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
        display(self.box)
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


def ExportProject(siblings, btn):
    for sibling in siblings:
        getattr(getattr(sys.modules[__name__], sibling),
                "instance_reset")()

def main():
    global GEM_MATRIPY_HOME, g_message, g_project
    # display(HTML('''<script>
    # code_show=true;
    # function code_toggle() {
    #  if (code_show){
    #  $('div.input').hide();
    #  } else {
    #  $('div.input').show();
    #  }
    #  code_show = !code_show
    # }
    # $( document ).ready(code_toggle);
    # </script>
    # <a href="javascript:code_toggle()">Source toggle.</a>''')) 

    if 'GEM_MATRIPY_HOME' in os.environ:
        GEM_MATRIPY_HOME = os.environ['GEM_MATRIPY_HOME']
    else:
        from os.path import expanduser
        GEM_MATRIPY_HOME = expanduser("~") + '/.matripyoska'
        os.environ['GEM_MATRIPY_HOME'] = GEM_MATRIPY_HOME

    if not os.access(GEM_MATRIPY_HOME, os.W_OK):
        print "Projects directory [%s] access denied." % GEM_MATRIPY_HOME
        raise os.PermissionError

    g_project = widgets.HTML(read_only=True, width="800px",
                             value="Project: none", height="2em")
    display(g_project)

    # message widget
    g_message = widgets.HTML(read_only=True, width="800px",
                             height="2em")
    display(g_message)

    prj_siblings = ['NewProjectMenu', 'LoadProjectMenu']

    new_prj = widgets.Button(description='New Project', margin="4px")
    new_prj.on_click(lambda x: NewProjectMenu(prj_siblings, x))

    load_prj = widgets.Button(description='Load Project', margin="4px")
    load_prj.on_click(lambda x: LoadProjectMenu(prj_siblings, x))

    export_prj = widgets.Button(description='Export Project', margin="4px")
    export_prj.on_click(lambda x: ExportProject(prj_siblings, x))

    box = widgets.HBox(children=[new_prj, load_prj, export_prj])
    # box.layout.border = '3px solid red'
    display(box)


    models_box = widgets.HBox(children=[])

    project_box = widgets.HBox(title="the project", children=[models_box])
    display(project_box)


