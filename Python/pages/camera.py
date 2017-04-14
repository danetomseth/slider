#!/usr/bin/env python

from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.uix.layout import Layout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import time
import gphoto2 as gp
import logging
import stepper


# from cameraClass import camera
from cameraClass import camera


class CameraScreen(Screen):
    camera_widget = ObjectProperty(None)
    page_title = StringProperty('CAMERA')
    def __init__(self, **kwargs):
        super(CameraScreen, self).__init__(**kwargs)
        self.shutter_text = self.get_shutter_text()
        self.pic_count = 0
        self.startTime = time.time()
    
    def picture(self):
        camera.capture_image()

    def burst_trigger(self, dt):
        self.startTime = time.time()
        if self.pic_count < 5:
            camera.trigger()
            self.pic_count += 1
            print(str(self.pic_count))
            endTime = time.time() - self.startTime
            print(str(endTime))
        else:
            print("FINSIHED")
            self.program_interval.cancel()



    def quick_picture(self):
        start = time.time()
        camera.trigger()
        end = time.time() - start
        print("TIME: " + str(end))

    def initialize_camera(self):
        start = time.time()
        camera.initialize()
        end = time.time() - start
        print("TIME: " + str(end))


    def modify_shutter(self, direction):
        camera.modify_bulb_time(direction)

        self.ids.shutter.text = self.get_shutter_text()

    def get_shutter_text(self):
        return "Shutter Speed: " + str(camera.shutter_time) + 's'

class PanoScreen(Screen):
    page_title = StringProperty('PANORAMA')
    set_point = StringProperty('SET END')
    tilt_degrees = NumericProperty(0)
    subject_distance = NumericProperty(10)
    movement_btn = ObjectProperty(None)
    main_widget = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(PanoScreen, self).__init__(**kwargs)
        self.direction = "RIGHT"
        self.end_set = False
        self.set_mode = 0
        self.pan_degrees = 0

    # def set_move_points(self):
    #     if self.set_mode == 0:
    #         stepper.set_pano_end()
    #         self.set_point = "SET PAN START"
    #         self.end_set = True
    #         self.set_mode = 1
    #     elif self.set_mode == 1:
    #         self.pan_degrees = stepper.set_pano_start()
    #         self.set_point = "SET TILT END"
    #         self.set_mode = 2
    #     else:
    #         tilt_degrees = stepper.set_tilt_start()
    #         self.end_set = False
    #         self.main_widget.remove_widget(self.movement_btn)
    #         labelText = "Pan Degrees: "  + str(self.pan_degrees) + " Tilt degrees: " + str(tilt_degrees)
    #         self.main_widget.add_widget(Label(text=labelText))

    def set_move_points(self):
        if self.end_set == False:
            stepper.set_pano_end()
            self.set_point = "SET PAN START"
            self.end_set = True
        else:
            pan_degrees = stepper.set_pano_start()
            self.end_set = False
            self.main_widget.remove_widget(self.movement_btn)
            labelText = "Pan Degrees: "  + str(pan_degrees)
            self.main_widget.add_widget(Label(text=labelText, font_size=30))

    def set_distance(self, direction):
        if direction < 0:
            self.subject_distance -= 1
        else:
            self.subject_distance += 1

    def set_degrees(self, direction):
        if direction < 0:
            if self.tilt_degrees > 0:
                self.tilt_degrees -= 1
        else:
            if self.tilt_degrees < 60:
                self.tilt_degrees += 1
        stepper.program_tilt_steps(self.tilt_degrees)

    def set_direction(self, direction):
        if direction:
            self.direction = "RIGHT"
        else:
            self.direction = "LEFT"

    def preview(self):
        stepper.pano_preview()

    def run_pano(self):
        stepper.run_pano()



class FocusScreen(Screen):
    page_title = StringProperty('FOCUS STACK')
    bulb_time = NumericProperty(0.5)
    def __init__(self, **kwargs):
        super(FocusScreen, self).__init__(**kwargs)

    def set_shutter(self, direction):
        if direction < 0:
            if self.bulb_time > 0:
                self.bulb_time = self.bulb_time * 0.9
        else:
            self.bulb_time = self.bulb_time * 1.1

    def run_bulb(self):
        for x in range(5):
            camera.bulb(self.bulb_time)

    def test_bulb(self):
        camera.bulb(self.bulb_time)

    def connect(self):
        stepper.connect_ps()      

    def read(self):
        stepper.read_ps()

    def disconnect(self):
        stepper.disconnect_ps()

class CameraControl(Screen):
    page_title = StringProperty('CAMERA CONTROL')
    top_row = ObjectProperty(None)
    mount_btn = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(CameraControl, self).__init__(**kwargs)
        # self.context = gp.Context()
        # self.camera = gp.Camera()
        # self.camera.init(self.context)
        # self.camera_options = self.camera.get_config(self.context)

    def camera_context(self):
        # text = camera.get_summary(context)
        text = self.camera.get_abilities()
        print('Summary')
        print('=======')
        print(str(text))


    def mount_camera(self):
        stepper.mount_camera()
        # self.top_row.remove_widget(self.mount_btn)
        # new_button = Button(text="FINISHED")
        # new_button.bind(on_press=self.mount_finished)
        # self.top_row.add_widget(new_button)

    def mount_finished(self):
        stepper.return_camera_home()
        print("FINISHED")

    def config(self):
        options = self.camera.get_config(self.context)
        print(options)
        child_count = options.count_children()
        if child_count < 1:
            print('no children')
            return
        for n in range(child_count):
            child = options.get_child(n)
            label = '{} ({})'.format(child.get_label(), child.get_name())
            print(label)
            self.list_children(child)
            print("-----------")

    def list_children(self, child):
        count = child.count_children()
        if count < 1:
            # print("-----")
            return
        else:
            for n in range(count):
                option = child.get_child(n)
                label = '{} ({})'.format(option.get_label(), option.get_name())
                print(label)
                print(option.get_value())
                if option.get_name() == 'iso':
                    choices = option.count_choices()
                    for x in range(choices):
                        print(option.get_choice(x))
                    option.set_value('100')
                        
                    print("*******************")
                # self.list_children(option)

    def capture(self):
        self.camera.trigger_capture(self.context)


    def run_timelapse(self):
        for x in range(1900):
            if x % 30 == 0:
                self.change_shutter()
                time.sleep(1)
            self.capture()
            time.sleep(6)
            print(str(x))

    def change_shutter(self):
        config = gp.check_result(gp.gp_camera_get_config(self.camera, self.context))
        setting = gp.check_result(
        gp.gp_widget_get_child_by_name(config, 'shutterspeed'))
        current = setting.get_value()
        total_values = setting.count_choices()
        
        for x in range(total_values):
            value = gp.check_result(gp.gp_widget_get_choice(setting, x))
            if value == current:
                current_index = x -1
                value = gp.check_result(gp.gp_widget_get_choice(setting, current_index))
                gp.check_result(gp.gp_widget_set_value(setting, value))
                gp.check_result(gp.gp_camera_set_config(self.camera, config, self.context))
                break

    def get_item(self):
        config = gp.check_result(gp.gp_camera_get_config(self.camera, self.context))
        setting = gp.check_result(
        gp.gp_widget_get_child_by_name(config, 'shutterspeed'))
        current = setting.get_value()
        print(current)
        total_values = setting.count_choices()
        print(total_values)
        
        for x in range(total_values):
            value = gp.check_result(gp.gp_widget_get_choice(setting, x))
            if value == current:
                print("Found")
                print(x)
                print(value)
                current_index = x -1
                value = gp.check_result(gp.gp_widget_get_choice(setting, current_index))
                gp.check_result(gp.gp_widget_set_value(setting, value))
                gp.check_result(gp.gp_camera_set_config(self.camera, config, self.context))
                self.capture()
                break
        # time.sleep(2)
        # for x in range(5):
        #     current_index -= 1
        #     value = gp.check_result(gp.gp_widget_get_choice(setting, current_index))
        #     gp.check_result(gp.gp_widget_set_value(setting, value))
        #     gp.check_result(gp.gp_camera_set_config(self.camera, config, self.context))
        #     time.sleep(1)
        #     self.capture()
        #     print(value)
        #     time.sleep(1)
        #     if x > 5:
        #         break
