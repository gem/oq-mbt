# from debug import get_debug
import os
import pydoc
from ipywidgets import widgets
from serial import Dictable
from mbt_comm import Bunch, message_set, StdoutToNull
import mbt_comm
import hashlib

class Importer(object):
    def __init__(self, ref, code, descr):
        self.ref = pydoc.locate(ref)
        if not callable(self.ref):
            raise TypeError("The importer [%s] isn't a callable."
                            % ref)
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
mbt_importers.add(Importer('mbt.tools.imprt.faults.get_fmg_faults', 'get_fmg_faults', 'FMG-shallow_faults'))
mbt_importers.add(Importer('mbt.tools.imprt.catalogues.get_htmk_catalogue', 'get_htmk_catalogue', 'FMG-catalogue'))

class Resource_external_file(Dictable):
    __public__ = ["key", "filename", "loader", "onthefly", "checksum", "mtime" ]

    def __init__(self, key, filename, loader, onthefly, checksum, mtime):
        self.key = key
        self.filename = filename
        self.loader = loader
        self.onthefly = onthefly
        self.checksum = checksum
        self.mtime = mtime
        self._obj = None

        if self.onthefly is False:
            self.value

        # check import file consistency
        # TODO

        self.parent = None
        self.wid_key = widgets.Label(value=self.key)
        if (len(self.filename) > 45):
            file_label = "%s ... %s" % (self.filename[0:10], self.filename[-30:])
        else:
            file_label = self.filename

        self.wid_file = widgets.Label(value=file_label)

        self.wid_vbox = widgets.VBox(children=[self.wid_key, self.wid_file],
                                   width="400px")

        self.wid_del = widgets.Button(description="Delete", margin="4px")
        self.wid_del._gem_ctx = self

        def wid_del(btn):
            btn._gem_ctx.on_del()
        self.wid_del.on_click(wid_del)

        self.widget = widgets.HBox(children=[self.wid_vbox, self.wid_del],
                                   width="400px")

    def widget_get(self):
        return (self.widget)


    @property
    def value(self):
        if self._obj != None:
            return self._obj

        abs_filename = os.path.join(mbt_comm.OQ_MBT_DATA,
                                    self.filename)
        importer = mbt_importers.ref_by_code(self.loader)
        with StdoutToNull():
            self._obj = importer(abs_filename)
        if self._obj is None:
            raise ValueError

        return self._obj

    def key_get(self):
        return self.key

    def clear(self):
        if self.onthefly is False:
            return False
        del self._obj
        self._obj = None
        return True

    @classmethod
    def add_cb(cls, btn):
        options = mbt_importers.options_get()
        title = widgets.HTML(value="Add external resource")
        message = widgets.HTML(value="")
        key = widgets.Text(description="Key: ")
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

        onthefly = widgets.Checkbox(value=False,)
        onthefly_desc = widgets.HTML(value="Load on-the-fly when required (persistent and cached otherwise)")
        onthefly_box = widgets.HBox(children=[onthefly, onthefly_desc])


        def new_cb(btn):
            ctx = btn._gem_ctx
            parent_ctx = btn._gem_ctx._parent_ctx
            ctx.message.value = ""

            # check again against C&P missing modify message workaround
            abs_filename = os.path.join(mbt_comm.OQ_MBT_DATA,
                                        ctx.filename.value)
            # print abs_filename
            file_exists.value = (
                os.path.exists(abs_filename) and not os.path.isdir(abs_filename))

            if ctx.filename_exists.value is False:
                ctx.message.value = "File '%s' doesn't exists" % ctx.filename.value
                return False

            importer = mbt_importers.ref_by_code(ctx.importer.value)
            if importer is None:
                ctx.message.value = "Importer '%s' not found." % ctx.importer.value
                return False

            # checksum computation
            BLOCKSIZE = 65536
            hasher = hashlib.sha1()
            with open(abs_filename, 'rb') as afile:
                buf = afile.read(BLOCKSIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = afile.read(BLOCKSIZE)
            checksum = hasher.hexdigest()

            # retrieve mtime
            mtime = os.stat(abs_filename).st_mtime

            res_ef = cls(ctx.key.value, ctx.filename.value, ctx.importer.value,
                         ctx.onthefly.value, checksum, mtime)
            res_ef.parent_set(parent_ctx)
            parent_ctx.resource_add(res_ef)


        new = widgets.Button(description='Add', margin="8px")
        new._gem_ctx = Bunch(message=message, key=key, filename=filename, filename_exists=file_exists,
                             importer=importer, onthefly=onthefly, _parent_ctx=btn._gem_ctx)
        new.on_click(new_cb)

        def close_cb(btn):
            btn._gem_ctx.res_mgmt.children = []

        close = widgets.Button(description='Close', margin="8px")
        close._gem_ctx = btn._gem_ctx
        close.on_click(close_cb)

        btnbox = widgets.HBox(children=[new, close])

        box = widgets.Box(children=[key, title, message, flexbox, importer, onthefly_box, btnbox],
                          border_style="solid", border_width="1px",
                          border_radius="8px", padding="8px",
                          width="400px")

        btn._gem_ctx.res_mgmt.children = [box]

    def on_del(self):
        if self.parent:
            self.parent.resource_del(self)

    def close(self):
        # FIXME
        pass

class Resource_kv(Dictable):
    __public__ = ["key", "value"]

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.parent = None

        self.wid_kv = widgets.Text(description=("%s:" % key), value=value)

        def wid_kv_on_observe(msg):
            self.value = msg['new']
        self.wid_kv.observe(wid_kv_on_observe, names=["value"])


        self.wid_del = widgets.Button(description="Delete", margin="4px")
        self.wid_del._gem_ctx = self

        def wid_del(btn):
            btn._gem_ctx.on_del()
        self.wid_del.on_click(wid_del)

        self.widget = widgets.HBox(children=[self.wid_kv, self.wid_del],
                                   width="400px")

    def key_get(self):
        return self.key

    def on_del(self):
        if self.parent:
            self.parent.resource_del(self)

    def widget_get(self):
        return (self.widget)

    def sync_dom(self):
        self.value = self.wid_kv.value

    def clear(self):
        return True

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

    def close(self):
        # FIXME
        pass


class Resources(Dictable):
    __public__ = ["resources"]

    def __init__(self, resources=[]):
        #
        #  RESOURCES
        #

        self.resources = resources[:]
        self.res_label = widgets.HTML(value="Resources:", font_weight="bold")
        children = []
        for item in self.resources:
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

    def resource_find(self, key):
        for i, res in enumerate(self.resources):
            # print "[%s] [%s]" % (res.key_get(), name)
            if res.key_get() == key:
                return i
        return -1

    def resource_add(self, resource):
        # print "resource_add fired"
        self.resources.append(resource)
        self.res_contbox.children = (self.res_contbox.children +
                                     (resource.widget_get(),))
        self.res_mgmt.children = []

    def resource_get(self, id):
        return self.resources[id]

    def resource_del(self, resource):
        # print "resource_del fired"
        new_children = tuple([x for x in self.res_contbox.children
                              if x != resource.widget_get()])
        self.res_contbox.children = new_children
        self.resources.remove(resource)
        resource.close()
        del resource

    def widget_get(self):
        return self.widget
