# from owon_spe import OwonSpePsu
from power_supply import PowerSupply
from arduino_controller import ArduinoController

import time

# create serial connection interfaces for arduino and psu
arduino = ArduinoController("/dev/ttyUSB0", 115200)
psu = PowerSupply("/dev/ttyUSB1", 115200)

duty_cycle_cmd = 1000
decoded_line = ""

def thrust_benchmark(min_throttle: int = 1000, max_throttle: int = 2000, step_size: int = 100):
    # constrain min/max throttle to technical limits
    if min_throttle < 1000:
        min_throttle = 1000
    if max_throttle > 2000:
        max_throttle = 2000

    print(f"Running a motor-propeller benchmark (from {min_throttle}us to {max_throttle}us with +/-{step_size}us steps)")
    
    # perform a standard thrust benchmark with given parameters
    duty_cycle_cmd = min_throttle
    while duty_cycle_cmd < max_throttle:
        if arduino.update_desired_throttle(duty_cycle_cmd) == True:
            time.sleep(2.7)
            thrust = arduino.get_produced_thrust()
            # rpm       = ...
            current   = psu.current
            power     = psu.power
            print(f">> Throttle = {duty_cycle_cmd} us | Current = {current} A | Power = {power} W | Thrust = {thrust} g")
            duty_cycle_cmd += step_size

    while duty_cycle_cmd >= min_throttle:
        if arduino.update_desired_throttle(duty_cycle_cmd) == True:
            time.sleep(2.7)
            thrust = arduino.get_produced_thrust()
            # rpm       = ...
            current   = psu.current
            power     = psu.power
            print(f">> Throttle = {duty_cycle_cmd} us | Current = {current} A | Power = {power} W | Thrust = {thrust} g")
            duty_cycle_cmd -= step_size

def motor_cooling(cooling_throttle: int = 1270):

    print("Perform motor cooling at low constant RPM")
    # upper limit for effective cooling
    if cooling_throttle > 1350:
        cooling_throttle = 1350
        print("Throttle limit is 1350 for effective cooling.")
    
    while True:
        arduino.update_desired_throttle(cooling_throttle)
        time.sleep(2)

#######################
### main entrypoint ###
#######################

try:
    # detect power supply
    print(f"Power supply ready: {psu.id}")

    # configure power supply
    print("Configuring PSU ...")
    psu.off()
    psu.voltage_setpoint = 14.8
    psu.current_setpoint = 10.5

    print("Enabling PSU output ...")
    psu.on()
    time.sleep(5) # ESC needs a  few second to initialize!

    # perform automatic thrust measurement 
    # thrust_benchmark(min_throttle=1150, max_throttle=1350, step_size=50)

    # spin at moderate speed for cooling airflow
    motor_cooling(1260)

    time.sleep(2)

    print("Disabling PSU output ...")
    psu.off()

except KeyboardInterrupt:
    print("Wait for motor stop ...")
    while arduino.update_desired_throttle(1000) == False:
        pass

    print("Throttle at zero.")
    time.sleep(0.3)
    print("Disabling PSU output ...")
    psu.off()

    time.sleep(1)

    del arduino
    print("Graceful exit.")
