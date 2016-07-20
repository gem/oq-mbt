import os
from ipywidgets import widgets
from serial import Dictable
from urllib import quote_plus
from IPython.display import display

import mbt_comm
from mbt_comm import Bunch, accordion_title_find, message_set
from resources import Resources

def confirm(message, yes_cb, no_cb, context):
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

        self.model_delete_btn = widgets.Button(description='Delete', margin="8px")
        self.model_delete_btn._gem_ctx = self

        def yes_cb(model):
            parent = model.parent_get()
            parent.model_del(model)

        def no_cb(model):
            return

        def model_delete_cb(model_delete_cb):
            confirm("This is the confirm page", yes_cb, no_cb, self)
            return

        self.model_delete_btn.on_click(model_delete_cb)
        model_label = widgets.Label(value="Model:")
        self.widget = widgets.VBox(children=[
            self.resources.widget_get(), model_label, self.model_delete_btn])

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
        pre = os.path.join(self.parent.parent.objpath(self.title, is_leaf=False))
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
        self.models_label = widgets.HTML(value="Models:", font_weight="bold")
        # ATTENTION: buggy accordion implementation force us to destroy and recreate it
        #            for each modification (UGLY)!
        self.models_cont = None
        self.models_proxy = widgets.Proxy(self.models_cont)

        self.models_mgmt = widgets.VBox(children=[])

        self.models = models
        for mod in self.models:
            mod.parent_set(self)

        # 'current' is a model title
        self.current = None
        if current != None:
            model_id = self.model_find(current)
            if model_id > -1:
                self.current = current

        self.widget_update()

        def models_add_cb(btn):
            def model_add_cb(btn):
                parent_ctx = btn._gem_ctx._parent_ctx
                if accordion_title_find(parent_ctx.models_cont,
                                        btn._gem_ctx.name.value) > -1:
                    message_set("model '%s' already exists" %
                                btn._gem_ctx.name.value)
                    return False

                model = Model(btn._gem_ctx.name.value, Resources(), [])
                parent_ctx.model_add(model)
                btn._gem_ctx._parent_ctx.models_mgmt.children = []

            def model_close_cb(btn):
                btn._gem_ctx.models_mgmt.children = []

            title = widgets.HTML(value="New model")
            name = widgets.Text(description="Name: ")

            add = widgets.Button(description='Add', margin="8px")
            add._gem_ctx = Bunch(name=name, _parent_ctx=btn._gem_ctx)
            add.on_click(model_add_cb)

            close = widgets.Button(description='Close', margin="8px")
            close._gem_ctx = btn._gem_ctx
            close.on_click(model_close_cb)

            btnbox = widgets.HBox(children=[add, close])

            box = widgets.Box(children=[title, name, btnbox],
                              border_style="solid", border_width="1px",
                              border_radius="8px", padding="8px",
                              width="400px")

            btn._gem_ctx.models_mgmt.children = [box]

        self.models_add = widgets.Button(description='Add model', margin="8px")
        self.models_add._gem_ctx = self
        self.models_add.on_click(models_add_cb)

        self.widget = widgets.VBox(
            children=[self.models_label, self.models_proxy,
                      self.models_add, self.models_mgmt],
            border_style="solid", border_width="1px", padding="8px",
            border_radius="4px")


    def widget_update(self):
        models_cont_old = self.models_cont

        children_new = [mod.widget_get() for mod in self.models]
        models_cont_new = widgets.Accordion(children=children_new, width=800)
        for i, mod in enumerate(self.models):
            models_cont_new.set_title(i, mod.title)

        model_id = -1
        if self.current is not None:
            model_id = self.model_find(self.current)
            if model_id == -1:
                self.current = None

        if model_id >= 0:
            models_cont_new.selected_index = model_id
        else:
            models_cont_new.selected_index = -1

        def selected_index_cb(msg):
            self.current = self.model_get(msg['new']).title

        models_cont_new.observe(selected_index_cb, names=["selected_index"])

        self.models_proxy.child = models_cont_new
        self.models_cont = models_cont_new
        if models_cont_old is not None:
            models_cont_old.close()

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
            # print "[%s] [%s]" % (res.key_get(), name)
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
