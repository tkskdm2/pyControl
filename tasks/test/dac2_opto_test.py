from pyControl.utility import *
import pyb
from devices import off

# Use direct DAC channel 2 so output test does not depend on the selected hardware definition.
_dac2 = pyb.DAC(2)
_pulse_timer = pyb.Timer(6)

states = ["pulsing"]
events = []

initial_state = "pulsing"

# 8-bit DAC value for 0.1 V on a 0-3.3 V range.
v.pulse_voltage = 0.1
v.pulse_on_value = int(round((v.pulse_voltage / 3.3) * 255))
_pulse_period_ms = 2000
_pulse_width_ms = 100
_pulse_buf = None


def run_start():
    global _pulse_buf
    # Build one full cycle: 100 ms high followed by 1900 ms low.
    _pulse_buf = bytearray(
        [v.pulse_on_value] * _pulse_width_ms + [0] * (_pulse_period_ms - _pulse_width_ms)
    )
    _pulse_timer.init(freq=1000)  # 1 sample per ms.
    _dac2.write_timed(_pulse_buf, _pulse_timer, mode=pyb.DAC.CIRCULAR)
    print("DAC2 pulses started: 100 ms at 0.5 Hz, on_value={}".format(v.pulse_on_value))


def run_end():
    _pulse_timer.deinit()
    _dac2.write(0)
    off()


def pulsing(event):
    pass
