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
    if throttle > 2000:
        throttle = 2000

    # send the throttle command over serial connection
    ser.write(f"{throttle}\n".encode('utf-8'))

    # wait for acknowledgement
    line = ser.readline()
    if line:
        decoded_line = line.decode('utf-8', errors='ignore').strip()
        if decoded_line.find(">> Throttle set to: " + str(throttle)) == -1:
            print("Failed to update throttle!")
        else:
            print(f"Updated throttle to {throttle} us")
            return True
    else:
        print("Failed to read acknowledgement!")
    
    return False


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
    while duty_cycle_cmd < 1800:
        update_desired_throttle(serial_arduino, duty_cycle_cmd)
        duty_cycle_cmd += 100
        time.sleep(2.7)

    while duty_cycle_cmd >= 1000:
        update_desired_throttle(serial_arduino, duty_cycle_cmd)
        duty_cycle_cmd -= 100
        time.sleep(2.7)

except KeyboardInterrupt:
    print("Wait for motor stop ...")
    while update_desired_throttle(serial_arduino, 1000) == False:
        pass

    print("Throttle at zero.")
    time.sleep(1)

    serial_arduino.close()
    print("Graceful exit.")
