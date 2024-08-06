import os

from kivy.lang import Builder
from kivymd.app import MDApp


def load_kv(module_name):
    #for production
    Builder.load_file(f"{os.path.join(*module_name.split('.'))}.kv")

    #for hotreload
    # MDApp.get_running_app().KV_FILES.append(f"{os.path.join(*module_name.split('.'))}.kv") # type: ignore
    



