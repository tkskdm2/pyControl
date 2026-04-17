from pyControl.utility import *

try:
    import hardware_definition as hw
except ImportError:
    from devices import Breakout_1_2, Digital_output, off

    class _HW:
        pass

    hw = _HW()
    board = Breakout_1_2()
    hw.port2_pow_a = Digital_output(board.port_2.POW_A)
    hw.port2_pow_b = Digital_output(board.port_2.POW_B)
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
        set_timer("toggle_outputs", 1 * second)
    elif event == "toggle_outputs":
        v.phase_a_on = not v.phase_a_on
        _set_outputs()
        set_timer("toggle_outputs", 1 * second)


def _set_outputs():
    if v.phase_a_on:
        hw.port2_pow_a.on()
        hw.port2_pow_b.off()
    else:
        hw.port2_pow_a.off()
        hw.port2_pow_b.on()
