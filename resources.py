from ipywidgets import widgets
from serial import Dictable
from mtk_comm import Bunch, message_set


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

    def sync_dom(self):
        self.value = self.wid_kv.value


class Resources(Dictable):
    __public__ = ["resources"]

    def __init__(self, resources=[]):
        #
        #  RESOURCES
        #
        self.resources = resources
        self.res_label = widgets.HTML(value="Resources:", font_weight="bold")
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
                    message_set("resource '%s' already exists"
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

        self.widget = widgets.VBox(
            children=[self.res_label, self.res_contbox,
                      self.res_btns, self.res_mgmt])

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

    def widget_get(self):
        return self.widget
