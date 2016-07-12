import os
from IPython.display import HTML
from IPython.display import display, Javascript
from ipykernel.comm import Comm
import json
from ipywidgets import widgets

import mbt_comm
from mbt_comm import message_set, message_show

from resources import Resources
from models import Models
from cells import Cells, Cell, cells_cleanall
from project import Project

g_prj = None


class NewProjectMenu(object):
    @staticmethod
    def _create_cb(btn):
        global g_prj
        name = btn._gem_ctx.text.value
        newdir = os.path.join(mbt_comm.OQ_MBT_HOME,
                              name
                              + mbt_comm.OQ_MBT_SFX)
        if os.path.isdir(newdir):
            message_set("'%s' project already exists" % name)
            return

        try:
            os.mkdir(newdir)
        except:
            message_set("'%s' project creation failed" % name)
            return

        message_set("'%s' project created" % name)
        g_prj = Project(Resources(), Models(), Cells())
        g_prj.title_set(newdir, name)
        g_prj.current_set()
        btn._gem_ctx.metys.prjbox_set([g_prj.widget_get()])
        btn._gem_ctx.metys.menubox_set(())
        del btn._gem_ctx

    @staticmethod
    def _close_cb(btn):
        btn._gem_ctx.metys.menubox_set(())
        del btn._gem_ctx

    def __init__(self, metys):
        self.metys = metys
        message_set('')
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

    def widget_get(self):
        return self.box


class LoadProjectMenu(object):
    @staticmethod
    def _load_cb(btn):
        global g_prj

        if g_prj is not None:
            g_prj.clean()
            del g_prj

        g_prj = Project.load(btn._gem_ctx.ddown.value)
        btn._gem_ctx.metys.prjbox_set([g_prj.widget_get()])

        btn._gem_ctx.metys.menubox_set(())
        del btn._gem_ctx

    @staticmethod
    def _close_cb(btn):
        # print "close_cb"
        btn._gem_ctx.metys.menubox_set(())
        del btn._gem_ctx

    def __init__(self, metys):
        self.metys = metys
        message_set('')
        self.load = widgets.Button(description='Load', margin="8px")
        self.load._gem_ctx = self
        self.load.on_click(self._load_cb)

        self.close = widgets.Button(description='Close', margin="8px")
        self.close._gem_ctx = self
        self.close.on_click(self._close_cb)

        for (_, all_dirs, _) in os.walk(mbt_comm.OQ_MBT_HOME):
            break

        prjs = [x for x in all_dirs if x.endswith(mbt_comm.OQ_MBT_SFX)]
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

    def widget_get(self):
        return self.box



class Metys():

    def __init__(self):
        global g_prj

        mbt_comm.init()

        self.menubox = widgets.Box(children=[])

        self.new_prj = widgets.Button(description='New Project', margin="4px")
        self.new_prj._gem_ctx = self

        def new_prj_cb(btn):
            new_prj = NewProjectMenu(btn._gem_ctx)
            btn._gem_ctx.menubox_set((new_prj.widget_get(),))
        self.new_prj.on_click(new_prj_cb)

        self.load_prj = widgets.Button(description='Load Project',
                                       margin="4px")
        self.load_prj._gem_ctx = self

        def load_prj_cb(btn):
            load_prj = LoadProjectMenu(btn._gem_ctx)
            btn._gem_ctx.menubox_set((load_prj.widget_get(),))
        self.load_prj._gem_ctx = self
        self.load_prj.on_click(load_prj_cb)

        self.save_prj = widgets.Button(description='Save Project',
                                       margin="4px")
        self._gem_ctx = self

        def save_prj_cb(btn):
            filename = os.path.join(g_prj.folder, 'project.json')

            def on_msg(msg):
                with open(filename, "w") as outfile:
                    cells = []
                    for cell_in in msg['content']['data']:
                        cells.append(Cell(cell_in['type'], cell_in['content']))
                    g_prj.cells_add(cells)
                    
                    json.dump(g_prj.to_dict(), outfile, sort_keys=True, indent=4)
                    message_set("'%s' project saved correctly" % filename)
                c.close([])
            
            c = Comm(target_name='oq_getcells_target', target_module='oq_getcells_module',
                     data={'some': 'data'})
            c.on_msg(on_msg)

            c.send(['require_cells'])

        self.save_prj.on_click(save_prj_cb)

        self.box = widgets.HBox(children=[self.new_prj, self.load_prj,
                                          self.save_prj
                                          ])

        self.vbox = widgets.VBox(children=[self.box, self.menubox])

        self.prjbox = widgets.Box(children=[])

    def prjbox_set(self, new_items):
        if self.prjbox is not None:
            self.prjbox.children = new_items

    def menubox_set(self, new_items):
        self.menubox.children = new_items

    def show(self):
        display(HTML('''<script>
        code_show=true;
        function code_toggle() {
            if (code_show){
                $($('div.input')[0]).hide();
            } else {
                $($('div.input')[0]).show();
            }
         code_show = !code_show
        }
        $( document ).ready(code_toggle);
        </script>
        <a href="javascript:code_toggle()">Source toggle.</a>'''))
        message_show()
        display(self.vbox)
        display(self.prjbox)
        cells_cleanall()

        if os.getenv('OQ_MBT_IS_DEVEL') is not None:
            # enable operation
            load_prj = LoadProjectMenu(self)
            self.menubox_set((load_prj.widget_get(),))
            load_prj.ddown.value = 'SouthEast China_mbt'

            load_prj.load._click_handlers.callbacks[0](load_prj.load)

            print g_prj["owner"]

            
#            print g_prj.mod["Model one"]["the_data"]


