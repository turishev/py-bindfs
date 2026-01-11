from __future__ import annotations # for list annotations
from typing import TypeAlias

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gdk, Gio, GObject



class DataObject(GObject.GObject):
    __gtype_name__ = 'DataObject'

    origin_path = GObject.Property(type=str, default="")
    target_path = GObject.Property(type=str, default="")
    switched_on = GObject.Property(type=bool, default=False)

    def __init__(self, origin_path, target_path, status):
        super().__init__()
        self.origin_path = origin_path
        self.target_path = target_path
        self.switched_on = status


def _create_list_column(name, data_field, setup_fn, bind_fn, unbind_fn):
    factory = Gtk.SignalListItemFactory()
    factory.connect("setup", setup_fn)
    factory.connect("bind", bind_fn)
    if unbind_fn is not None: factory.connect("unbind", unbind_fn)
    return Gtk.ColumnViewColumn(title=name, factory=factory)


class BindingList():
    def __init__(self):
        self.store = Gio.ListStore(item_type=DataObject)
        self.list_view = Gtk.ColumnView()

        self.origin_path = _create_list_column("Origin",
                                               "origin_path",
                                               self.setup_path_field,
                                               self.bind_origin,
                                               None)
        self.origin_path.set_expand(True)
        self.list_view.append_column(self.origin_path)

        self.target_path = _create_list_column("Target",
                                               "target_path",
                                               self.setup_path_field,
                                               self.bind_target,
                                               None)
        self.target_path.set_expand(True)
        self.list_view.append_column(self.target_path)

        self.list_view.append_column(
            _create_list_column(
                "",
                "switched_on",
                self.setup_button_field,
                self.bind_button_field,
                self.unbind_fields)
        )

        sorter = Gtk.ColumnView.get_sorter(self.list_view)
        self.sort_model = Gtk.SortListModel(model=self.store, sorter=sorter)
        self.selection = Gtk.NoSelection(model=self.sort_model)
        self.list_view.set_model(self.selection)
        self.list_view.set_hexpand(True)
        self.list_view.set_vexpand(True)


    def setup_path_field(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(0.0)
        item.set_child(label)

    def bind_origin(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(obj.origin_path)

    def bind_target(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(obj.target_path)

    def setup_button_field(self, factory, item : Gtk.ColumnViewCell):
        bt = Gtk.Button()
        # bt.add_css_class("result-list-active-button")
        item.set_child(bt)

    def bind_button_field(self, factory, item : Gtk.ColumnViewCell):
        bt = item.get_child()
        obj : DataObject = item.get_item()
        bt.set_action_name("app.bind_fs")
        obj : DataObject = item.get_item()
        target_value = GLib.Variant("as", [obj.origin_path, obj.target_path])
        bt.set_action_target_value(target_value)
        bt._binding = obj.bind_property("switched_on",
                                        bt, "label",
                                        GObject.BindingFlags.SYNC_CREATE,
                                        lambda __,v: "MOUNT" if not v else "UNMOUNT")


    def unbind_fields(self, factory, item : Gtk.ColumnViewCell):
        child = item.get_child()
        if hasattr(child, "_binding"):
            child._binding.unbind()


    def append(self, origin_path, target_path, status = False):
        obj = DataObject(origin_path=origin_path, target_path=target_path, status=status)
        self.store.append(obj)


    def clear(self):
        self.store.remove_all()


    def get_list_len(self):
        return len(self.store)

    def set_binded_flag(self, origin_path, target_path, is_binded):
        for obj in self.store:
            if obj.origin_path == origin_path and obj.target_path == target_path:
                obj.switched_on = is_binded


    def get_binded_flag(self, origin_path, target_path):
        for obj in self.store:
            if obj.origin_path == origin_path and obj.target_path == target_path:
                return obj.switched_on
