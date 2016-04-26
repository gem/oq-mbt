import os
from IPython.display import display, clear_output
from IPython.core.getipython import get_ipython

from ipywidgets import widgets
import json

import mtk_comm
from mtk_comm import Bunch, accordion_title_find
from resources import Resource_kv
from serial import Dictable

#
#  TODO
#
# objectify resources to be reused in project as in each model
# create a frontend class
# add exteral items (with md5 checks)


class Project(Dictable):
    __public__ = ["resources", "models"]

    def __init__(self, resources, models):

        #
        #  RESOURCES
        #
        self.resources = resources
        self.res_label = widgets.HTML(value="Resources:",font_weight="bold")
        children = []
        for item in resources:
            children.append(item.widget_get())
            item.parent_set(self)
        self.res_contbox = widgets.VBox(children=children)

        def res_addkv_cb(btn):
            # print "res_addkv_cb fired"
            def res_addkv_add(btn):
                parent_ctx = btn._gem_ctx._parent_ctx
                if parent_ctx.resource_find(btn._gem_ctx.name.value) > -1:
                    mtk_comm.g_message.value = ("resource '%s' already exists"
                                                % btn._gem_ctx.name.value)
                    return False

                res_kv = Resource_kv(btn._gem_ctx.name.value,
                                     btn._gem_ctx.value.value)
                res_kv.parent_set(parent_ctx)
                parent_ctx.resource_add(res_kv)
                # print "res_addkv_add fired"

            def res_addkv_close(btn):
                btn._gem_ctx.res_mgmt.children = []

            title = widgets.HTML(value="New parameter")
            name = widgets.Text(description="Name: ")
            value = widgets.Text(description="Value: ")

            add = widgets.Button(description='Add', margin="8px")
            add._gem_ctx = Bunch(name=name, value=value,
                                 _parent_ctx=btn._gem_ctx)
            add.on_click(res_addkv_add)

            close = widgets.Button(description='Close', margin="8px")
            close._gem_ctx = btn._gem_ctx
            close.on_click(res_addkv_close)

            btnbox = widgets.HBox(children=[add, close])

            box = widgets.Box(children=[title, name, value, btnbox],
                              border_style="solid", border_width="1px",
                              border_radius="8px", padding="8px",
                              width="400px")

            btn._gem_ctx.res_mgmt.children = [box]

        self.res_addkv = widgets.Button(description='Add parameter',
                                        margin="8px")
        self.res_addkv._gem_ctx = self
        self.res_addkv.on_click(res_addkv_cb)

        def res_addext_cb(btn):
            print "res_addext_cb"
        self.res_addext = widgets.Button(description='Add external file',
                                         margin="8px")
        self.res_addext._gem_ctx = self
        self.res_addext.on_click(res_addext_cb)

        self.res_btns = widgets.HBox(
            children=[self.res_addkv, self.res_addext])

        self.res_mgmt = widgets.VBox(children=[])

        #
        # MODELS
        #
        self.models = models
        self.models_label = widgets.HTML(value="Models:", font_weight="bold")
        # ATTENTION: buggy accordion implementation force us to destroy and recreate it
        #            for each modification (UGLY)!
        self.models_cont = widgets.Accordion(children=[], width=800)

        def models_add_cb(btn):
            def model_add(btn):
                parent_ctx = btn._gem_ctx._parent_ctx
                if accordion_title_find(parent_ctx.models_cont,
                                        btn._gem_ctx.name.value) > -1:
                    mtk_comm.g_message.value = ("model '%s' already exists" %
                                                btn._gem_ctx.name.value)
                    return False

                # TODO: here create of model object and add to the project models array

                # TODO: retrieve UI for new model and add to the accordion
                #res_kv = Resource_kv(btn._gem_ctx.name.value,
                #                     btn._gem_ctx.value.value)
                #res_kv.parent_set(parent_ctx)
                # FOLLOW Resource rules for model
                model = widgets.HTML(value="CONTENT: " + btn._gem_ctx.name.value)
                parent_ctx.model_add(model, btn._gem_ctx.name.value)

            def model_close(btn):
                btn._gem_ctx.models_mgmt.children = []

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
                              border_radius="8px", padding="8px",
                              width="400px")

            btn._gem_ctx.models_mgmt.children = [box]

        self.models_add = widgets.Button(description='Add model', margin="8px")
        self.models_add._gem_ctx = self
        self.models_add.on_click(models_add_cb)

        self.models_mgmt = widgets.VBox(children=[])

        self.project_label = widgets.HTML(value="Project: ",
                                          font_weight="bold")
        self.models_contbox = widgets.Box(children=[self.models_cont])
        self.project_box = widgets.VBox(
            children=[self.project_label,
                      self.res_label, self.res_contbox,
                      self.res_btns, self.res_mgmt,

                      self.models_label, self.models_contbox,
                      self.models_add, self.models_mgmt],
            border_style="solid", border_width="1px", padding="8px",
            border_radius="4px")

    def resource_find(self, name):
        for i, res in enumerate(self.resources):
            # print "[%s] [%s]" % (res.key_get(), name)
            if res.key_get() == name:
                return i
        return -1

    def resource_add(self, resource):
        # print "resource_add fired"
        self.resources.append(resource)
        self.res_contbox.children = (self.res_contbox.children +
                                     (resource.widget_get(),))
        self.res_mgmt.children = []

    def resource_del(self, resource):
        # print "resource_del fired"
        new_children = tuple([x for x in self.res_contbox.children
                              if x != resource.widget_get()])
        self.res_contbox.children = new_children
        self.resources.remove(resource)
        del resource

    def model_add(self, model, title):
        sz = len(self.models_cont.children)
        children_new = self.models_cont.children + (model,)
        new_acc = widgets.Accordion(children=children_new, width=800)
        for i in range(0, sz):
            new_acc.set_title(i, self.models_cont.get_title(i))
        new_acc.set_title(sz, title)

        self.models_contbox.children = [new_acc]
        del(self.models_cont)
        self.models_cont = new_acc
        self.models_mgmt.children = []

    @classmethod
    def load(cls, name):
        prjdir = os.path.join(mtk_comm.GEM_MATRIPY_HOME, name)

        if not os.path.isdir(prjdir) and mtk_comm.g_message:
            mtk_comm.g_message.value = "'%s' project not exists" % name
            return None

        filename = os.path.join(prjdir, 'project.json')
        if os.path.isfile(filename):
            # here the loading of project
            with open(filename, "r") as infile:
                prj = Dictable.deserialize(json.load(infile))
        else:
            # all parts must be initialized with defaults and 
            # the json file must be created
            prj = Project([], [])
        prj.title_set(prjdir, name[:-4])
        return prj

    def widget_get(self):
        return self.project_box

    def clean(self):
        # resources
        self.res_contbox.children = []

        for item in self.resources:
            del item
        self.resources = []

        # models
        new_acc = widgets.Accordion(children=[], width=800)

        self.models_contbox.children = [new_acc]
        del(self.models_cont)
        self.models_cont = new_acc

    def title_set(self, folder, name):
        self.title = name
        self.folder = folder
        self.project_label.value = "Project: " + name
