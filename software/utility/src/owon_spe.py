from __future__ import annotations
from dataclasses import dataclass

import serial
from serial.tools import list_ports


@dataclass(frozen=True)
class PsuDevice:
    """A serial device that may be an OWON SPE-series PSU."""

    port: str
    description: str
    hwid: str
    vid: int | None = None
    pid: int | None = None


@dataclass(frozen=True)
class PsuReading:
    """Measured PSU output values."""

    voltage: float
    current: float

    @property
    def power(self) -> float:
        return self.voltage * self.current


class OwonSpePsu:
    """Small wrapper for the tested OWON SPE8205 USB-serial SCPI subset.

    Verified serial settings: 115200 baud, 8 data bits, no parity, 1 stop bit,
    no flow control, newline-terminated SCPI commands.
    """

    DEFAULT_BAUDRATE = 115200
    DEFAULT_TIMEOUT = 1.0
    DEFAULT_WRITE_TIMEOUT = 1.0
    CH340_VID = 0x1A86
    CH340_PID = 0x7523

    def __init__(
        self,
        port: str | None = None,
        *,
        baudrate: int = DEFAULT_BAUDRATE,
        timeout: float = DEFAULT_TIMEOUT,
        write_timeout: float = DEFAULT_WRITE_TIMEOUT,
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.write_timeout = write_timeout
        self._serial: serial.Serial | None = None

    @staticmethod
    def enumerate_devices() -> list[PsuDevice]:
        """Return connected serial devices matching the verified CH340 USB adapter."""
        devices: list[PsuDevice] = []
        for port in list_ports.comports():
            if port.vid == OwonSpePsu.CH340_VID and port.pid == OwonSpePsu.CH340_PID:
                devices.append(
                    PsuDevice(
                        port=port.device,
                        description=port.description,
                        hwid=port.hwid,
                        vid=port.vid,
                        pid=port.pid,
                    )
                )
        return devices

    @classmethod
    def first_available_port(cls) -> str:
        """Return the first matching PSU serial port, or raise if none is present."""
        devices = cls.enumerate_devices()
        if not devices:
            raise RuntimeError("No CH340-backed OWON SPE PSU serial device found")
        return devices[0].port

    @classmethod
    def open_first(cls, **kwargs) -> "OwonSpePsu":
        """Create and open a PSU session for the first enumerated device."""
        psu = cls(cls.first_available_port(), **kwargs)
        psu.open()
        return psu

    def open(self) -> "OwonSpePsu":
        """Open the serial session if it is not already open."""
        if self._serial and self._serial.is_open:
            return self
        if not self.port:
            self.port = self.first_available_port()
        self._serial = serial.Serial(
            self.port,
            baudrate=self.baudrate,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=self.timeout,
            write_timeout=self.write_timeout,
        )
        return self

    def close(self) -> None:
        """Close the serial session."""
        if self._serial and self._serial.is_open:
            self._serial.close()

    def __enter__(self) -> "OwonSpePsu":
        return self.open()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @property
    def is_open(self) -> bool:
        return bool(self._serial and self._serial.is_open)

    def _write(self, command: str) -> None:
        """Send a newline-terminated command without requiring a response."""
        self._send(command, expect_response=False)

    def _query(self, command: str) -> str:
        """Send a newline-terminated query and return the stripped response."""
        return self._send(command, expect_response=True)

    def _send(self, command: str, *, expect_response: bool) -> str:
        self.open()
        assert self._serial is not None
        if hasattr(self._serial, "reset_input_buffer"):
            self._serial.reset_input_buffer()
        wire = command.rstrip("\r\n") + "\n"
        self._serial.write(wire.encode("ascii"))
        self._serial.flush()
        if not expect_response:
            return ""
        return self._serial.read(512).decode(errors="replace").strip()

    def identify(self) -> str:
        return self._query("*IDN?")

    def system_version(self) -> str:
        return self._query("SYST:VERS?")

    def error_status(self) -> str:
        return self._query("SYST:ERR?")

    @property
    def voltage_setpoint(self) -> float:
        return float(self._query("VOLT?"))

    @voltage_setpoint.setter
    def voltage_setpoint(self, volts: float) -> None:
        self._write(f"VOLT {volts:.3f}")

    @property
    def current_limit(self) -> float:
        return float(self._query("CURR?"))

    @current_limit.setter
    def current_limit(self, amps: float) -> None:
        self._write(f"CURR {amps:.3f}")

    @property
    def output_enabled(self) -> bool:
        return self._query("OUTP?").upper() == "ON"

    @output_enabled.setter
    def output_enabled(self, enabled: bool) -> None:
        self._write("OUTP ON" if enabled else "OUTP OFF")

    def enable_output(self) -> None:
        self.output_enabled = True

    def disable_output(self) -> None:
        self.output_enabled = False

    @property
    def measured_voltage(self) -> float:
        return float(self._query("MEAS:VOLT?"))

    @property
    def measured_current(self) -> float:
        return float(self._query("MEAS:CURR?"))

    @property
    def measured_power(self) -> float:
        return float(self._query("MEAS:POW?"))

    def measure_all(self) -> PsuReading:
        voltage, current = _parse_csv_floats(self._query("MEAS:ALL?"), count=2)
        return PsuReading(voltage=voltage, current=current)


def _parse_csv_floats(value: str, *, count: int) -> tuple[float, ...]:
    parts = [float(part.strip()) for part in value.split(",")]
    if len(parts) != count:
        raise ValueError(f"Expected {count} comma-separated values, got {value!r}")
    return tuple(parts)
