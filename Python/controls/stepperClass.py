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
import RPi.GPIO as GPIO
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
        self.zero = 512

        for p in pins:
            GPIO.setup(p, GPIO.OUT)
            GPIO.output(p, 0)
        
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

        self.read = self.read_debounce
        
        

        for l in limits:
           GPIO.setup(l, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.set_direction(self.home_direction) 

    def _set_rpm(self, rpm):
        """Set the turn speed in RPM."""
        self._rpm = rpm
        # T is the amount of time to stop between signals
        self._T = (60.0 / rpm) / self.steps_per_rev

    # This means you can set "rpm" as if it is an attribute and
    # behind the scenes it sets the _T attribute
    rpm = property(lambda self: self._rpm, _set_rpm)

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
        self.enable()
        time.sleep(0.01)
        for x in range(steps):
            GPIO.output(self.step_pin, True)
            time.sleep(self.speed)
            GPIO.output(self.step_pin, False)
            time.sleep(self.speed)
        self.disable()


    def move_distance(self, distance):
        total_steps = int(distance / self.unit_per_step)
        self.enable()
        print("Steps: " + str(total_steps))
        for steps in range(total_steps):
            if self.limit() == False:
                break
            if stepper.stop():
                break
            else:
                self.single_step()
        self.disable()

    def set_step_count(self, distance):
        self.program_finished = False
        self.display_message = True
        self.programmed_steps_taken = 0
        self.programmed_steps = int(distance / self.unit_per_step)
        print(self.name + " STEPS PROGRAMMED: " + str(self.programmed_steps))



    def joystick(self):
        self.enable()
        while stepper.run() and self.limit():
            self.read_analog()
            if self.analog_speed == 0:
                pass
            else:
                for x in range(400):
                    self.variable_single_step()
        self.disable()

    def single_step(self):
        GPIO.output(self.step_pin, True)
        time.sleep(self.speed)
        GPIO.output(self.step_pin, False)
        time.sleep(self.speed)

    def single_step_speed(self, speed):
        GPIO.output(self.step_pin, True)
        time.sleep(speed)
        GPIO.output(self.step_pin, False)
        time.sleep(speed)
      

    def step_high(self):
        GPIO.output(self.step_pin, True)


    def timelapse_step_low(self, step_count):
        GPIO.output(self.step_pin, False)
        if step_count >= self.steps_per_move:
            self.disable()
            return False
        else:
            return True

    def count_step_high(self):
        GPIO.output(self.step_pin, True)
        self.step_count += self.step_count_direction



    def step_low(self):
        GPIO.output(self.step_pin, False)

    def alt_step(self):
        self.step_state = not self.step_state
        GPIO.output(self.step_pin, self.step_state)
        self.step_count += self.step_count_direction


    def programmed_alt_step(self):
        if (self.programmed_steps_taken / 2) < self.programmed_steps:
            if self.limit() == False:
                self.programmed_steps_taken = self.programmed_steps * 2
                self.program_finished = True
                if self.display_message:
                    print(self.name + " STOPPING BY STEP ADJUST")
                    self.display_message = False
                    self.disable()
            else:
                self.step_state = not self.step_state
                GPIO.output(self.step_pin, self.step_state)
                self.programmed_steps_taken += 1
        else:
            self.program_finished = True
            if self.display_message:
                print(self.name + " STOPPING BY STEP ADJUST")
                self.display_message = False
                self.disable()




    def set_speed(self, speed):
        self.speed = speed

    def set_direction(self, direction):
        self.current_direction = direction
        GPIO.output(self.direction_pin, direction)

   

    def set_direction_two(self, direction):
        self.current_direction = direction
        GPIO.output(self.direction_pin, direction)
        GPIO.output(24, direction)

    def switch_direction(self):
        self.current_direction = not self.current_direction
        GPIO.output(self.direction_pin, self.current_direction)

    def read_analog(self):
        self.analog_speed = analog.read_channel(self.analog_pin)
        if self.analog_speed < 0:
            self.set_direction(False)
        elif self.analog_speed > 0:
            self.set_direction(True)
            
        self.analog_speed = abs(self.analog_speed)

        if self.name == 'tilt':
            self.analog_speed = self.analog_speed * 2

    def read_debounce(self):
        self.analog_speed = analog.read_debounce(self.analog_pin, self.zero)
        if self.analog_speed == 1000:
            self.idle_count += 1
            if self.idle_count > 100 and self.enabled:
                self.disable()
            return
        
        if self.analog_speed < 0:
            self.set_direction(self.main_direction)
            self.step_count_direction = 1
        else:
            self.set_direction(self.alt_direction)
            self.step_count_direction = -1
        self.idle_count = 0
        if self.enabled == False:
            self.enable()
        self.analog_speed = abs(self.analog_speed)
        return self.analog_speed

    def read_controller(self):
        self.analog_speed = analog.read_controller(self.axis)
        if self.analog_speed == 1000:
            self.idle_count += 1
            if self.idle_count > 100 and self.enabled:
                self.disable()
            return
        
        if self.analog_speed < 0:
            self.set_direction(self.main_direction)
            self.step_count_direction = 1
        else:
            self.set_direction(self.alt_direction)
            self.step_count_direction = -1
        self.idle_count = 0
        if self.enabled == False:
            self.enable()
        self.analog_speed = abs(self.analog_speed)
        return self.analog_speed


    def read_joystick(self):
        self.analog_speed = analog.read_joystick(self.analog_pin)
        if self.analog_speed == 1000:
            self.idle_count += 1
            if self.idle_count > 100 and self.enabled:
                self.disable()
            return
        elif self.analog_speed < 0:
            self.set_direction(self.main_direction)
            self.step_count_direction = 1
        elif self.analog_speed > 0:
            self.set_direction(self.alt_direction)
            self.step_count_direction = -1
        self.idle_count = 0
        if self.enabled == False:
            self.enable()
        self.analog_speed = abs(self.analog_speed)
        if self.analog_speed < 1:
            self.analog_speed = 1

        if self.name == 'tilt':
            self.analog_speed = self.analog_speed * 2

        if self.name == 'pan':
            self.analog_speed = self.analog_speed * 2

       
    def read_set_channel(self):
        self.analog_speed = analog.read_channel(2)
        if self.analog_speed < 0:
            self.set_direction(False)
        elif self.analog_speed > 0:
            self.set_direction(True)
            
        self.analog_speed = abs(self.analog_speed)

        if self.name == 'tilt':
            self.analog_speed = self.analog_speed * 2
        # return self.analog_speed
    
    def variable_single_step(self):
        if self.analog_speed > 0:
            GPIO.output(self.step_pin, True)
            time.sleep(self.analog_speed)
            GPIO.output(self.step_pin, False)
            time.sleep(self.analog_speed)
        else:
            return
        if self.current_direction == False:
            self.step_count -= 1
        else:
            self.step_count += 1

    def two_motor_step(self):
        if self.analog_speed > 0:
            GPIO.output(self.step_pin, True)
            GPIO.output(23, True)
            time.sleep(self.analog_speed)
            GPIO.output(self.step_pin, False)
            GPIO.output(23, False)
            time.sleep(self.analog_speed)
        else:
            return
        if self.current_direction == False:
            self.step_count -= 1
        else:
            self.step_count += 1

    def read_two_motor(self):
        self.analog_speed = analog.read_channel(2)
        if self.analog_speed < 0:
            self.set_direction_two(False)
        elif self.analog_speed > 0:
            self.set_direction_two(True)
            
        self.analog_speed = abs(self.analog_speed)

        if self.name == 'tilt':
            self.analog_speed = self.analog_speed * 2




    def return_home(self):
        self.enable()
        self.speed = 0.0002
        if self.step_count < 0:
            self.set_direction(True)
        else:
            self.set_direction(False)
        self.step_count = abs(self.step_count)
        for x in range(self.step_count):
            self.single_step()
        self.disable()
        self.step_count = 0

    def enable(self):
        self.enabled = True
        GPIO.output(self.enable_pin, True)

    def disable(self):
        self.enabled = False
        GPIO.output(self.enable_pin, False)        

    def toggle_enable(self):
        self.enabled = not self.enabled


    def enable_counting(self):
        self.step_count = 0
        self.enable()


    def disable_counting(self):
        print("Total " + self.name +": " + str(self.step_count))
        self.step_count = abs(self.step_count)
        self.disable()


    def stop_counting(self):
        print("Count: " + str(self.step_count))
        self.step_count = abs(self.step_count)
        self.disable()

    def set_move_steps(self, total_frames):
        self.steps_per_move = int(self.programmed_steps / total_frames)
        print(self.name + ": " + str(self.steps_per_move))

    def find_home(self):
        self.set_direction(self.home_direction)
        self.speed = self.default_speed
        self.enable()
        while self.limit():
            self.single_step()
        print("Home Found")
        time.sleep(0.5)
        self.switch_direction()
        print("OFFSET: " + str(self.home_step_offset))
        for x in range(self.home_step_offset):
            if stepper.stop():
                break
            else:
                self.single_step()
        # self.count_from_home()
        self.disable()

    def set_home_direction(self):
        self.set_direction(self.home_direction)

    def adjust_home(self):
        self.enable()
        while stepper.stop() == False:
            self.read_analog()
            for x in range(100):
                self.variable_single_step()
        self.disable()

    def reset_from_limit(self):
        away_dir = not self.home_direction
        self.set_direction(away_dir)
        self.enable()
        while self.limit() == False:
            self.single_step()
        for x in range(500):
            self.single_step()
        self.disable()

    def count_from_home(self):
        count = 0
        away_dir = not self.home_direction
        self.set_direction(away_dir)
        while stepper.stop() == False:
            count += 1
            self.single_step()
        self.disable()
        print("STEPS TAKEN: " + str(count))

    def check_home_limit(self):
        limit_status = True
        for l in self.limits:
            if GPIO.input(l) == False:
                limit_status = False
                break
        return limit_status

    def limit(self):
        limit_status = True
        for l in self.limits:
            if GPIO.input(l) == False:
                limit_status = False
                break
            elif stepper.stop():
                limit_status = False
                break
            else:
                pass
        return limit_status

    def __clear(self):
        GPIO.output(self.P1, 0)
        GPIO.output(self.P2, 0)
        GPIO.output(self.P3, 0)
        GPIO.output(self.P4, 0)

    


