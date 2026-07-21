# from owon_spe import OwonSpePsu
from power_supply import PowerSupply
from arduino_controller import ArduinoController

import time

# create serial connection interfaces for arduino and psu
arduino = ArduinoController("COM3", 115200)
psu = PowerSupply("COM4", 115200)

duty_cycle_cmd = 1000
decoded_line = ""

def thrust_benchmark(supply_voltage: float = 11.1, min_throttle: int = 1000, max_throttle: int = 2000, step_size: int = 100):
    # constrain the supply voltage
    if supply_voltage < 7.4:
        supply_voltage = 7.4
    if supply_voltage > 16.8:
        supply_voltage = 16.8

    # constrain min/max throttle to technical limits
    if min_throttle < 1000:
        min_throttle = 1000
    if max_throttle > 2000:
        max_throttle = 2000

    # gather info about motor and propeller
    print("Motor model: ")
    motor_model = input()
    print("Propeller model: ")
    propeller_model = input()

    # prepare power supply
    print("Preparing power supply ...")
    psu.off()
    time.sleep(0.2)
    psu.voltage_setpoint = supply_voltage
    time.sleep(0.2)     # dirty fix!!
    psu.current_setpoint = 12.5
    time.sleep(0.2)     # dirty fix!!
    print("Enabling output ...")
    psu.on()
    time.sleep(5) # ESC needs a  few second to initialize!

    print(f"\nRunning a motor-propeller benchmark @ {supply_voltage} V (from {min_throttle} us to {max_throttle} us with +/-{step_size} us steps)")
    
    # perform a standard thrust benchmark with given parameters
    duty_cycle_cmd = min_throttle
    while duty_cycle_cmd <= max_throttle:
        if arduino.update_desired_throttle(duty_cycle_cmd) == True:
            time.sleep(3.5)
            thrust      = arduino.get_produced_thrust()
            # rpm       = ...
            current     = psu.current
            power       = psu.power
            efficiency  = thrust / power

            print(
                f">> Throttle = {duty_cycle_cmd:>4d} us | "
                f"Current = {current:>6.3f} A | "
                f"Power = {power:>6.2f} W | "
                f"Thrust = {thrust:>6.1f} g | "
                f"Efficiency = {efficiency:>6.3f} g/W"
            )
            duty_cycle_cmd += step_size

    # stop motor once benchmark is completed
    print("Benchmark completed. Stop motors.\n")
    arduino.update_desired_throttle(1000)
    time.sleep(1)

    # disable power supply output
    psu.off()

def motor_cooling(supply_voltage: float = 11.1, cooling_throttle: int = 1270):
    # constrain the supply voltage
    if supply_voltage < 7.4:
        supply_voltage = 7.4
    if supply_voltage > 16.8:
        supply_voltage = 16.8
    
    # upper limit for effective cooling
    if cooling_throttle > 1350:
        cooling_throttle = 1350
        print("Throttle limit is 1350 for effective cooling.")

    # prepare power supply
    print("Preparing power supply ...")
    psu.off()
    time.sleep(0.2)
    psu.voltage_setpoint = supply_voltage
    time.sleep(0.2)     # dirty fix!!
    psu.current_setpoint = 12.5
    time.sleep(0.2)     # dirty fix!!
    print("Enabling output ...")
    psu.on()
    time.sleep(5) # ESC needs a  few second to initialize!
    
    print("Perform motor cooling at low constant RPM")
    while True:
        arduino.update_desired_throttle(cooling_throttle)
        time.sleep(3)

#######################
### main entrypoint ###
#######################

try:
    # identify available power supply
    print(f"Power supply ready: {psu.id}")

    # perform automatic thrust measurement 
    thrust_benchmark(supply_voltage=11.1, min_throttle=1300, max_throttle=1600, step_size=100)

    # spin at moderate speed for cooling airflow
    # motor_cooling(12.4, 1260)

    time.sleep(3)

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
