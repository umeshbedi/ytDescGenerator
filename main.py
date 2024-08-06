from kivy.uix.screenmanager import ScreenManager
from kivymd.tools.hotreload.app import MDApp
from kivy.core.window import Window
from dotenv import load_dotenv
# from kivymd.app import MDApp

load_dotenv()

Window.size = (350,650)
Window._set_window_pos(0,25)

class SM(ScreenManager):
    def get_classes(self):
        return {screen.__class__.__name__: screen.__class__.__module__ for screen in self.screens}


class MainApp(MDApp):
    DEBUG = True
    sm = None
    
    def build_app(self, first=False):
        
        KV_FILES = []
        self.sm = SM()
        CLASSES = self.sm.get_classes()
        self.sm.current = "upload"

        return self.sm
    



# class SM(ScreenManager):
#     pass


# class MainApp(MDApp):
#     sm = None

#     def build(self):
#         self.sm = SM()
#         self.sm.current = 'one'
#         return self.sm



if __name__ == '__main__':
    app = MainApp()
    app.run()



# without hot reload

# from kivy.uix.screenmanager import ScreenManager
# from kivymd.app import MDApp


# class SM(ScreenManager):
#     pass


# class MainApp(MDApp):
#     sm = None

#     def build(self):
#         self.sm = SM()
#         self.sm.current = 'one'
#         return self.sm
#     def some2(self):
#         print("printed from main app")


# if __name__ == '__main__':
#     app = MainApp()
#     app.run()