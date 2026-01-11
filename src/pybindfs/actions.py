import os
from pathlib import Path, PurePath
import subprocess
import re

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gio, GLib
# from subprocess import Popen, DEVNULL, STDOUT
import dialogs
from shortcuts import shortcuts;
import version

from dataclasses import dataclass

class AppError(Exception): pass

@dataclass
class MountItem:
    device : str
    mount_point : str
    type : str
    options : list[str]

class AppActions:
    default_origin_dir = Path('/', 'run', 'media')
    default_target_dir = Path('/','home','myfamftp','my','media')

    def __init__(self, win):
        self.win = win
        self.actions = [
            ('quit', self.quit_handler),
            ('help', self.help_handler),
            ('update', self.read_mount_table),
            ]

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


        act = Gio.SimpleAction.new("bind_fs", GLib.VariantType.new("as"))
        act.connect("activate", self.bind_fs_handler)
        app.add_action(act)


    def fill_bind_list(self):
        self.read_mount_table()
        self.user = os.getenv('USER')
        if self.user is None: raise AppError
        self.media_path = Path(AppActions.default_origin_dir, self.user)

        if self.media_path.exists():
            for child in self.media_path.iterdir():
                if child.is_dir():
                    name = child.name
                    origin_path = Path(self.media_path, name)
                    target_path = Path(AppActions.default_target_dir, name)
                    print(f"path:{origin_path} -> {target_path}")
                    mount_item = self.find_in_mount_table(str(target_path))
                    print(f"mount_item:{mount_item}")
                    mount_type = mount_item.type if mount_item else ""
                    mount_origin = mount_item.device if mount_item else ""
                    is_binded = mount_type == "fuse.bindfs" and mount_origin == str(origin_path)
                    self.win.binding_list.append(origin_path, target_path, is_binded)


    def quit_handler(self):
        self.win.destroy()


    def help_handler(self):
        print("help_handler")
        head = f"pybindfs\nbuild:{version.build_time}\ngit:{version.hash}\n"
        shortcuts_help = "Common shortcuts\n" + "\n".join([
            f"{v[0]}\t{v[1]}" for v in shortcuts.values()
        ])
        text = "\n\n".join([head, shortcuts_help])
        dialogs.show_info_dialog(self.win, text)


    def bind_fs_handler(self, action, parameter):
        origin_dir, target_dir = parameter.unpack()
        print(f"bind_fs_handler, origin_dir: {origin_dir} target_dir:{target_dir}")
        is_binded = self.win.binding_list.get_binded_flag(origin_dir, target_dir)
        if not is_binded:
            result = self.bind_origin_to_target(origin_dir, target_dir)
            if not result: print("Binding error")
            self.win.binding_list.set_binded_flag(origin_dir, target_dir, True)
        else:
            result = self.unbind_target(target_dir)
            if not result: print("Unbinding error")
            self.win.binding_list.set_binded_flag(origin_dir, target_dir, False)

        self.read_mount_table()


    def check_binding(self, origin_dir : str, target_dir : str):
        # mount
        pass
        # /run/media/prog/EVT_DATA on /home/myfamftp/my/media/EVT_DATA type fuse.bindfs (rw,nosuid,nodev,relatime,user_id=1000,group_id=1000,default_permissions,allow_other)



    def bind_origin_to_target(self, origin_dir : str, target_dir : str):
        target_path = Path(target_dir)
        if target_path.exists():
            if any(target_path.iterdir()): raise AppError()
        else:
            target_path.mkdir(parents=True, exist_ok=True)

        completed = subprocess.run(["bindfs", origin_dir, target_dir])

        if completed.returncode != 0:  return False
        else: return True


    def unbind_target(self, target_dir):
        completed = subprocess.run(["fusermount", "-u", target_dir])
        if completed.returncode != 0:  return False
        else: return True


    def read_mount_table(self):
        result = subprocess.run(
            ["mount"],
            capture_output=True,    # Захватить stdout и stderr
            text=True,              # Декодировать вывод в строку (UTF-8)
            check=True              # Выбросить исключение при ошибке (код != 0)
        )
        # print(result.stdout)        # Основной вывод процесса

        lines = result.stdout.split("\n")
        table = [l.split() for l in lines]
        self.mount_table = [
            MountItem(
                device = item[0],
                mount_point = item[2],
                type = item[4],
                options = item[5][1:-1].split(','),
            )
            for item in table if item != []
        ]
        print(self.mount_table)


    def find_in_mount_table(self, mount_point):
        for item in self.mount_table:
            if item.mount_point == mount_point:
                return item
