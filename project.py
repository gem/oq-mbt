import os
import json
from ipywidgets import widgets

import mbt_comm
from mbt_comm import message_set
from serial import Dictable

#
#  TODO
#
# fix TODO for resources and for models
# manage "current" project and model
# add exteral items (with md5 checks)


class Project(Dictable):
    __public__ = ["resources", "models"]

    def __init__(self, resources, models):
        self.project_label = widgets.HTML(value="Project: ",
                                          font_weight="bold")
        #
        #  RESOURCES
        #
        self.resources = resources

        #
        # MODELS
        #
        self.mod = self.models = models
        # print "models len: %d" % len(models.models)
        self.project_label = widgets.HTML(value="Project: ",
                                          font_weight="bold")
        self.project_box = widgets.VBox(
            children=[self.project_label,
                      self.resources.widget_get(),
                      self.models.widget_get()],
            border_style="solid", border_width="1px", padding="8px",
            border_radius="4px")

    @classmethod
    def load(cls, name):
        prjdir = os.path.join(mbt_comm.OQ_MBT_HOME, name)

        if not os.path.isdir(prjdir):
            message_set("'%s' project not exists" % name)
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
        prj.resources.parent_set(prj)
        return prj

    def widget_get(self):
        return self.project_box

    def clean(self):
        # resources
        #self.res_contbox.children = []

        #for item in self.resources:
        #    del item
        #self.resources = []
        # print "TODO clean resources"

        # models
        # print "TODO clean models"
        # new_acc = widgets.Accordion(children=[], width=800)

        # self.models_contbox.children = [new_acc]
        # del(self.models_cont)
        # self.models_cont = new_acc
        pass

    def title_set(self, folder, name):
        self.title = name
        self.folder = folder
        self.project_label.value = "Project: " + name

    def __getitem__(self, key):
        id = self.resources.resource_find(key)
        if id == -1:
            raise KeyError
        return self.resources.resource_get(id).value
