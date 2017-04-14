import RPi.GPIO as GPIO ## Import GPIO library
from subprocess import call
import time
from datetime import datetime
from datetime import timedelta
import subprocess


from wrappers import GPhoto
import gphoto2 as gp

camera_wrapper = GPhoto(subprocess)

class CameraObj(object):
    def __init__(self):
        self.picture_count = 0
        self.total_pictures = 0
        self.timelapse_duration = 60
        self.timelapse_interval = 3
        self.timelape_start_time = time.time()
        self.shutter_time = 0.5
        self.stable_delay = 0.5
        self.shutter_pin = 14
        self.connected = False
        self.camera = None
        self.trigger = self.remote_trigger

        self.set_timelapse(self.timelapse_duration, self.timelapse_interval)
        self.settings = {'shutterspeed': "---", 'aperture': "---", 'iso': "---"}
        self.settings_index = {'shutterspeed': 0, 'aperture': 0, 'iso': 0}

    def initialize_usb(self):
        try:
            self.context = gp.Context()
            self.camera =gp.Camera()
            self.camera.init(self.context)
            self.options = self.camera.get_config(self.context)
            self.config = gp.check_result(gp.gp_camera_get_config(self.camera, self.context))
            print("SUCCESS")
            return True
        except:
            print("FAILED")
            return False


    def set_timelapse(self, duration, interval):
        # duration in min
        # interval in seconds
        self.total_pictures = int((duration * 60) / interval)
        self.timelapse_duration = duration
        self.timelapse_interval = interval
        self.clip_duration = int(self.total_pictures / 24)


    def get_config(self):
        camera_wrapper.get_shutter_speeds()
        camera_wrapper.get_isos()

    def reset_timelapse(self):
        self.total_pictures = int((self.timelapse_duration * 60) / self.timelapse_interval)
        self.clip_duration = int(self.total_pictures / 24)


    def set_interval(self, direction):
        if direction < 0:
            self.timelapse_interval -= 1
        else:
            self.timelapse_interval += 1

        if self.timelapse_interval < 1:
            self.timelapse_interval = 1
        
        self.reset_timelapse()

    def set_duration(self, direction):
        if direction < 0:
            self.timelapse_duration -= 5
        else:
            self.timelapse_duration += 5
        if self.timelapse_duration < 5:
            self.timelapse_duration = 5
        self.reset_timelapse()

    def modify_bulb_time(self, direction):
        if direction < 0:
            self.shutter_time -= 0.025
        else:
            self.shutter_time += 0.025


    def initialize(self):
        self.connected = camera_wrapper.set_capture_target()
        if self.connected == False:
          self.timelapse_interval = 0.001

    def usb_trigger(self):
        self.camera.trigger_capture(self.context)

    def remote_trigger(self):
        GPIO.output(self.shutter_pin, True)
        time.sleep(0.3)
        GPIO.output(self.shutter_pin, False)

    def timelapse_picture(self):
        time.sleep(self.stable_delay)
        self.trigger()
        self.picture_count += 1



    def bulb_trigger(self):
        camera_wrapper.bulb_trigger(self.shutter_time)

    def mode(self, mode):
        if mode == "usb":
            if self.initialize_usb():
                self.trigger = self.usb_trigger
                self.get_all_settings()
                return True
            else:
                return False
        else:
            self.trigger = self.remote_trigger
            return True

    def get_setting(self, setting_name):
        try:
            setting = gp.check_result(gp.gp_widget_get_child_by_name(self.config, setting_name))
            current = setting.get_value()
            total_values = setting.count_choices()
            self.settings[setting_name] = current
            
            for x in range(total_values):
                value = gp.check_result(gp.gp_widget_get_choice(setting, x))
                if value == current:
                    print("Found")
                    print(x)
                    self.settings_index[setting_name] = x
                    break
            print(self.settings)
            return current
        except:
            print("FAILED")
            return "FAILED"

    def change_setting(self, setting_name, direction):
        if direction < 0:
            next_index = self.settings_index[setting_name] - 1
        else:
            next_index = self.settings_index[setting_name] + 1
        try:
            setting = gp.check_result(gp.gp_widget_get_child_by_name(self.config, setting_name))
            value = gp.check_result(gp.gp_widget_get_choice(setting, next_index))
            print(value)
            gp.check_result(gp.gp_widget_set_value(setting, value))
            gp.check_result(gp.gp_camera_set_config(self.camera, self.config, self.context))
            self.settings[setting_name] = setting.get_value()
            self.settings_index[setting_name] = next_index
        except:
            print("FAILED")

    def get_all_settings(self):
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
                


CONFIGS = [("1/8000", 100),
           ("1/6400", 100),
           ("1/5000", 100),
           ("1/4000", 100),
           ("1/3100", 100),
           ("1/2500", 100),
           ("1/1000", 100),
           ("1/1600", 100),
           ("1/1250", 100),
           ("1/1000", 100),
           ("1/800", 100),
           ("1/640", 100),
           ("1/500", 100),
           ("1/400", 100),
           ("1/320", 100),
           ("1/250", 100),
           ("1/100", 100),
           ("1/160", 100),
           ("1/125", 100),
           ("1/100", 100),
           ("1/80", 100),
           ("1/60", 100),
           ("1/50", 100),
           ("1/40", 100),
           ("1/30", 100),
           ("1/25", 100),
           ("1/20", 100),
           ("1/15", 100),
           ("1/13", 100),
           ("1/10", 100),
           ("1/8", 100),
           ("1/6", 100),
           ("1/5", 100),
           ("1/4", 100),
           ("0.3", 100),
           ("0.4", 100),
           ("0.5", 100),
           ("0.6", 100),
           ("0.8", 100),
           ("1", 100),
           ("1.3", 100),
           ("1.6", 100),
           ("2", 100),
           ("2.5", 100),
           ("3.2", 100),
           ("4", 100),
           ("5", 100),
           ("6", 100),
           ("8", 100),
           ("10", 100),
           ("13", 100),
           ("15", 100),
           ("20", 100),
           ("25", 100),
           ("30", 100),
           ("30", 100)]

camera = CameraObj()



   

  