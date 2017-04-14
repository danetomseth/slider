import time

from triangula.input import SixAxis, SixAxisResource


# def calibrate():
#     string = 'CAL: %s CAL: %s CAL: %s'
#     zero_vals = []
#     for motor in all_motors:
#         motor.set_zero()
#         zero_vals.append(motor.name + " - " + str(motor.zero))
#     print string % tuple(zero_vals)



# def analog_read():
#     read_values = []
#     string = 'Slide: %s PAN: %s TILT %s'
#     print("STARTING")
#     while stop() == False:
#         read_values = analog.read_all()
#         print string % tuple(read_values)
#         time.sleep(0.5)
#     print("FINISHED")


def connect_ps():
    global joystick
    try:
        joystick = SixAxis()
        print(joystick.connect())
    except:
        print("EXEC")
        joystick.disconnect()
    print("DONE")

def disconnect():
    joystick.disconnect()

def check_bluetooth():
    return joystick.is_connected()

def read_controller(axis):
    time_range = 1000.0
    dir_mod = 1
    x = joystick.axes[axis].corrected_value()
    if abs(x) < 0.1:
        return 1000
    else:
        if x < 0:
            dir_mod = (-1)

        x = abs(x)
        time_val = (1 - x) / 1000
        time_val = round(time_val, 5)
        if time_val < 0.000075:
            time_val = 0.000075
        time_val = time_val * dir_mod
        return time_val

def read_channel(pin):
    value = map_values(mcp.read_adc(pin))
    return value

def read_raw(pin):
    value = mcp.read_adc(pin)
    return value

def read_all():
    read_array = []
    for x in range(3):
        read_array.append(str(mcp.read_adc(x)))
    return read_array



def read_joystick(pin):
    value = joystick(mcp.read_adc(pin))
    return value

def read_quick(pin):
    mcp.read_adc(pin)


def get_values():
    values = [0]*3
    for i in range(3):
        values[i] = map_values(mcp.read_adc(i))
    return values


def map_values(sensor_val):
    neutral = 512.0
    new_range = 100.0
    time_range = 100000.0
    dir_mod = 1

    read_diff = neutral - sensor_val
    
    if abs(read_diff) < 50:
        return 0
    if read_diff < 0:
        dir_mod = (-1)

    read_diff = abs(read_diff)
    scaled_read = (1.0 - float(read_diff / 512)) * new_range

    time_val = scaled_read / time_range
    time_val = round(time_val, 5)

    if time_val < 0.000075:
        time_val = 0.000075
    time_val = time_val * dir_mod

    return time_val


def joystick(sensor_val):
    neutral = 512.0
    new_range = 4.0
    dir_mod = 1

    read_diff = neutral - sensor_val
    
    if abs(read_diff) < 60:
        return 1000
    if read_diff < 0:
        dir_mod = (-1)

    read_diff = abs(read_diff)
    scaled_read = (1.0 - float(read_diff / 512)) * new_range
    time_val = int(scaled_read * dir_mod)
    return time_val



neutral = 512.0
new_range = 5.0


def read_debounce(pin, zero):
    raw_val = mcp.read_adc(pin)
    if raw_val < (zero + 50) and raw_val > (zero - 50):
        return 1000
    else:
        # if raw_val < zero:
        #     raw_val + 25
        # else:
        #     raw_val - 25
        return joystick_debounce(raw_val, zero)


def joystick_debounce(sensor_val, zero):
    speed_range = 10.0
    dir_mod = 1.0
    

    read_diff = neutral - sensor_val
    if read_diff < 0:
        dir_mod = (-1.0)

    read_diff = abs(read_diff)
    time_val = (((1.0 - float(read_diff / neutral)) * speed_range) + 1.0) / 10000.0
    if time_val < 0.00015:
        time_val = 0.0001
    time_val = time_val * dir_mod
    time_val = round(time_val, 5)
    return time_val
