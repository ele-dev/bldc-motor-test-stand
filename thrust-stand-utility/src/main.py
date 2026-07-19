from owon_spe import OwonSpePsu
from arduino_controller import ArduinoController

import time

devices = OwonSpePsu.enumerate_devices()
print(devices)

# serial_arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
arduino = ArduinoController("/dev/ttyUSB0", 115200)

duty_cycle_cmd = 1000
decoded_line = ""

def thrust_benchmark():
    # perform a standard thrust benchmark with +/- 10% steps
    duty_cycle_cmd = 1000
    while duty_cycle_cmd < 1900:
        if arduino.update_desired_throttle(duty_cycle_cmd) == True:
            time.sleep(2.7)
            thrust = arduino.get_produced_thrust()
            # rpm       = ...
            # current   = ...
            # power     = ...
            print(f">> Throttle = {duty_cycle_cmd} us | Thrust = {thrust} g")
            duty_cycle_cmd += 100

    while duty_cycle_cmd >= 1000:
        if arduino.update_desired_throttle(duty_cycle_cmd) == True:
            time.sleep(2.7)
            thrust = arduino.get_produced_thrust()
            # rpm       = ...
            # current   = ...
            # power     = ...
            print(f">> Throttle = {duty_cycle_cmd} us | Thrust = {thrust} g")
            duty_cycle_cmd -= 100

def motor_cooling():
    while True:
        arduino.update_desired_throttle(1300)
        time.sleep(2)

#######################
### main entrypoint ###
#######################

try:
    # perform automatic thrust measurement 
    # thrust_benchmark()

    # spin at moderate speed for cooling airflow
    motor_cooling()

except KeyboardInterrupt:
    print("Wait for motor stop ...")
    while arduino.update_desired_throttle(1000) == False:
        pass

    print("Throttle at zero.")
    time.sleep(1)

    del arduino
    print("Graceful exit.")
