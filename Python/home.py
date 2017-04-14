#!/usr/local/bin/python
#!/usr/bin/env python

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

# kivy files
import timelapse
import video

# Control Files
import stepper
import camera
import settings

sys.path.append('./pages')
sys.path.append('./controls')


class PageTitle(BoxLayout):
    title = StringProperty('title')

class E(ExceptionHandler):
    def handle_exception(self, inst):
        print("********EXCEPTION********")
        Logger.exception('CAUGHT EXCEPTION')
        stepper.clean()
        stepper.disconnect_ps()
        App.get_running_app().stop()
        return ExceptionManager.PASS

ExceptionManager.add_handler(E())


class HomeScreen(Screen):
    page_title = StringProperty('PiLapse')
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)


    def enable_run(self):
        # stepper.enable_run()
        stepper.set_timelapse_end()

    def increase_steps(self):
        stepper.increase_steps()

    def run_slide(self):
        stepper.move_slide()


    def test_func(self):
        temp.temp_func()


