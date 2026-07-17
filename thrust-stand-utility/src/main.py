from owon_spe import OwonSpePsu

import serial
import time

devices = OwonSpePsu.enumerate_devices()
print(devices)

serial_arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

duty_cycle_cmd = 1000
decoded_line = ""

def update_desired_throttle(ser: serial.Serial, throttle: int) -> bool:
    # clip to allowed throttle range
    if throttle < 1000:
        throttle = 1000
        print("Warning: Clipping throttle command!")
    if throttle > 2000:
        throttle = 2000
        print("Warning: Clipping throttle command!")

    # send the throttle command over serial connection
    ser.write(f"SET_THROTTLE {throttle}\n".encode('utf-8'))

    # wait for acknowledgement
    line = ser.readline()
    if line:
        decoded_line = line.decode('utf-8', errors='ignore').strip()
        if decoded_line.find("OK: Throttle set to " + str(throttle)) != -1:
            # print(f"Updated throttle to {throttle} us")
            return True
    
    return False

def get_produced_thrust(ser: serial.Serial) -> float:
    # query the thrust measurement over serial connection
    ser.write("GET_THRUST\n".encode('utf-8'))

    # wait for response and return extracted thrust in gramms
    line = ser.readline()
    if line:
        decoded_line = line.decode('utf-8', errors='ignore').strip()
        if decoded_line.startswith("THRUST="):
            return float(decoded_line.removeprefix("THRUST="))
        else:
            print(f"ERROR: {decoded_line}")
    
    return -1000.0


#######################
### main entrypoint ###
#######################

try:
    print("Waiting for controller ...")
    while decoded_line.find("Setup complete.") == -1:
        line = serial_arduino.readline()
        if line:
            decoded_line = line.decode('utf-8', errors='ignore').strip()

    print("Controller ready to receive commands.\n")
    time.sleep(1)

    # perform a simple sweep up and down with +/- 10% steps
    duty_cycle_cmd = 1000
    while duty_cycle_cmd < 1600:
        if update_desired_throttle(serial_arduino, duty_cycle_cmd) == True:
            time.sleep(2.7)
            thrust = get_produced_thrust(serial_arduino)
            print(f">> Throttle = {duty_cycle_cmd} us | Thrust = {thrust} g")
            duty_cycle_cmd += 100

    while duty_cycle_cmd >= 1000:
        if update_desired_throttle(serial_arduino, duty_cycle_cmd) == True:
            time.sleep(2.7)
            thrust = get_produced_thrust(serial_arduino)
            print(f">> Throttle = {duty_cycle_cmd} us | Thrust = {thrust} g")
            duty_cycle_cmd -= 100

except KeyboardInterrupt:
    print("Wait for motor stop ...")
    while update_desired_throttle(serial_arduino, 1000) == False:
        pass

    print("Throttle at zero.")
    time.sleep(1)

    serial_arduino.close()
    print("Graceful exit.")
