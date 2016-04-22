from ipywidgets import widgets
from serial import Dictable

class Resource_kv(Dictable):
    __public__ = ["key", "value"]

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.parent = None

        self.wid_kv = widgets.Text(description=("%s:" % key), value=value)

        def wid_kv_on_change(txt):
            print "wid_kv_on_change fired"
        self.wid_kv.on_submit(wid_kv_on_change)

        self.wid_del = widgets.Button(description="Delete", margin="4px")
        self.wid_del._gem_ctx = self

        def wid_del(btn):
            btn._gem_ctx.on_del()
        self.wid_del.on_click(wid_del)

        self.widget = widgets.HBox(children=[self.wid_kv, self.wid_del],
                                   width="800px")

    def parent_set(self, parent):
        self.parent = parent

    def key_get(self):
        return self.key

    def on_del(self):
        if self.parent:
            self.parent.resource_del(self)

    def widget_get(self):
        return (self.widget)

    def update(self):
        self.value = self.wid_kv.value
