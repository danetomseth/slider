#!/usr/bin/env python

from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.uix.layout import Layout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import time
import stepper
from stepper import camera
import arduino


class SettingsScreen(Screen):
    step_mode_tab = ObjectProperty(None)
    control_tab = ObjectProperty(None)
    camera_tab = ObjectProperty(None)
    motors_tab = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

class StepMode(BoxLayout):
    page_title = StringProperty('STEPPER SETTINGS')
    def __init__(self, **kwargs):
        super(StepMode, self).__init__(**kwargs)


    def set_slide(self, mode):
        stepper.slide_microstep(mode)

    def set_pan(self, mode):
        stepper.pan_microstep(mode)


class ControlTab(BoxLayout):
    page_title = StringProperty('CONTROL SETTINGS')
    def __init__(self, **kwargs):
        super(ControlTab, self).__init__(**kwargs)

    

    def connect_arduino(self):
        arduino.connect()

    def recieve_data(self):
        arduino.recieve_data()

    def send_number(self, data):
        arduino.send_number(data)

    def test(self):
        pass

    def calibrate(self):
        # calibrate analog
        stepper.calibrate()

        

class CameraTab(BoxLayout):
    page_title = StringProperty('CAMERA SETTINGS')
    shutter = StringProperty(camera.settings['shutterspeed'])
    iso = StringProperty(camera.settings['iso'])
    aperture = StringProperty(camera.settings['aperture'])
    def __init__(self, **kwargs):
        super(CameraTab, self).__init__(**kwargs)
        
    def set_control(self, mode):
        camera.mode(mode)
        self.display_settings()

    def get_setting(self, setting):
        camera.get_setting(setting)
        self.display_settings()

    def get_config(self):
        camera.get_all_settings()

    def get_current(self):
        camera.get_setting('iso')
        camera.get_setting('shutterspeed')
        camera.get_setting('aperture')
        self.display_settings()

    def change_setting(self, setting, direction):
        camera.change_setting(setting, direction) 
        self.display_settings() 

    def display_settings(self):
        self.shutter = camera.settings['shutterspeed']
        self.iso = camera.settings['iso']
        self.aperture = camera.settings['aperture']
        if self.shutter != '---':
            camera.set_shutter_speed(self.shutter)   

    def test(self):
        camera.trigger()

class MotorsTab(BoxLayout):
    page_title = StringProperty('MOTORS')
    def __init__(self, **kwargs):
        super(MotorsTab, self).__init__(**kwargs)
        self.speed = 1000

    def enable(self):
        stepper.enable_all()

    def disable(self):
        stepper.disable_all()


    




