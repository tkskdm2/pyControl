from pyControl.utility import *

try:
    import hardware_definition as hw
except ImportError:
    from devices import Breakout_1_2, Digital_output, off

    class _HW:
        pass

    hw = _HW()
    board = Breakout_1_2()
    hw.bnc1_out = Digital_output(board.BNC_1)
    hw.off = off

states = ["active_burst", "inter_burst_interval"]
events = ["pulse_end", "next_pulse", "burst_complete"]

initial_state = "active_burst"

v.pulse_width = 1 * ms
v.pulse_period = 100 * ms
v.pulses_per_burst = 50


def run_start():
    v.pulse_count = 0


def run_end():
    hw.bnc1_out.off()
    hw.off()


def active_burst(event):
    if event == "entry":
        v.pulse_count = 0
        _start_pulse()
    elif event == "pulse_end":
        hw.bnc1_out.off()
        if v.pulse_count < v.pulses_per_burst:
            set_timer("next_pulse", v.pulse_period - v.pulse_width)
        else:
            set_timer("burst_complete", 0 * ms)
    elif event == "next_pulse":
        _start_pulse()
    elif event == "burst_complete":
        goto_state("inter_burst_interval")
    elif event == "exit":
        disarm_timer("pulse_end")
        disarm_timer("next_pulse")
        disarm_timer("burst_complete")
        hw.bnc1_out.off()


def inter_burst_interval(event):
    if event == "entry":
        timed_goto_state("active_burst", 5 * second)


def _start_pulse():
    v.pulse_count += 1
    hw.bnc1_out.on()
    set_timer("pulse_end", v.pulse_width)
