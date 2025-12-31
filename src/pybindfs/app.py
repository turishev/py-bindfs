import os
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw

from main_window import MainWindow
from actions import AppActions

from styles import create_css_provider

class MyApp(Adw.Application):
    def __init__(self):
        super().__init__()
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        print('app: on_activate')
        create_css_provider()
        win = MainWindow(application=app)
        self.actions = AppActions(win)
        self.actions.register_actions(self)
        self.actions.fill_bind_list()
        win.after_init() # after init_actions
        win.present()


