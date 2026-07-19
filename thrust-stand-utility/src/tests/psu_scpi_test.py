import pyvisa

rm = pyvisa.ResourceManager('@py')

# Open the resource explicitly as a Serial Instrument
inst = rm.open_resource('ASRL/dev/ttyUSB0::INSTR')

# Force common raw serial parameters
inst.baud_rate = 115200        # Match your power supply manual's default
inst.data_bits = 8
inst.stop_bits = pyvisa.constants.StopBits.one
inst.parity = pyvisa.constants.Parity.none

# Disabling flow control completely fixes most USB-to-Serial bridge hangs
inst.set_visa_attribute(pyvisa.constants.VI_ATTR_ASRL_FLOW_CNTRL, pyvisa.constants.VI_ASRL_FLOW_NONE)

inst.write_termination = '\n'
inst.read_termination = '\n'
inst.timeout = 1000          # Bump timeout to 5 seconds to give it breathing room

print("Sending *IDN?...")
print(inst.query('*IDN?'))