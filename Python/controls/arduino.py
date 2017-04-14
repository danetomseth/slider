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


