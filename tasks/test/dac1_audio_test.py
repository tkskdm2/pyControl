from pyControl.utility import *
import math
import pyb

try:
    import hardware_definition as hw
except ImportError:
    from devices import Breakout_1_2, off
    from pyControl.audio import Audio_output

    class _HW:
        pass

    hw = _HW()
    board = Breakout_1_2()
    # Use direct DAC audio output to avoid dependency on I2C audio-board control.
    hw.speaker = Audio_output(channel=board.port_3.DAC)
    hw.off = off

states = ["tone_4khz", "tone_12khz"]
events = []

initial_state = "tone_4khz"

v.audio_volume = 20
v.output_scale = 0.015625
_sine_len = 100
_sine_buf = None


def run_start():
    global _sine_buf
    # Audio_board supports set_volume; direct Audio_output does not.
    if hasattr(hw.speaker, "set_volume"):
        try:
            hw.speaker.set_volume(v.audio_volume)
        except OSError:
            # Continue even if I2C volume control is unavailable.
            print("Warning: set_volume failed, continuing with current hardware volume.")
    # Build a DAC waveform with 25% of full-scale sine magnitude around midpoint.
    _sine_buf = bytearray(
        [128 + int(round(127 * v.output_scale * math.sin(2 * math.pi * i / _sine_len))) for i in range(_sine_len)]
    )


def run_end():
    hw.speaker.off()
    hw.off()


def tone_4khz(event):
    if event == "entry":
        _play_scaled_sine(4000)
        timed_goto_state("tone_12khz", 2 * second)
    elif event == "exit":
        hw.speaker.off()


def tone_12khz(event):
    if event == "entry":
        _play_scaled_sine(12000)
        timed_goto_state("tone_4khz", 2 * second)
    elif event == "exit":
        hw.speaker.off()


def _play_scaled_sine(freq):
    hw.speaker._DAC.write_timed(_sine_buf, pyb.Timer(4, freq=freq * _sine_len), mode=pyb.DAC.CIRCULAR)
