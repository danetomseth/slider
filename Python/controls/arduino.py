import time 
import serial
import stepper

ser = None

def connect():
    global ser
    try:
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0.5)
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


