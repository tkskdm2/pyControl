from pyControl.utility import *

try:
    import hardware_definition as hw
except ImportError:
    from devices import Analog_input, Breakout_1_2, off

    class _HW:
        pass

    hw = _HW()
    board = Breakout_1_2()
    hw.bnc2_in = Analog_input(pin=board.BNC_2, name="treadmill_velocity", sampling_rate=100)
    hw.off = off

states = ["monitoring"]
events = []

initial_state = "monitoring"


def run_start():
    print("BNC2 analog input streaming at 100 Hz: treadmill_velocity")


def run_end():
    hw.off()


def monitoring(event):
    if event == "entry":
        print("Monitoring started.")
