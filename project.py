import os
from IPython.display import display, clear_output
from IPython.core.getipython import get_ipython

from ipywidgets import widgets

import mtk_comm
from mtk_comm import Bunch


class Project(object):
    def __init__(self):
        self.models_label = widgets.HTML(value="Models:")

        # ATTENTION: buggy accordion implementation force us to destroy and recreate it
        #            for each modification (UGLY)!
        self.models_cont = widgets.Accordion(children=[], width=800)

        def models_add_cb(btn):
            def model_add(btn):
                # TODO: add check for duplication of model name

                # TODO: here create of model object and add to the project models array

                # TODO: retrieve UI for new model and add to the accordion
                new_model = widgets.HTML(value="CONTENT: " + btn._gem_ctx.name.value)
                parent_ctx = btn._gem_ctx._parent_ctx
                sz = len(parent_ctx.models_cont.children)
                children_new = parent_ctx.models_cont.children + (new_model,)
                new_acc = widgets.Accordion(children=children_new, width=800)
                for i in range(0, sz):
                    new_acc.set_title(i, parent_ctx.models_cont.get_title(i))
                new_acc.set_title(sz, btn._gem_ctx.name.value)

                parent_ctx.models_contbox.children = [new_acc]
                del(parent_ctx.models_cont)
                parent_ctx.models_cont = new_acc
                parent_ctx.modelsbox.children = []

            def model_close(btn):
                btn._gem_ctx.modelsbox.children = []

            title = widgets.HTML(value="New model")
            name = widgets.Text(description="Name: ")

            add = widgets.Button(description='Add', margin="8px")
            add._gem_ctx = Bunch(name=name, _parent_ctx=btn._gem_ctx)
            add.on_click(model_add)

            close = widgets.Button(description='Close', margin="8px")
            close._gem_ctx = btn._gem_ctx
            close.on_click(model_close)

            btnbox = widgets.HBox(children=[add, close])

            box = widgets.Box(children=[title, name, btnbox],
                              border_style="solid", border_width="1px",
                              border_radius="8px", padding="8px", width="400px")

            btn._gem_ctx.modelsbox.children = [box]


        self.models_add = widgets.Button(description='Add model', margin="8px")
        self.models_add._gem_ctx = self
        self.models_add.on_click(models_add_cb)

        self.modelsbox = widgets.VBox(children=[])

        self.project_label = widgets.HTML(value="Project: ")
        self.project_contents = widgets.HBox(children=[])
        self.models_contbox = widgets.Box(children=[self.models_cont])
        self.project_box = widgets.VBox(
            children=[self.project_label, self.project_contents,
                      self.models_label, self.models_contbox, self.models_add, self.modelsbox])
        display(self.project_box)
        self.project_box.visible = False

    def load(self, name):
        self.clean()
        prjdir = os.path.join(mtk_comm.GEM_MATRIPY_HOME, name)

        if not os.path.isdir(prjdir) and mtk_comm.g_message:
            mtk_comm.g_message.value = "'%s' project not exists" % name
            return

        if not os.path.isfile(os.path.join(prjdir, 'project.json')):
            # all parts must be initialized with defaults and 
            # the json file must be created
            pass
        else:
            # here the loading of project
            pass
        self.title_set(name[:-4])

    def clean(self):
        new_acc = widgets.Accordion(children=[], width=800)

        self.models_contbox.children = [new_acc]
        del(self.models_cont)
        self.models_cont = new_acc


    def title_set(self, name):
        self.project_label.value = "Project: " + name

    def show(self):
        self.project_box.visible = True

