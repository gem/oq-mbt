from ipywidgets import widgets
from serial import Dictable

from mbt_comm import Bunch, accordion_title_find, message_set
from resources import Resources


class Model(Dictable):
    __public__ = ["title", "resources"]

    def __init__(self, title, resources=None, other=None):
        self.title = title
        if resources is None:
            self.resources = Resources()
        else:
            self.resources = resources

        self.is_cur = False
        self.is_cur_wid = widgets.ToggleButton(
            description='Is current',
            value=self.is_cur
            )

        def clicked(btn):
            print clicked

        # self.is_cur_wid.on_click(clicked)

        self.other = other
        self.other_wid_get = widgets.HTML(value="other")

        self.widget = widgets.VBox(children=[
            self.resources.widget_get(),
            self.is_cur_wid,
            self.other_wid_get])

    def parent_set(self, parent):
        self.parent = parent
        pass

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


class Models(Dictable):
    __public__ = ["models"]

    def __init__(self, models=[]):
        self.models_label = widgets.HTML(value="Models:", font_weight="bold")
        # ATTENTION: buggy accordion implementation force us to destroy and recreate it
        #            for each modification (UGLY)!
        self.models_cont = widgets.Accordion(children=[], width=800)
        self.models_mgmt = widgets.VBox(children=[])

        self.models = []
        for item in models:
            self.model_add(item)
            item.parent_set(self)

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
            children=[self.models_label, self.models_cont,
                      self.models_add, self.models_mgmt],
            border_style="solid", border_width="1px", padding="8px",
            border_radius="4px")

    def model_add(self, model):
        self.models.append(model)
        sz = len(self.models_cont.children)
        children_new = self.models_cont.children + (model.widget_get(),)
        self.models_cont.children = children_new
        self.models_cont.set_title(sz, model.title)
        self.models_mgmt.children = []

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
