import serial

class ArduinoController:
    """Small wrapper for the USB-serial communication with arduino controlling the motor
    ESC and sensors.
    """

    DEFAULT_BAUDRATE = 115200
    DEFAULT_TIMEOUT = 1.0
    DEFAULT_WRITE_TIMEOUT = 1.0
    CH340_VID = 0x1A86
    CH340_PID = 0x7523

    def __init__(
        self,
        port: str | None = None,
        baudrate: int = DEFAULT_BAUDRATE,
        timeout: float = DEFAULT_TIMEOUT,
        write_timeout: float = DEFAULT_WRITE_TIMEOUT,
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.write_timeout = write_timeout
        self._serial: serial.Serial | None = None
        self.open()

        init_message = ""
        print(f"Waiting for controller on {self.port} ...")
        while init_message.find("Setup complete.") == -1:
            init_message = self._read_line()

        print("Controller ready to receive commands.\n")

    def __del__(self) -> None:
        self.close()

    def open(self) -> None:
        self._serial = serial.Serial(
            self.port,
            baudrate=self.baudrate,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=self.timeout,
            write_timeout=self.write_timeout
        )

    def close(self) -> None:
        if self._serial and self._serial.is_open:
            self._serial.close()

    def _send_line(self, line: str) -> None:
        bytes_to_send = (line + "\n").encode('utf-8')
        self._serial.write(bytes_to_send)

    def _read_line(self) -> str:
        bytes_read = self._serial.readline()
        return bytes_read.decode('utf-8', errors='ignore').strip()
    
    def get_produced_thrust(self) -> float:
        # query the thrust measurement
        self._send_line("GET_THRUST")

        response = self._read_line()
        if response.startswith("THRUST="):
            return float(response.removeprefix("THRUST="))
        else:
            print(f"ERROR: {response}")

        return -1000.0
    
    def update_desired_throttle(self, throttle: int) -> bool:
        # clip to allowed throttle range
        if throttle > 2000:
            throttle = 2000
        if throttle < 1000:
            throttle = 1000

        self._send_line(f"SET_THROTTLE {throttle}")

        # wait for acknowledgement
        response = self._read_line()
        if response.find("OK: Throttle set to " + str(throttle)) != -1:
            return True
        
        return False
