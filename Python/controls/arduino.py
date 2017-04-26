import time 
import serial
from cameraClass import camera


ser = None

def connect():
    global ser
    try:
        # ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0.5)
        ser = serial.Serial('/dev/cu.usbmodem1421', 9600)
        # ser = serial.Serial('/dev/tty.usbserial', 9600)
        print("ARDUINO CONNECTED")
    except:
        print("ARDUINO ERROR")

def recieve_data():
    print("Starting")
    ser.write("testing")
    for x in range(10):
        response = ser.readline()
        print(response)
    print("FINISHED")

def first_item():
    ser.write('1x')
    # while stepper.stop() == False:
    #     message = ser.readline()
    #     print(message)
    print("DONE")


def send_number(num): 
    print("Sending: " + num)
    ser.write(num)
    response = ser.readline()
    print(response)

""" Timelapse Control Flow ----

1) Live Control
    a. Read 
2) Single Axis
    a. Read
    1) X Axis
    2) Y Axis
    3) Z Axis

3) Picture
    a. Read

4) Timelapse
    a. Read
    b. Send 1 (Set End)
    c. Read
    d. Send 2 (Set Start)
    e. Read
    f. Send total Frames
    g. Send shutter time
    h. Read x 3 (x steps, y steps, z steps)
    j. Send 3
    k. Read

5) Stop Test
    a. Read

"""
def live_control():
    ser.write("1/")
    res = ser.readline()
    print(res)

def single_axis(axis):
    ser.write("2/")
    print(ser.readline())
    if axis == 'x':
        print("SLIDE")
        ser.write("1/")
    elif axis == 'y':
        ser.write("2/")
        print("PAN")
    else:
        ser.write("3/")
        print("TILT")

def picture():
    ser.write("3/")
    print(ser.readline())

def timelapse_mode():
    ser.write("4/")
    print(ser.readline())

def set_timelapse_end():
    ser.write("1/")
    print(ser.readline())

def set_timelapse_start():
    programmed_steps = [0,0,0];
    total_frames = str(camera.total_pictures) + "/"
    interval_time = str(camera.timelapse_interval) + "/" #$$ replace with camera interval (delay in ms)
    ser.write("2/")
    print(ser.readline())
    ser.write(total_frames) #Send total frames of timelapse
    ser.write(interval_time) #send shuttertime
    programmed_steps[0] = ser.readline()
    programmed_steps[1] = ser.readline()
    programmed_steps[2] = ser.readline()
    return programmed_steps

def start_timelapse():
    ser.write("4/")
    print(ser.readline())


def timelapse_step():
    ser.write("8/")

