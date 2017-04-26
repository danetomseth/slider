#!/usr/bin/env python

# Slide motor
#   step = 17
#   dir = 4
#   enable = 27
#   gearing = 13.73
#   step_angle = 0.131
#   current = 1.68A


# Pan Motor
#   step = 23
#   dir = 24
#   enable = 25
#   gearing = 19.19
#   step_angle = 0.094
#   current = 0.8A 

# Tilt Motor
#   step = 20
#   dir = 21
#   enable = 12
#   gearing = 50.9
#   step_angle = 0.035
#   current = 0.8A  

import time
import analog
import stepper

class MotorObj(object):
    def __init__(self, pins, step_mode, step_angle, ratio, analog_pin, limits, main_direction, home_dir, steps_from_home, motor_name, axis): #pins [step, dir, enable]
        self.name = motor_name
        self.step_pin = pins[0]
        self.direction_pin = pins[1]
        self.enable_pin = pins[2]
        self.main_direction = main_direction
        self.alt_direction = not main_direction
        self.step_count_direction = 1
        self.axis = axis

        
        
        self.gear_ratio = ratio
        self.step_angle = step_angle
        self.step_mode = step_mode
        self.deg_per_step = step_angle / (step_mode)

        self.unit_per_step = (self.deg_per_step / ratio)

        self.steps_per_rev = int(360 / self.deg_per_step)
        self.units_per_rev = int(self.unit_per_step * self.steps_per_rev)
        



        self.speed = 0.00015
        self.default_speed = 0.00015
        self.analog_speed = 0.0
        self.enabled = False
        self.analog_pin = analog_pin 
        self.step_state = False

        self.current_direction = home_dir
        self.home_direction = home_dir
        self.home_step_offset = steps_from_home

        self.step_count = 0
        self.programmed_steps = 0
        self.programmed_steps_taken = 0
        self.program_finished = False
        self.display_message = True
        self.idle_count = 0
        self.programmed_degrees = 0

        self.limits = limits 
        self.limit_status = False
        self.steps_per_move = 0


        # PANO SETTINGS
        self.pano_programmed_steps = 0

        

        self.set_direction(self.home_direction) 

    def _set_rpm(self, rpm):
        """Set the turn speed in RPM."""
        self._rpm = rpm
        # T is the amount of time to stop between signals
        self._T = (60.0 / rpm) / self.steps_per_rev

    # This means you can set "rpm" as if it is an attribute and
    # behind the scenes it sets the _T attribute
    # rpm = property(lambda self: self._rpm, _set_rpm)

    def set_zero(self):
        self.zero = analog.read_raw(self.analog_pin)

    def start_counting(self):
        self.step_count = 0

    def set_step_degrees(self, mode):
        self.step_mode = mode
        self.deg_per_step = self.step_angle / (self.step_mode * self.gear_ratio)

    def calculate_degrees(self, steps):
        self.programmed_degrees = steps * self.deg_per_step
        return self.programmed_degrees

    def calculate_pano_steps(self, degrees):
        self.programmed_degrees = degrees
        self.pano_programmed_steps = int(degrees / self.deg_per_step)
        print("STEPS: " + str(self.pano_programmed_steps))

    def degrees_to_steps(self, degrees):
        steps = int(degrees / self.deg_per_step)
        return steps

    def program_steps(self):
        if self.step_count < 0:
            self.set_direction(self.main_direction)
        else:
            self.set_direction(self.alt_direction)
        self.programmed_steps = abs(self.step_count)

    def program_pano_steps(self):
        if self.step_count < 0:
            self.set_direction(self.main_direction)
        else:
            self.set_direction(self.alt_direction)
        self.pano_programmed_steps = abs(self.step_count)

    def move(self, steps):
        for x in range(steps):
            # Move motor
            pass
        self.disable()


    def move_distance(self, distance):
        total_steps = int(distance / self.unit_per_step)
        for steps in range(total_steps):
            # Move distance
            pass

    def set_step_count(self, distance):
        self.program_finished = False
        self.display_message = True
        self.programmed_steps_taken = 0
        self.programmed_steps = int(distance / self.unit_per_step)
        print(self.name + " STEPS PROGRAMMED: " + str(self.programmed_steps))





    def timelapse_step_low(self, step_count):
        if step_count >= self.steps_per_move:
            return False
        else:
            return True

    def count_step_high(self):
        self.step_count += self.step_count_direction



    def set_speed(self, speed):
        self.speed = speed

    def set_direction(self, direction):
        self.current_direction = direction
        # Set Motor direction
   


    def switch_direction(self):
        self.current_direction = not self.current_direction
        # switch direction



    def read_controller(self):
        self.analog_speed = analog.read_controller(self.axis)
        


    def enable_counting(self):
        self.step_count = 0


    def disable_counting(self):
        print("Total " + self.name +": " + str(self.step_count))
        self.step_count = abs(self.step_count)


    def set_move_steps(self, total_frames):
        self.steps_per_move = int(self.programmed_steps / total_frames)
        print(self.name + ": " + str(self.steps_per_move))

    def find_home(self):
        self.set_direction(self.home_direction)
        # run find home  use self.home_step_offset

    def set_home_direction(self):
        self.set_direction(self.home_direction)


    

  

