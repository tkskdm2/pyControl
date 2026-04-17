from pyControl.utility import *

try:
    import hardware_definition as hw
except ImportError:
    from devices import Breakout_1_2, Digital_output, off

    class _HW:
        pass

    hw = _HW()
    board = Breakout_1_2()
    hw.port3_dio_a = Digital_output(board.port_3.DIO_A)
    hw.port3_dio_b = Digital_output(board.port_3.DIO_B)
    hw.off = off

states = ["alternating"]
events = ["toggle_outputs"]

initial_state = "alternating"


def run_start():
    v.phase_a_on = True


def run_end():
    hw.off()


def alternating(event):
    if event == "entry":
        _set_outputs()
        set_timer("toggle_outputs", 500 * ms)
    elif event == "toggle_outputs":
        v.phase_a_on = not v.phase_a_on
        _set_outputs()
        set_timer("toggle_outputs", 500 * ms)


def _set_outputs():
    if v.phase_a_on:
        hw.port3_dio_a.on()
        hw.port3_dio_b.off()
    else:
        hw.port3_dio_a.off()
        hw.port3_dio_b.on()
