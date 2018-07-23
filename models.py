import os
from ipywidgets import widgets
from serial import Dictable
from urllib import quote_plus
# from IPython.display import display

import mbt_comm
from mbt_comm import Bunch, accordion_title_find, message_set, metys_confirm
from resources import Resources


class Model(Dictable):
    __public__ = ["title", "resources"]

    def __init__(self, title, resources=None, other=None):
        self.title = title
        self.parent = None

        if resources is None:
            self.resources = Resources()
        else:
            self.resources = resources

        self.other = other

        self.wid_delete_btn = widgets.Button(description='Delete',
                                             margin="8px")
        self.wid_delete_btn._gem_ctx = self

        def yes_cb(model):
            parent = model.parent_get()
            parent.model_del(model)

        def no_cb(model):
            return

        def model_delete_cb(model_delete_cb):
            metys_confirm("Delete '%s' model, confirm it ?" % self.title,
                          yes_cb, no_cb, self)
            return

        self.wid_delete_btn.on_click(model_delete_cb)
        wid_label = widgets.Label(value="Model:")
        self.widget = widgets.VBox(children=[
            self.resources.widget_get(), wid_label, self.wid_delete_btn])

    def parent_set(self, parent):
        self.parent = parent

    def parent_get(self):
        return self.parent

    def widget_get(self):
        return self.widget

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
        pre = os.path.join(self.parent.parent.objpath(
            self.title, is_leaf=False))
        if is_leaf:
            return (mbt_comm.OQ_MBT_HOME,
                    os.path.join(pre, 'data', quote_plus(objname)))
        else:
            return (os.path.join(pre, quote_plus(objname)))

    def close(self):
        # FIXME
        pass


class Models(Dictable):
    __public__ = ["models", "current"]

    def __init__(self, models=[], current=None):
        self.wid_label = widgets.HTML(value="Models:", font_weight="bold")
        # ATTENTION: buggy accordion implementation force us
        #            to destroy and recreate it
        #            for each modification (UGLY)!
        self.wid_models_cont = None
        self.wid_proxy = widgets.Proxy(self.wid_models_cont)

        self.wid_mgmt = widgets.VBox(children=[])

        self.models = models[:]
        for mod in self.models:
            mod.parent_set(self)

        # 'current' is a model title
        self.current = None
        if current is not None:
            model_id = self.model_find(current)
            if model_id > -1:
                self.current = current

        self.widget_update()

        def models_add_cb(btn):
            def model_add_cb(btn):
                parent_ctx = btn._gem_ctx._parent_ctx
                if accordion_title_find(parent_ctx.wid_models_cont,
                                        btn._gem_ctx.wid_name.value) > -1:
                    message_set("model '%s' already exists" %
                                btn._gem_ctx.wid_name.value)
                    return False

                model = Model(btn._gem_ctx.wid_name.value, Resources(), [])
                parent_ctx.model_add(model)
                btn._gem_ctx._parent_ctx.wid_mgmt.children = []

            def model_close_cb(btn):
                btn._gem_ctx.wid_mgmt.children = []

            wid_title = widgets.HTML(value="New model")
            wid_name = widgets.Text(description="Name: ")

            wid_add_btn = widgets.Button(description='Add', margin="8px")
            wid_add_btn._gem_ctx = Bunch(wid_name=wid_name,
                                         _parent_ctx=btn._gem_ctx)
            wid_add_btn.on_click(model_add_cb)

            wid_close_btn = widgets.Button(description='Close', margin="8px")
            wid_close_btn._gem_ctx = btn._gem_ctx
            wid_close_btn.on_click(model_close_cb)

            wid_btnbox = widgets.HBox(children=[wid_add_btn, wid_close_btn])

            wid_box = widgets.Box(children=[wid_title, wid_name, wid_btnbox],
                                  border_style="solid", border_width="1px",
                                  border_radius="8px", padding="8px",
                                  width="400px")

            btn._gem_ctx.wid_mgmt.children = [wid_box]

        self.wid_add_btn = widgets.Button(description='Add model',
                                          margin="8px")
        self.wid_add_btn._gem_ctx = self
        self.wid_add_btn.on_click(models_add_cb)

        self.widget = widgets.VBox(
            children=[self.wid_label, self.wid_proxy,
                      self.wid_add_btn, self.wid_mgmt],
            border_style="solid", border_width="1px", padding="8px",
            border_radius="4px")

    def widget_update(self):
        wid_models_cont_old = self.wid_models_cont

        children_new = [mod.widget_get() for mod in self.models]
        wid_models_cont_new = widgets.Accordion(children=children_new,
                                                width=800)

        for i, mod in enumerate(self.models):
            wid_models_cont_new.set_title(i, mod.title)

        model_id = -1
        if self.current is not None:
            model_id = self.model_find(self.current)
            if model_id == -1:
                self.current = None

        wid_models_cont_new.selected_index = model_id

        def selected_index_cb(msg):
            self.current = self.model_get(msg['new']).title

        wid_models_cont_new.observe(selected_index_cb,
                                    names=["selected_index"])

        self.wid_proxy.child = wid_models_cont_new
        self.wid_models_cont = wid_models_cont_new

        if wid_models_cont_old is not None:
            wid_models_cont_old.close()

    def model_add(self, model):
        self.models.append(model)
        self.current = model.title
        self.widget_update()
        model.parent_set(self)

    def model_del(self, model):
        self.models.remove(model)
        self.widget_update()
        model.close()
        del model

    def model_find(self, title):
        for i, mod in enumerate(self.models):
            # print("[%s] [%s]" % (res.key_get(), name))
            if mod.title == title:
                return i
        return -1

    def model_get(self, id):
        return self.models[id]

    def parent_set(self, parent):
        self.parent = parent

    def widget_get(self):
        return self.widget

    def __getitem__(self, title):
        mod = self.model_find(title)
        if mod == -1:
            raise KeyError
        return self.model_get(mod)

    def keys(self):
        return [x.title for x in self.models]
