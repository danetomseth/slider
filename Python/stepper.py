import RPi.GPIO as GPIO ## Import GPIO library
from decimal import Decimal
import time
import analog
import stepperClass as stepper
from main import window
from subprocess import call
from kivy.uix.progressbar import ProgressBar
from cameraClass import camera
import math

from triangula.input import SixAxis, SixAxisResource

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

GPIO.setmode(GPIO.BCM) ## Use board pin numbering

GPIO.setup(shutter, GPIO.OUT)
GPIO.output(shutter, 0)    

GPIO.setup(stop_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

for p in micropins:
    GPIO.setup(p, GPIO.OUT)
    GPIO.output(p, 0)



for y in limits:
    GPIO.setup(y, GPIO.IN, pull_up_down=GPIO.PUD_UP) 




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

last_signal = 50
last_speed = 0.01

def set_pwm():
    global pwm_signal
    global last_signal
    pwm_signal = GPIO.PWM(17, 20000)

def start_pwm():
    slide.enable()
    pwm_signal.start(50)

def stop_pwm():
    pwm_signal.stop()
    slide.disable()

def increase_speed():
    global last_signal
    global last_speed
    last_signal = last_signal * 10
    last_speed = last_speed / 10.0
    print(str(last_speed))

def compare():
    start_time = time.time()
    start_pwm()
    count = 0
    while (time.time() - start_time) < 4.48:
        count += 1
    stop_pwm()
    end_time = time.time() - start_time
    print(str(count))
    print(str(end_time))


def test_signal(delay):
    print("RUNNING")
    slide.enable()
    while stop() == False:
        slide.step_high()
        time.sleep(delay)
        slide.step_low()
        time.sleep(delay)
    slide.disable()
    print("FINISHED")


def test_signal_ramp():
    print("RUNNING")
    delay = 0.1
    while stop() == False:
        slide.step_high()
        time.sleep(delay)
        slide.step_low()
        time.sleep(delay)
    delay = delay / 10
    print("DELAY: "+ str(delay))
    time.sleep(1)
    while stop() == False:
        slide.step_high()
        time.sleep(delay)
        slide.step_low()
        time.sleep(delay)
    delay = delay / 10
    print("DELAY: "+ str(delay))
    time.sleep(1)
    while stop() == False:
        slide.step_high()
        time.sleep(delay)
        slide.step_low()
        time.sleep(delay)
    time.sleep(1)
    delay = delay / 10
    print("DELAY: "+ str(delay))
    while stop() == False:
        slide.step_high()
        time.sleep(delay)
        slide.step_low()
        time.sleep(delay)
    delay = delay / 10
    print("DELAY: "+ str(delay))
    time.sleep(1)
    while stop() == False:
        slide.step_high()
        time.sleep(delay)
        slide.step_low()
        time.sleep(delay)
    
    print("FINISHED")


def test_signal_all(delay):
    print("RUNNING")
    while stop() == False:
        for motor in all_motors:
            motor.step_high()
        time.sleep(delay)
        for motor in all_motors:
            motor.step_low()
        time.sleep(delay)
    print("FINISHED")

def read_ps():
    slide.enable()
    while stop() == False:
        slide.read_controller()

        if slide.analog_speed == 1000:
            pass
        else:
            for x in range(200):
                slide.single_step_speed(slide.analog_speed)
        # x = joystick.axes[0].corrected_value()
        # y = joystick.axes[1].corrected_value()
        # print(x,y)
        # time.sleep(0.1)
    time.sleep(1)
    while stop() == False:
        slide.read_controller()

        if slide.analog_speed == 1000:
            pass
        else:
            for x in range(5):
                slide.single_step_speed(slide.analog_speed)
        # x = joystick.axes[0].corrected_value()
        # y = joystick.axes[1].corrected_value()
        # print(x,y)
        # time.sleep(0.1)
    slide.enable()
    for x in range(3000):
        slide.step_high()
        time.sleep(0.0001)
        slide.step_low()
        time.sleep(0.0001)
    slide.disable()

def disconnect_ps():
    analog.disconnect()



def trigger_shutter():
    GPIO.output(shutter, True)
    time.sleep(0.166667)
    GPIO.output(shutter, False)
    print("Picture")

def change_dir():
    while stop() == False:
        for motor in all_motors:
            motor.switch_direction()
        time.sleep(1)

def test_pan():
    print("STARTING")
    pan.enable()
    while stop() == False:
        pan.single_step_speed(0.0002)
    slide.switch_direction()
    pan.disable()
    print("FINISHED")


def test_slide():
    print("STARTING")
    slide.enable()
    while stop() == False:
        slide.single_step_speed(0.001)
    slide.disable()
    slide.switch_direction()
    print("FINISHED")

def set_pano_start():
    speed = 0.0001
    
    pan.read_debounce()
    pan.start_counting()
    
    while stop() == False:
        pan.read_debounce()
        if pan.analog_speed == 1000:
            pass
        else:
            for x in range(steps_read_cycle):
                pan.count_step_high()
                time.sleep(pan.analog_speed)
                pan.step_low()
                time.sleep(speed)
    pan.disable()
    pan.program_pano_steps()
    print("FINISHED")
    print(str(pan.pano_programmed_steps))
    print(str(pan.calculate_degrees(pan.pano_programmed_steps)))

    if pan.current_direction:
        print("PAN RIGHT")
    else:
        print("PAN LEFT")
    
    return pan.programmed_degrees

def set_pano_end():
    speed_list = []
    speed = 0.0001
    for motor in all_motors:
        motor.read_controller()
    while stop() == False:
        active_motors = []
        for motor in all_motors:
            motor.read_controller()
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

def set_tilt_start():
    speed = 0.0001
    
    tilt.read_debounce()
    tilt.start_counting()
    
    while stop() == False:
        tilt.read_debounce()
        if tilt.analog_speed == 1000:
            pass
        else:
            for x in range(steps_read_cycle):
                tilt.count_step_high()
                time.sleep(tilt.analog_speed)
                tilt.step_low()
                time.sleep(speed)
    tilt.disable()
    tilt.program_pano_steps()
    print("FINISHED")
    print(str(tilt.pano_programmed_steps))
    print(str(tilt.calculate_degrees(tilt.pano_programmed_steps)))

    return tilt.programmed_degrees

def program_tilt_steps(degrees):
    tilt.calculate_pano_steps(degrees)

def pano_preview():
    pan.enable()
    tilt.set_direction(tilt_away)
    for x in range(pan.pano_programmed_steps):
        if stop():
            break
        pan.single_step_speed(0.0002)
    pan.disable()
    print("pan done")
    tilt.enable()
    tilt.set_direction(tilt_away)
    for x in range(tilt.pano_programmed_steps):
        if stop():
            break
        tilt.single_step_speed(0.0002)
    tilt.disable()
    print("FINISHED")

# def calculate_segments(distance, view_angle, total_degrees):
#     radians = math.radians(view_angle / 2)

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

    for motor in motors:
        motor.disable()
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





def run_AB():
    motors = sorted_motors
    for motor in motors:
        motor.enable()
    print("STARTING")
    time.sleep(1)
    for motor in motors:
        motor.enable()
        time.sleep(0.025)
        for x in range(motor.programmed_steps):
            if stop():
                print("STOPPING")
                break
            else:
                motor.single_step()
        motor.disable()
        print(motor.name + " FINISHED")
    time.sleep(1)
    print("ALL FINISHED")



def return_all_home():
    motors = [slide, pan, tilt]

    for motor in motors:
        motor.return_home()

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

def find_home(motor):
    if motor == 'slide':
        slide.find_home()
    elif motor == 'pan':
        print("FINDING PAN HOME")
        pan.find_home()
    elif motor == 'tilt':
        tilt.find_home()
    else:
        print("Invalid Motor")

def find_home_all():
    motors = [slide, pan, tilt]
    home_speed = 0.0003
    for motor in motors:
        motor.set_home_direction()
        motor.enable()
    step_count = 0
    limits_reached = 0
    while limits_reached < 3:
        limits_reached = 0
        if stop():
            break            
        for motor in motors:
            if motor.check_home_limit():
                motor.step_high()
            else:
                limits_reached += 1
        time.sleep(home_speed)
        for motor in motors:
            motor.step_low()
        time.sleep(home_speed)
        step_count += 1
    for motor in motors:
        motor.switch_direction()

    if stop():
        limits_reached = 3
    else:
        limits_reached = 0
    time.sleep(1)
    step_count = 0
    while limits_reached < 3:
        limits_reached = 0
        if stop():
            break            
        for motor in motors:
            if step_count < motor.home_step_offset:
                motor.step_high()
            else:
                limits_reached += 1
        time.sleep(home_speed)
        for motor in motors:
            motor.step_low()
        time.sleep(home_speed)
        step_count += 1

    for motor in motors:
        motor.disable()
    print("FINISHED")


def slide_pan_joystick():
    time.sleep(0.5)
    time_total = 0
    count = 0

    slide.enable()
    pan.enable()
    while stop() == False:
        # motor.read_analog()
        slide.read_two_motor()
        if slide.analog_speed == 0:
            pass
        else:
            for x in range(5):
                slide.two_motor_step()
    time.sleep(1)

def enable_run():
    time.sleep(1)
    print("SLIDE")
    while stop() == False:
        slide.enable()
    slide.disable()
    time.sleep(1)
    print("PAN")
    while stop() == False:
        pan.enable()
    pan.disable()
    time.sleep(1)
    print("TILT")
    while stop() == False:
        tilt.enable()
    tilt.disable()


def mount_camera():
    total_steps = tilt.degrees_to_steps(10)
    tilt.enable()
    tilt.set_direction(tilt_home)
    while tilt.check_home_limit():
        if stop():
            break
        tilt.single_step()
    print("HOME FOUND")
    for x in range(total_steps):
        if stop():
            break
        tilt.single_step()
    tilt.disable()
    print("FINISHED")


def return_camera_home():
    total_steps = tilt.degrees_to_steps(20)
    tilt.enable()
    tilt.set_direction(tilt_away)
    for x in range(total_steps):
        if stop():
            break
        tilt.single_step()
    tilt.disable()
    print("FINISHED")




def run():
    stop_status = GPIO.input(stop_button)
    if stop_status == False:
        print("-----EXIT BUTTON-----")
        return stop_status
    else:
        return stop_status

def stop():
    limitStatus = False
    stop_status = GPIO.input(stop_button)
    
    if stop_status == False:
        limitStatus = True
        disable_all()

    return limitStatus

def disable_all():
    for motor in all_motors:
        motor.disable()

def enable_all():
    for motor in all_motors:
        motor.enable()

def slide_microstep(mode):
    if mode == 1:
        GPIO.output(slide_M0, False)
        GPIO.output(slide_M1, False)
        GPIO.output(slide_M2, False)
        print("FULL")
    elif mode == 2:
        GPIO.output(slide_M0, True)
        GPIO.output(slide_M1, False)
        GPIO.output(slide_M2, False)
        print("HALF")
    elif mode == 4:
        GPIO.output(slide_M0, False)
        GPIO.output(slide_M1, True)
        GPIO.output(slide_M2, False)
        print("QUARTER")
    elif mode == 8:
        GPIO.output(slide_M0, True)
        GPIO.output(slide_M1, True)
        GPIO.output(slide_M2, False)
        print("EIGHTH")
    elif mode == 16:
        GPIO.output(slide_M0, False)
        GPIO.output(slide_M1, False)
        GPIO.output(slide_M2, True)
        print("16")
    elif mode == 32:
        GPIO.output(slide_M0, True)
        GPIO.output(slide_M1, True)
        GPIO.output(slide_M2, True)
        print("32")
    else:
        print("INVALID")
    slide.set_step_degrees(mode)


def pan_microstep(mode):
    if mode == 16:
        GPIO.output(pan_M1, False)
        print("16")
    elif mode == 32:
        GPIO.output(pan_M1, True)
        print("32")
    pan.set_step_degrees(mode)

def ps3():
    print("PS3")

def joystick():
    print("JOYSTICK")

def set_control_ps3():
    global read_mode
    read_mode = ps3
    if analog.check_bluetooth():
        print("CONNECTED")
        for motor in all_motors:
            motor.read = motor.read_controller

    else:
        print("NO CONNECTION")
        for motor in all_motors:
            motor.read = motor.read_debounce



def set_control_joystick():
    global read_mode
    read_mode = joystick
    slide.read = slide.read_debounce
    for motor in all_motors:
        motor.read = motor.read_debounce

def test_control_mode():
    global read_mode
    read_mode()
    while stop() == False:
        speed_list = []
        speed = 0.0002
        for motor in all_motors:
            motor.read()
        while stop() == False:
            active_motors = []
            for motor in all_motors:
                motor.read()
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

def analog_read():
    read_values = []
    string = 'Slide: %s PAN: %s TILT %s'
    print("STARTING")
    while stop() == False:
        read_values = analog.read_all()
        print string % tuple(read_values)
        time.sleep(0.5)
    print("FINISHED")

def accel_step(target_steps, target_speed):
    steps_taken = 0
    current_speed = 0.025
    tilt.enable()
    while current_speed > 0.005:
        tilt.step_high()
        time.sleep(current_speed)
        tilt.step_low()
        time.sleep(current_speed)
        current_speed = current_speed * 0.9
        steps_taken += 1
    while current_speed > 0.0005:
        tilt.step_high()
        time.sleep(current_speed)
        tilt.step_low()
        time.sleep(current_speed)
        current_speed = current_speed * 0.99
        steps_taken += 1
    while current_speed > target_speed:
        tilt.step_high()
        time.sleep(current_speed)
        tilt.step_low()
        time.sleep(current_speed)
        current_speed = current_speed * 0.999
        steps_taken += 1
    print("ACCEL DONE")
    for x in range(3000):
        tilt.step_high()
        time.sleep(target_speed)
        tilt.step_low()
        time.sleep(target_speed)
    tilt.disable()
    print(str(steps_taken))


def calibrate():
    string = 'CAL: %s CAL: %s CAL: %s'
    zero_vals = []
    for motor in all_motors:
        motor.set_zero()
        zero_vals.append(motor.name + " - " + str(motor.zero))
    print string % tuple(zero_vals)


slide_microstep(8)
pan_microstep(16)
connect_ps()

read_mode = joystick

def clean():
    GPIO.cleanup()
    pass