# from debug import get_debug
import os
import pydoc
from ipywidgets import widgets
from serial import Dictable
from mbt_comm import Bunch, message_set
import mbt_comm
import hashlib

class Importer(object):
    def __init__(self, ref, code, descr):
        self.ref = pydoc.locate(ref)
        self.code = code
        self.descr = descr

class Importers_collection(object):
    def __init__(self):
        self.importer = []

    def add(self, importer):
        for cur in self.importer:
            if cur.code == importer.code:
                raise ValueError
        self.importer.append(importer)

    def options_get(self):
        ret = {}
        for cur in self.importer:
            ret[cur.descr] = cur.code
        return ret

    def ref_by_code(self, code):
        for cur in self.importer:
            if cur.code == code:
                return cur.ref
        return None

mbt_importers = Importers_collection()
# from oqmbt.china.china_tools import faults_to_hmtk
mbt_importers.add(Importer('oqmbt.tools.china.area.areas_to_hmtk', 'china_areas_hmtk', 'China: from areas to hmtk'))
mbt_importers.add(Importer('oqmbt.china.china_tools.faults_to_hmtk', 'china_faults_hmtk', 'China: from faults to hmtk'))

class Resource_external_file(Dictable):
    __public__ = ["filename", "loader", "onthefly", "checksum", "date" ]

    def __init__(self, filename, loader):
        self.filename = filename
        self.loader = loader
        self.parent = None

    @staticmethod
    def add_cb(btn):
        options = mbt_importers.options_get()
        title = widgets.HTML(value="Add external resource")
        message = widgets.HTML(value="")
        file_exists = widgets.Valid(value=False, readout='')
        filename = widgets.Text(description="Filename: ")
        filename._gem_ctx = Bunch(file_exists=file_exists)
        def check_existence(msg):
            file_name = os.path.join(mbt_comm.OQ_MBT_DATA, msg['new'])
            # print file_name
            msg['owner']._gem_ctx.file_exists.value = (
                os.path.exists(file_name) and not os.path.isdir(file_name))
            return True
        
        filename.observe(check_existence, names=["value"])
        flexbox = widgets.HBox(children=[filename, file_exists])

        importer = widgets.Dropdown(
            options=options,
            description='Type of importer:',
        )

        onthefly = widgets.Checkbox(
            value=True,)
        onthefly_desc = widgets.HTML(value="Load on-the-fly when required (persistent and cached otherwise)")
        onthefly_box = widgets.HBox(children=[onthefly, onthefly_desc])

        
        def new_cb(btn):
            ctx = btn._gem_ctx
            ctx.message.value = ""
            if ctx.filename_exists.value is False:
                ctx.message.value = "File '%s' doesn't exists" % ctx.filename.value
                return False

            importer = mbt_importers.ref_by_code(ctx.importer.value)
            if importer is None:
                ctx.message.value = "Importer '%s' not found." % ctx.importer.value
                return False

            print os.path.join(mbt_comm.OQ_MBT_DATA,
                                        ctx.filename.value)
            # == importer here ==
            # obj = importer(os.path.join(mbt_comm.OQ_MBT_DATA,
            #                             ctx.filename.value))
            # print obj

            # checksum computation
            # BLOCKSIZE = 65536
            # hasher = hashlib.sha1()
            # with open('anotherfile.txt', 'rb') as afile:
            #     buf = afile.read(BLOCKSIZE)
            #     while len(buf) > 0:
            #         hasher.update(buf)
            #         buf = afile.read(BLOCKSIZE)
            #         print(hasher.hexdigest())



            
        new = widgets.Button(description='Add', margin="8px")
        new._gem_ctx = Bunch(message=message, filename=filename, filename_exists=file_exists,
                             importer=importer, onthefly=onthefly, _parent_ctx=btn._gem_ctx)
        new.on_click(new_cb)

        def close_cb(btn):
            btn._gem_ctx.res_mgmt.children = []

        close = widgets.Button(description='Close', margin="8px")
        close._gem_ctx = btn._gem_ctx
        close.on_click(close_cb)

        btnbox = widgets.HBox(children=[new, close])

        box = widgets.Box(children=[title, message, flexbox, importer, onthefly_box, btnbox],
                          border_style="solid", border_width="1px",
                          border_radius="8px", padding="8px",
                          width="400px")

        btn._gem_ctx.res_mgmt.children = [box]


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
                                   width="400px")

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

    @staticmethod
    def add_cb(btn):
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

        self.res_addkv = widgets.Button(description='Add parameter',
                                        margin="8px")
        self.res_addkv._gem_ctx = self
        self.res_addkv.on_click(Resource_kv.add_cb)


        self.res_addext = widgets.Button(description='Add external file',
                                         margin="8px")
        self.res_addext._gem_ctx = self
        self.res_addext.on_click(Resource_external_file.add_cb)

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

    def parent_set(self, parent):
        self.parent = parent

    def widget_get(self):
        return self.widget
