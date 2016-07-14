import os
import json
from ipywidgets import widgets

import mbt_comm
from mbt_comm import message_set
from serial import Dictable
from cells import Cells
from urllib import quote_plus

from resources import Resources
from models import Models

class Project(Dictable):
    __public__ = ["resources", "models", "cells"]

    def __init__(self, resources, models, cells = None):
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
        self.models.parent_set(self)
        # CELLS
        if cells is None:
            self.cells = Cells([])
        else:
            self.cells = cells

        # print "models len: %d" % len(models.models)
        self.project_label = widgets.HTML(value="Project: ",
                                          font_weight="bold")
        self.project_box = widgets.VBox(
            children=[self.project_label,
                      self.resources.widget_get(),
                      self.models.widget_get()],
            border_style="solid", border_width="1px", padding="8px",
            border_radius="4px")

    def cells_add(self, cells):
        self.cells = Cells(cells)

    @classmethod
    def load(cls, name, is_primary=True):
        prjdir = os.path.join(mbt_comm.OQ_MBT_HOME, quote_plus(name))
        prjdir_old = os.path.join(mbt_comm.OQ_MBT_HOME, name)

        if os.path.isdir(prjdir) is False:
            if os.path.isdir(prjdir_old) is True:
                # migration case
                os.rename(prjdir_old, prjdir)
            else:
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
        if is_primary is True:
            prj.cells.load()
            prj.current_set()

        return prj

    @classmethod
    def create(cls, title):
        newdir = os.path.join(mbt_comm.OQ_MBT_HOME,
                              quote_plus(title) + mbt_comm.OQ_MBT_SFX)
        if os.path.isdir(newdir):
            msg = "'%s' project already exists" % title
            return (None, msg)

        try:
            os.mkdir(newdir)
        except:
            msg = "'%s' project creation failed" % title
            return (None, msg)

        msg = "'%s' project created" % title
        prj = Project(Resources(), Models(), Cells())

        prj.title_set(newdir, title)
        prj.save()

        return (prj, msg)


    def save(self):
        filename = os.path.join(self.folder, 'project.json')

        with open(filename, "w") as outfile:
            json.dump(self.to_dict(), outfile, sort_keys=True, indent=4)

        return True

    def current_set(self):
        with open(os.path.join(mbt_comm.OQ_MBT_HOME, 'CURRENT_PRJ'), 'w') as f:
            title, _ = self.title_get()
            f.write(str(title))


    @classmethod
    def current_get(cls):
        with open(os.path.join(mbt_comm.OQ_MBT_HOME, 'CURRENT_PRJ'), 'r') as f:
            return f.read()
        return None

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

    def title_get(self):
        return (self.title, self.folder)

    def __getitem__(self, key):
        id = self.resources.resource_find(key)
        if id == -1:
            raise KeyError
        return self.resources.resource_get(id).value

    def clear(self, key):
        id = self.resources.resource_find(key)
        if id == -1:
            raise KeyError
        return self.resources.resource_get(id).clear()

    def keys(self):
        return [x.key for x in self.resources.resources]

    def objpath(self, objname, is_leaf=True):
        if is_leaf:
            return (mbt_comm.OQ_MBT_HOME, os.path.join(quote_plus(self.title),
                                                       'data', quote_plus(objname)))
        else:
            return os.path.join(quote_plus(self.title), quote_plus(objname))
