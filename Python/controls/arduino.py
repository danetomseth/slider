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


def second_item(speed):
    print("SPEED: " + speed)
    ser.write(speed)
    # while stepper.stop() == False:
    #     message = ser.readline()
    #     print(message)
    print("DONE")

def slide():
    ser.write('s')
    # print(ser.read())
    ser.write('100/')
    while stepper.stop() == False:
        pass
    # ser.reset_input_buffer()
    ser.write('x')
    print(ser.read(10))


def pan():
    ser.write('p')
    print(ser.read())
    ser.write('100/')
    while stepper.stop() == False:
        pass
    ser.write('x')
    print(ser.read())

def tilt():
    ser.write('t')
    print(ser.read())
    ser.write('100/')
    while stepper.stop() == False:
        pass
    ser.write('x')
    print(ser.read())


def fast():
    ser.write("20x")
def stop():
    ser.write('0x')