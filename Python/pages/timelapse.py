#!/usr/bin/env python

from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.progressbar import ProgressBar
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.layout import Layout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
import time
import sys

sys.path.append('./controls')
import stepper



from stepper import camera
import arduino

class TimelapseMain(Screen):
    page_title = StringProperty('TIMELAPSE')
    def __init__(self, **kwargs):
        super(TimelapseMain, self).__init__(**kwargs)

    def new_func(self):
        print("Func")

    def print_size(self):
        print(str(self.ids.parent_box.size))




class TimelapseSimple_A(Screen):
    page_title = StringProperty('INTERVAL SETTINGS')
    timelapse_duration = StringProperty("blank")
    timelapse_interval = StringProperty("blank")
    clip_duration = StringProperty("blank")

    def __init__(self, **kwargs):
        super(TimelapseSimple_A, self).__init__(**kwargs)
        self.timelapse_duration = self.get_duration_text()
        self.timelapse_interval = self.get_interval_text()
        self.clip_duration = self.get_clip_duration_text()

    def set_duration(self, direction):
        camera.set_duration(direction)
        self.timelapse_duration = self.get_duration_text()
        self.clip_duration = self.get_clip_duration_text()

    def set_interval(self, direction):
        camera.set_interval(direction)
        self.timelapse_interval = self.get_interval_text()
        self.clip_duration = self.get_clip_duration_text()


    def get_duration_text(self):
        return "Timelapse Duration: " + str(camera.timelapse_duration) + "min"

    def get_interval_text(self):
        return "Interval: " + str(camera.timelapse_interval) + "s"

    def get_clip_duration_text(self):
        return "Clip Duration: " + str(camera.clip_duration) + "s"

        




class TimelapseSimple_B(Screen):
    page_title = StringProperty('MOVEMENT')
    set_point = StringProperty('SET END')
    main_widget = ObjectProperty(None)
    movement_btn = ObjectProperty(None)
    start_btn = ObjectProperty(None)
    end_btn = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(TimelapseSimple_B, self).__init__(**kwargs)
        self.end_set = False
        
    def reset_timelapse(self):
        self.end_set = False
        self.set_point = "SET END"
        print("N/A")

    def set_move_points(self):
        if self.end_set == False:
            arduino.set_timelapse_end()
            self.set_point = "SET START"
            self.end_set = True
        else:
            motors = arduino.set_timelapse_start()
            self.end_set = False
            self.main_widget.remove_widget(self.movement_btn)
            for motor in motors:
                labelText = motor.name + ": " + str(motor.programmed_steps)
                self.main_widget.add_widget(Label(text=labelText, font_size=30))

    def set_end(self):
        arduino.timelapse_mode()
        arduino.set_timelapse_end()
        self.end_btn.disabled = True
        self.start_btn.disabled = False

    def set_start(self):
        motors = arduino.set_timelapse_start()
        self.main_widget.remove_widget(self.start_btn)
        self.main_widget.remove_widget(self.end_btn)
        for motor in motors:
            labelText = "Steps: " + str(motor)
            self.main_widget.add_widget(Label(text=labelText, font_size=30))


class TimelapseSimple_C(Screen):
    progress_widget = ObjectProperty(None)
    progress_label = ObjectProperty(None)
    preview_btn = ObjectProperty(None)
    progress = NumericProperty(None)
    total_pictures = StringProperty("0")
    def __init__(self, **kwargs):
        super(TimelapseSimple_C, self).__init__(**kwargs)
        self.progress = 0
        self.previewed = False


    def preview_movement(self):
        if self.previewed:
            stepper.reset_position()
            self.preview_btn.text = "PREVIEW"
            self.previewed = False
        else:
            stepper.timelapse_preview()
            self.preview_btn.text = "RESET"
            self.previewed = True


        

    def program_timelapse(self):
        stepper.program_timelapse()
        # camera.initialize()

    def run_program(self, dt):
        stepper.timelapse_step()
        self.calculate_progress()
        if stepper.timelapse_active == False:
            print("canceled")
            self.program_interval.cancel()


    def calculate_progress(self):
        self.progress = int((float(camera.picture_count) / float(camera.total_pictures)) * 100)
        self.total_pictures = str(camera.picture_count)
        if self.progress >= 100:
            print("CANCEL FROM PROGRESS")
            self.finish_program()
            self.program_interval.cancel()


    def initiate_program(self):
        self.program_timelapse()
        self.program_interval = Clock.schedule_interval(self.run_program, camera.timelapse_interval)

    def cancel_program(self):
        self.program_interval.cancel()

    def finish_program(self):
        self.progress_widget.remove_widget(self.progress_widget)
        self.progress_widget.remove_widget(self.progress_label)
        self.progress_widget.add_widget(Label(text="FINISHED", font_size="20sp"))
        self.total_pictures = "FINISHED"


    def start_timelapse(self):
        arduino.start_timelapse()





class TimelapseAdvanced_A(Screen):
    def __init__(self, **kwargs):
        super(TimelapseAdvanced_A, self).__init__(**kwargs)


