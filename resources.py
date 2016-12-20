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
mbt_importers.add(Importer('mbt.importers.faults.get_fmg_faults', 'get_fmg_faults', 'FMG-shallow_faults'))
mbt_importers.add(Importer('mbt.importers.catalogues.get_htmk_catalogue', 'get_htmk_catalogue', 'HMTK-catalogue'))
mbt_importers.add(Importer('mbt.importers.areas.areas_to_oqt_sources', 'areas_to_oqt_source', 'MBT-shapefile_area'))

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
        wid_title = widgets.HTML(value="Add external resource")
        wid_message = widgets.HTML(value="")
        wid_key = widgets.Text(description="Key: ")
        wid_file_exists = widgets.Valid(value=False, readout='')
        wid_filename = widgets.Text(description="Filename: ")
        wid_filename._gem_ctx = Bunch(wid_file_exists=wid_file_exists)
        def check_existence(msg):
            file_name = os.path.join(mbt_comm.OQ_MBT_DATA, msg['new'])
            # print file_name
            msg['owner']._gem_ctx.wid_file_exists.value = (
                os.path.exists(file_name) and not os.path.isdir(file_name))
            return True

        wid_filename.observe(check_existence, names=["value"])
        wid_flexbox = widgets.HBox(children=[wid_filename, wid_file_exists])

        wid_importer = widgets.Dropdown(
            options=options,
            description='Type of importer:',
        )

        wid_onthefly = widgets.Checkbox(value=False,)
        wid_onthefly_desc = widgets.HTML(value="Load on-the-fly when required (persistent and cached otherwise)")
        wid_onthefly_box = widgets.HBox(children=[wid_onthefly, wid_onthefly_desc])


        def new_cb(btn):
            ctx = btn._gem_ctx
            parent_ctx = btn._gem_ctx._parent_ctx
            ctx.wid_message.value = ""

            # check again against C&P missing modify message workaround
            abs_filename = os.path.join(mbt_comm.OQ_MBT_DATA,
                                        ctx.wid_filename.value)
            # print abs_filename
            wid_file_exists.value = (
                os.path.exists(abs_filename) and not os.path.isdir(abs_filename))

            if ctx.wid_file_exists.value is False:
                ctx.wid_message.value = "File '%s' doesn't exists" % ctx.wid_filename.value
                return False

            importer = mbt_importers.ref_by_code(ctx.wid_importer.value)
            if importer is None:
                ctx.wid_message.value = "Importer '%s' not found." % ctx.wid_importer.value
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

            res_ef = cls(ctx.wid_key.value, ctx.wid_filename.value, ctx.wid_importer.value,
                         ctx.wid_onthefly.value, checksum, mtime)
            res_ef.parent_set(parent_ctx)
            parent_ctx.resource_add(res_ef)


        wid_new_btn = widgets.Button(description='Add', margin="8px")
        wid_new_btn._gem_ctx = Bunch(wid_message=wid_message, wid_key=wid_key, wid_filename=wid_filename,
                             wid_file_exists=wid_file_exists, wid_importer=wid_importer,
                             wid_onthefly=wid_onthefly, _parent_ctx=btn._gem_ctx)
        wid_new_btn.on_click(new_cb)

        def close_cb(btn):
            btn._gem_ctx.wid_mgmt.children = []

        wid_close_btn = widgets.Button(description='Close', margin="8px")
        wid_close_btn._gem_ctx = btn._gem_ctx
        wid_close_btn.on_click(close_cb)

        wid_btnbox = widgets.HBox(children=[wid_new_btn, wid_close_btn])

        wid_box = widgets.Box(children=[wid_key, wid_title, wid_message, wid_flexbox, wid_importer, wid_onthefly_box, wid_btnbox],
                          border_style="solid", border_width="1px",
                          border_radius="8px", padding="8px",
                          width="400px")

        btn._gem_ctx.wid_mgmt.children = [wid_box]

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
            if parent_ctx.resource_find(btn._gem_ctx.wid_name.value) > -1:
                message_set("resource '%s' already exists"
                           % btn._gem_ctx.wid_name.value)
                return False

            res_kv = Resource_kv(btn._gem_ctx.wid_name.value,
                                 btn._gem_ctx.wid_value.value)
            res_kv.parent_set(parent_ctx)
            parent_ctx.resource_add(res_kv)
            # print "res_addkv_add fired"

        def res_addkv_close(btn):
            btn._gem_ctx.wid_mgmt.children = []

        wid_title = widgets.HTML(value="New parameter")
        wid_name = widgets.Text(description="Name: ")
        wid_value = widgets.Text(description="Value: ")

        wid_add_btn = widgets.Button(description='Add', margin="8px")
        wid_add_btn._gem_ctx = Bunch(wid_name=wid_name, wid_value=wid_value,
                             _parent_ctx=btn._gem_ctx)
        wid_add_btn.on_click(res_addkv_add)

        wid_close_btn = widgets.Button(description='Close', margin="8px")
        wid_close_btn._gem_ctx = btn._gem_ctx
        wid_close_btn.on_click(res_addkv_close)

        wid_btnbox = widgets.HBox(children=[wid_add_btn, wid_close_btn])

        wid_box = widgets.Box(children=[wid_title, wid_name, wid_value, wid_btnbox],
                          border_style="solid", border_width="1px",
                          border_radius="8px", padding="8px",
                          width="400px")

        btn._gem_ctx.wid_mgmt.children = [wid_box]

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
        self.wid_label = widgets.HTML(value="Resources:", font_weight="bold")
        children = []
        for item in self.resources:
            children.append(item.widget_get())
            item.parent_set(self)
        self.wid_contbox = widgets.VBox(children=children)

        self.wid_addkv = widgets.Button(description='Add parameter',
                                        margin="8px")
        self.wid_addkv._gem_ctx = self
        self.wid_addkv.on_click(Resource_kv.add_cb)


        self.wid_addext = widgets.Button(description='Add external file',
                                         margin="8px")
        self.wid_addext._gem_ctx = self
        self.wid_addext.on_click(Resource_external_file.add_cb)

        self.wid_btns = widgets.HBox(
            children=[self.wid_addkv, self.wid_addext])

        self.wid_mgmt = widgets.VBox(children=[])

        self.widget = widgets.VBox(
            children=[self.wid_label, self.wid_contbox,
                      self.wid_btns, self.wid_mgmt])

    def resource_find(self, key):
        for i, res in enumerate(self.resources):
            if res.key_get() == key:
                return i
        return -1

    def resource_add(self, resource):
        # print "resource_add fired"
        self.resources.append(resource)
        self.wid_contbox.children = (self.wid_contbox.children +
                                     (resource.widget_get(),))
        self.wid_mgmt.children = []

    def resource_get(self, id):
        return self.resources[id]

    def resource_del(self, resource):
        # print "resource_del fired"
        new_children = tuple([x for x in self.wid_contbox.children
                              if x != resource.widget_get()])
        self.wid_contbox.children = new_children
        self.resources.remove(resource)
        resource.close()
        del resource

    def widget_get(self):
        return self.widget
