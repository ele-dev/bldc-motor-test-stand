import easy_scpi as scpi

class PowerSupply( scpi.Instrument ):
    def __init__(self, port = "/dev/ttyUSB0", baudrate = 115200):
        super().__init__( 
            port = port,
            baud_rate = baudrate, 
            timeout = 5000,
            read_termination = '\n', 
            write_termination = '\n' 
        )

        # connect to power supply
        self.connect()
        print(f"Connected to power supply at {self.port}.")

    # -------------------------- Control related -----------------------------

    def on(self):
        """
        Turns on the DC output terminal.
        """
        self.output.state('on')
        
    def off(self):
        """
        Turns off the DC output terminal.
        """
        self.output.state('off')

    @property        
    def voltage_setpoint(self):
        """
        Returns the voltage setpoint in volts.
        """
        return float(self.source.volt.level())
    
    @voltage_setpoint.setter
    def voltage_setpoint(self, volts):
        """
        Sets the voltage setpoint in volts.
        """
        self.source.volt.level(volts)
    
    @property
    def current_setpoint(self):
        """
        Returns the current setpoint in amps.
        """
        return float(self.source.current.level())
        
    @current_setpoint.setter
    def current_setpoint(self, amps):
        """
        Sets the current setpoint in amps.
        """
        self.source.current.level(amps)

    # -------------------------- Measurement related -----------------------------

    @property
    def voltage(self):
        """
        Returns the measured DC output voltage in volts.
        """
        return float(self.measure.voltage.dc())
    
    @property
    def current(self):
        """
        Returns the measured DC output current in amps.
        """
        return float(self.measure.current.dc())

    @property
    def power(self):
        """
        Returns the measured DC output power in watts.
        """
        return float(self.measure.power.dc())
    
    def measure_all(self) -> str:
        """
        Returns more detailed status info about the DC output stage
        including voltage, current, power, OV/OC/OT events, CV/CC mode and failure states.
        The the fields are returned in a comma-separated string format.
        """
        return self.measure.all.info()