from __future__ import annotations # for list annotations
from typing import TypeAlias

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk #, Adw

from binding_list import BindingList

def make_button(label, action):
    bt = Gtk.Button(label=label)
    bt.set_action_name('app.' + action)
    return bt


class StatusPanel():
    def __init__(self):
        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.box.set_spacing(8)
        self.box.set_margin_top(8)
        self.box.set_margin_start(8)
        self.box.set_margin_end(16)

        self.status_label = Gtk.Label()
        self.box.append(self.status_label)
        expander = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        expander.set_hexpand(True)
        self.box.append(expander)
        self.count_label = Gtk.Label()
        self.count_label.set_text("")
        self.box.append(self.count_label)

    def get_box(self):
        return self.box

    def set_status(self, text, css_class=""):
        self.status_label.set_text(text)
        self.status_label.add_css_class(css_class)

    def set_count(self, num : int):
        self.count_label.set_text(f"records: {num}")


class MainWindow(Gtk.ApplicationWindow):
    app_title = "pybindfs"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root_dir = None
        self.set_default_size(1024, 800)
        self.set_title(self.app_title)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.main_box)

        self.center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.center_box.set_margin_start(8)
        self.center_box.set_margin_end(8)
        self.main_box.append(self.center_box)

        self.status_panel = StatusPanel()
        self.main_box.append(self.status_panel.get_box())

        self.bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.bottom_box.set_spacing(10)
        self.bottom_box.set_margin_top(10)
        self.bottom_box.set_margin_bottom(10)
        self.bottom_box.set_margin_start(10)
        self.bottom_box.set_margin_end(10)
        self.bottom_box.set_homogeneous(True)
        self.main_box.append(self.bottom_box)

        self.binding_list = BindingList()
        sw = Gtk.ScrolledWindow()
        self.center_box.append(sw)
        sw.set_child(self.binding_list.list_view)
        self.binding_list.list_view.grab_focus()

        self.help_bt = make_button("Help", "help")
        self.bottom_box.append(self.help_bt)

        self.close_bt = make_button("Close", "quit")
        self.bottom_box.append(self.close_bt)


    def after_init(self):
        print('after_init')
         # this doesn't work in __init__

    def set_status(self, text, css_class=''):
        self.status_panel.set_status(text, css_class)

