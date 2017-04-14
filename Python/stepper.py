from decimal import Decimal
import time
import analog
import stepperClass as stepper
from main import window
from subprocess import call
from cameraClass import camera
import math


joystick = 0

slide_pins = [17, 4, 27] #[step, dir, enable]
pan_pins = [23, 24, 25] #[step, dir, enable]
tilt_pins = [20, 21, 12] #[step, dir, enable]

slide_home = False
pan_home = True
tilt_home = True

slide_away = True
pan_away = True
tilt_away = False


stop_button = 22
limits = [5, 6, 13, 19]

#Microstep pins
slide_M0 = 16
slide_M1 = 18
slide_M2 = 15

pan_M1 = 26


#shutter
shutter = 14

pwm_signal = None

micropins = [slide_M0, slide_M1, slide_M2, pan_M1]

step_count_list = []
sorted_motors = []
interval_steps = 0
timelapse_active = False




#Create motor Classes
#([step, dir, enable], step_mode, step_angle, ratio, analog_pin, [limits], main_direction, home_dir, steps_from_home, motor_name): #pins [step, dir, enable]
slide = stepper.MotorObj(slide_pins, 16, 0.131, 3.54331, 2, [5,6], True, slide_home, 3000, "slide", 0)
pan = stepper.MotorObj(pan_pins, 16, 0.094, 4.2, 0, [19], True, pan_home, 4000, "pan", 2)
tilt = stepper.MotorObj(tilt_pins, 32, 0.035, 2, 1, [13], False, tilt_home, 3250, "tilt", 3)


#Create Camera
# camera = CameraObj()

# ------CONSTANTS-------
steps_read_cycle = 40
all_motors = [slide, pan, tilt]

def connect_ps():
    analog.connect_ps()

def picture():
    camera.trigger()












def move(motor):
    if motor == 'slide':
        slide.joystick()
    elif motor == 'pan':
        pan.joystick()
    elif motor == 'tilt':
        tilt.joystick()
    else:
        print("Invalid Motor")

def move_distance(motor, distance):
    if motor == 'slide':
        slide.move_distance(distance)
    elif motor == 'pan':
        pan.move_distance(distance)
    elif motor == 'tilt':
        tilt.move_distance(distance)
    else:
        print("Invalid Motor")




def mount_camera():
    print("Mount Camera")


def return_camera_home():
    print("Return Camera Home")



# -------------- TIMELAPSE -------------- #

def set_timelapse_start():
    global step_count_list
    global sorted_motors
    sorted_motors = []
    speed_list = []
    speed = 0.0001
    
    for motor in all_motors:
        motor.read_debounce()
        motor.start_counting()
    
    while stop() == False:
        active_motors = []
        for motor in all_motors:
            motor.read_debounce()
            if motor.analog_speed == 1000:
                pass
            else:
                speed_list.append(motor.analog_speed)
                active_motors.append(motor)
        if len(active_motors) > 0:
            speed = min(speed_list)
            speed_list = []
            for x in range(steps_read_cycle):
                for motor in active_motors:
                    motor.count_step_high()
                time.sleep(speed)
                for motor in active_motors:
                    motor.step_low()
                time.sleep(speed)
    
    for motor in all_motors:
        motor.program_steps()
        step_count_list.append(motor.programmed_steps)
    
    step_count_list.sort()
    
    for x in step_count_list:
        for motor in all_motors:
            if motor.programmed_steps == x:
                sorted_motors.append(motor)
    
    return sorted_motors

def set_timelapse_end():
    speed_list = []
    speed = 0.0001
    for motor in all_motors:
        motor.read_debounce()
    while stop() == False:
        active_motors = []
        for motor in all_motors:
            motor.read_debounce()
            if motor.analog_speed == 1000:
                pass
            else:
                speed_list.append(motor.analog_speed)
                active_motors.append(motor)
        if len(active_motors) > 0:
            speed = min(speed_list)
            speed_list = []
            for x in range(steps_read_cycle):
                for motor in active_motors:
                    motor.step_high()
                time.sleep(speed)
                for motor in active_motors:
                    motor.step_low()
                time.sleep(speed)
    disable_all()

def timelapse_preview():
    motors = sorted_motors
    counts = [0,0,0]
    preview_speed = 0.005
    enable_all()
    for x in range(motors[2].programmed_steps):
        if preview_speed > 0.00015:
            preview_speed -= 0.000001
        if stop():
            break
        elif x < motors[0].programmed_steps:
            motors[0].step_high()
            motors[1].step_high()
            motors[2].step_high()
            time.sleep(preview_speed)
            motors[0].step_low()
            motors[1].step_low()
            motors[2].step_low()
            time.sleep(preview_speed)

        elif x < motors[1].programmed_steps:
            motors[1].step_high()
            motors[2].step_high()
            time.sleep(preview_speed)
            motors[1].step_low()
            motors[2].step_low()
            time.sleep(preview_speed)

        else:
            motors[2].step_high()
            time.sleep(preview_speed)
            motors[2].step_low()
            time.sleep(preview_speed)

    disable_all()



def reset_position():
    motors = sorted_motors
    preview_speed = 0.005
    for motor in motors:
        motor.switch_direction()
        motor.enable()
    time.sleep(0.25)
    for x in range(motors[2].programmed_steps):
        if preview_speed > 0.001:
            preview_speed -= 0.00005
        if stop():
            break
        elif x < motors[0].programmed_steps:
            # run all motors to lowest step value
            pass

        elif x < motors[1].programmed_steps:
            #  run motors to 2nd lowest
            pass

        else:
            # run final motor
            pass

    for motor in motors:
        # switch direction
        motor.switch_direction()

    print("ALL FINISHED")


def program_timelapse():
    global interval_steps
    global timelapse_active
    timelapse_active = True
    print("TOTAL PICTURES: " + str(camera.total_pictures))
    print("STEPS PER PIC")
    for motor in sorted_motors:
        motor.set_move_steps(camera.total_pictures)
    interval_steps = sorted_motors[2].steps_per_move
    print("Max steps: " + str(interval_steps))

def reset_timelapse():
    global timelapse_active
    global sorted_motors
    sorted_motors = []
    timelapse_active = False
    motors = [slide, pan, tilt]
    camera.picture_count = 0
    for motor in motors:
        motor.programmed_steps = 0


def timelapse_step():
    global timelapse_active
    motors = [slide, pan, tilt]
    step_speed = 0.001
    for motor in motors:
        motor.enable()
    time.sleep(0.05)
    for x in range(interval_steps):
        if stop():
            camera.picture_count = camera.total_pictures
            timelapse_active = False
            break
        for motor in motors:
            motor.step_high()
        time.sleep(step_speed)
        for motor in motors:
            if motor.timelapse_step_low(x) == False:
                motors.remove(motor)
        time.sleep(step_speed)

    for motor in motors:
        motor.disable()
    camera.timelapse_picture()

    
# -------------- PANO -------------- #
def set_pano_start():
    
    # pan.program_pano_steps()
    # print(str(pan.pano_programmed_steps))
    # print(str(pan.calculate_degrees(pan.pano_programmed_steps)))

    return pan.programmed_degrees

def set_pano_end():
    # set pan end
    pass

def set_tilt_start():
    
    # tilt.start_counting()
    # tilt.disable()
    # tilt.program_pano_steps()
    # print("FINISHED")
    # print(str(tilt.pano_programmed_steps))
    # print(str(tilt.calculate_degrees(tilt.pano_programmed_steps)))

    return tilt.programmed_degrees

def program_tilt_steps(degrees):
    tilt.calculate_pano_steps(degrees)

def pano_preview():
    tilt.set_direction(tilt_away)
    for x in range(pan.pano_programmed_steps):
        # Pan step
        pass
    tilt.set_direction(tilt_away)
    for x in range(tilt.pano_programmed_steps):
        pass
        # tilt step
    tilt.disable()


def run_pano():
    view_angle = 17
    total_degrees = pan.calculate_degrees(pan.pano_programmed_steps)
    segments = int(total_degrees / (view_angle / 2))
    tilt_segments = int(tilt.programmed_degrees / (view_angle / 3))
    print("PAN: " + str(segments))
    print("TILT: " + str(tilt_segments))
    pan_steps = pan.pano_programmed_steps / segments
    tilt_steps = tilt.pano_programmed_steps / tilt_segments
    tilt.set_direction(tilt_away)
    pan.enable()
    tilt.enable()
    for x in range(segments):
        trigger_shutter()
        if stop():
            break
        for x in range(tilt_segments):
            for x in range(tilt_steps):
                if stop():
                    break
                tilt.single_step_speed(0.0002)
            trigger_shutter()
        tilt.switch_direction()
        for x in range(pan_steps):
            if stop():
                break
            pan.single_step_speed(0.0002)
        print("TILT")
    for x in range(tilt_steps):
        if stop():
            break
        tilt.single_step_speed(0.0002)
    trigger_shutter()
    pan.disable()
    tilt.disable()
    print("FINISHED")


def clean():
    print("CLEANING")
