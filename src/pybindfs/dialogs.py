import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, GLib, Gio


def show_confirm_dialog(parent, message, on_ok):
    def do_act(source_obj, async_res):
        if source_obj.choose_finish(async_res) == 1: on_ok()

    alert = Gtk.AlertDialog()
    alert.set_message(message)
    alert.set_modal(True)
    alert.set_buttons(["Cancel", "OK"])
    alert.set_default_button(0)
    alert.choose(parent, None, do_act)


def show_alert_dialog(parent, message):
    alert = Gtk.AlertDialog()
    alert.set_message(message)
    alert.set_modal(True)
    alert.set_buttons(["OK"])
    alert.set_default_button(0)
    alert.choose(parent, None, None)
