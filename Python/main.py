#!/usr/local/bin/python
#!/usr/bin/env python
from kivy.config import Config
Config.set('kivy', 'log_level', 'warning')
Config.write()
import os.path
import sys


from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.uix.layout import Layout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App
from kivy.base import ExceptionHandler
from kivy.base import ExceptionManager
from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
import sys
import time

sys.path.append('./pages')
sys.path.append('./controls')
sys.path.append("/Users/danetomseth/Library/Python/2.7/lib/python/site-packages")
print(sys.path)
print(os.path)

import home
import stepper










class Manager(ScreenManager):
    
    home_screen = ObjectProperty(None)
    
    # Live motion
    video_screen = ObjectProperty(None)


    # Timelapse
    timelapse_main = ObjectProperty(None)
    timelapse_simpleA = ObjectProperty(None)
    timelapse_simpleB = ObjectProperty(None)
    timelapse_simpleC = ObjectProperty(None)

    timelapse_advancedA = ObjectProperty(None)


    # Settings
    camera_screen = ObjectProperty(None)
    settings_screen = ObjectProperty(None)




popup = Popup(title='Error',
    content=Label(text='No Camera Detected'),
    size_hint=(None, None), size=(400, 400))

popup2 = Popup(title='Error',
    content=Label(text='No Camera Detected'),
    size_hint=(None, None), size=(400, 400))


class KvmainApp(App):
    
    def build(self):
        self.manager = Manager()
        self.camera_detected = True
        return self.manager

    def exit(self):
        App.get_running_app().stop()

    def find_home(self, motor):
        stepper.find_home(motor)

    def find_home_all(self):
        stepper.find_home_all()

    def no_camera(self):
        # self.camera_detected = False
        print("OPENING 1")
        popup.open()

    def show_popup(self):
        print("OPENING 2")
        popup2.open()


window = KvmainApp()




    



if __name__ == '__main__':
    window.run()