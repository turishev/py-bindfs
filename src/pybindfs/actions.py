import os
from pathlib import Path, PurePath
import subprocess
# import re
import tomllib

from dataclasses import dataclass

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gio, GLib


import dialogs
from shortcuts import shortcuts;
import version



class AppError(Exception): pass

@dataclass
class MountItem:
    device : str
    mount_point : str
    type : str
    options : list[str]

class AppActions:
    def __init__(self, win):
        self.home = os.getenv('HOME', '')
        self.win = win
        self.actions = [
            ('quit', None, self.quit_handler),
            ('help', None, self.help_handler),
            ('update', None, self.read_mount_table),
            ('bind_fs', 'as', self.bind_fs_handler)
            ]

        config_path = Path(self.home, ".config", "pybindfs.toml")
        config = self.load_config(str(config_path)) if config_path.exists() else {}

        print(f"config:{config}")

        self.sys_media_dir = Path(config.get('default_sys_media_dir', '/run/media'))
        self.default_target_dir = Path(config.get('default_bind_dir','/home/myfamftp/my/media'))
        self.custom_bindings = config.get('bindings', [])

        self.user = os.getenv('USER')
        if self.user is None: raise AppError
        self.media_path = Path(self.sys_media_dir, self.user)


    def register_actions(self, app):
        def _create_act(name : str, param_type : None | str, keys : list[str], fn):
            # we need pass name, keys, fn as values into a separate function
            # to decouple them from mutable iterators
            ptype = None if param_type is None else GLib.VariantType.new(param_type)
            act = Gio.SimpleAction(name=name, parameter_type=ptype)
            act.connect('activate', fn)
            app.add_action(act)
            app.set_accels_for_action("app.%s" % name, keys)

        for act, param_type, handler in self.actions:
            key = shortcuts[act][0] if act in shortcuts else ""
            _create_act(act, param_type, [key], handler)


    def fill_bindings_list(self):
        def append_to_list(origin_path, target_path):
            print(f"add binding:{origin_path} -> {target_path}")
            mount_item = self.find_in_mount_table(str(target_path))
            print(f"mount_item:{mount_item}")
            mount_type = mount_item.type if mount_item else ""
            mount_origin = mount_item.device if mount_item else ""
            is_binded = mount_type == "fuse.bindfs" and mount_origin == str(origin_path)
            self.win.binding_list.append(origin_path, target_path, is_binded)

        self.read_mount_table()
            
        if self.media_path.exists():
            for child in self.media_path.iterdir():
                if child.is_dir():
                    name = child.name
                    origin_path = Path(self.media_path, name)
                    target_path = Path(self.default_target_dir, name)
                    append_to_list(origin_path, target_path)                    

        for item in self.custom_bindings:
            print(f"custom item:{item}")
            origin_path = Path(item['orig'])
            target_path = Path(item['target'])
            append_to_list(origin_path, target_path)                    


    def quit_handler(self, *__):
        self.win.destroy()


    def help_handler(self, *__):
        print("help_handler")
        head = f"pybindfs\nbuild:{version.build_time}\ngit:{version.hash}\n"
        shortcuts_help = "Common shortcuts\n" + "\n".join([
            f"{v[0]}\t{v[1]}" for v in shortcuts.values()
        ])
        text = "\n\n".join([head, shortcuts_help])
        dialogs.show_info_dialog(self.win, text)


    def bind_fs_handler(self, __, parameter):
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

    def load_config(self, config_path : str):
        with open(config_path, "rb") as f:
            return tomllib.load(f)
