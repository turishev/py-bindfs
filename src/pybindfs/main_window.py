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


class MainWindow(Gtk.ApplicationWindow):
    app_title = "pybindfs"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root_dir = None
        self.set_default_size(800, 400)
        self.set_title(self.app_title)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.main_box)

        self.center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.center_box.set_margin_start(8)
        self.center_box.set_margin_end(8)
        self.main_box.append(self.center_box)

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

        self.update_bt = make_button("Update", "update")
        self.bottom_box.append(self.update_bt)

        self.help_bt = make_button("Help", "help")
        self.bottom_box.append(self.help_bt)

        self.close_bt = make_button("Close", "quit")
        self.bottom_box.append(self.close_bt)


    def after_init(self):
        print('after_init')
         # this doesn't work in __init__

    def set_status(self, text, css_class=''):
        self.status_panel.set_status(text, css_class)

