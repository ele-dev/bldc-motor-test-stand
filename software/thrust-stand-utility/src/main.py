from owon_spe import OwonSpePsu

import serial
import time

devices = OwonSpePsu.enumerate_devices()
print(devices)

serial_arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

duty_cycle_cmd = 1000
decoded_line = ""

def update_desired_throttle(ser: serial.Serial, throttle: int) -> None:
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
    else:
        print("Failed to read acknowledgement!")


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

    # simply set constant throttle level and keep it alive
    duty_cycle_cmd = 1200
    while True:    
        update_desired_throttle(serial_arduino, duty_cycle_cmd)
        time.sleep(1.5)

except KeyboardInterrupt:
    print("Wait for motor stop ...")
    while decoded_line.find("Reset throttle to zero.") == -1:
        line = serial_arduino.readline()
        if line:
            decoded_line = line.decode('utf-8', errors='ignore').strip()

    print("Throttle at zero.")
    time.sleep(1)

    serial_arduino.close()
    print("Graceful exit.")
