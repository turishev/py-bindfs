import enum

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gio, GLib
# from subprocess import Popen, DEVNULL, STDOUT
import dialogs
from shortcuts import shortcuts;
import version

class AppActions:
    def __init__(self, win):
        self.win = win
        self.actions = [
            ('quit', self.quit_handler),
            # ('help', self.help_handler),
            ]


    def _update_ui(self):
        while GLib.MainContext.default().pending():
            GLib.MainContext.default().iteration(False)

    def register_actions(self, app):
        def _create_act(name, keys, fn):
            # we need pass name, keys, fn as values into a separate function
            # to decouple them from mutable iterators
            act = Gio.SimpleAction(name=name)
            act.connect('activate', lambda *_: fn())
            app.add_action(act)
            app.set_accels_for_action("app.%s" % name, keys)

        for act, handler in self.actions:
            key = shortcuts[act][0] if act in shortcuts else ""
            _create_act(act, [key], handler)


    def quit_handler(self):
        self.win.destroy()

    def help_handler(self):
        print("help_handler")
        head = f"dirsize.py\nbuild:{version.build_time}\ngit:{version.hash}\n"
        shortcuts_help = "Common shortcuts\n" + "\n".join([
            f"{v[0]}\t{v[1]}" for v in shortcuts.values()
        ])
        text = "\n\n".join([head, shortcuts_help])
        dialogs.show_info_dialog(self.win, text)
