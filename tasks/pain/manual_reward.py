from pyControl.utility import *
from devices import Breakout_1_2, Digital_output


import hardware_definition as hw

# GateLED and RewardValve are normally provided by the loaded hardware definition.
# If they are not available, define a local fallback using the same channels.
try:
    GateLED = hw.GateLED
    RewardValve = hw.RewardValve
    v.using_local_hardware_fallback = False
except Exception:
    board = Breakout_1_2()
    RewardLED = Digital_output(board.port_2.POW_A)
    RewardValve = Digital_output(board.port_2.POW_B)
    v.using_local_hardware_fallback = True

# Manual reward task.
#
# Trigger the event "manual_reward" from the GUI to deliver one reward:
# 1) RewardLED on for 1 second
# 2) RewardValve on for 0.05 second

states = ["wait_for_trigger", "gate_on", "reward_on"]

events = ["manual_reward"]

initial_state = "wait_for_trigger"

# Variables shown in GUI.
v.button_click_count = 0


def run_start():
    # Show the initial count in GUI/log.
    print_variables(["button_click_count"])
    if v.using_local_hardware_fallback:
        warning("Hardware definition was not loaded; using local fallback for RewardLED/RewardValve.")


def wait_for_trigger(event):
    if event == "manual_reward":
        v.button_click_count += 1
        print_variables(["button_click_count"])
        goto_state("reward_on")


def reward_on(event):
    if event == "entry":
        RewardValve.on()
        timed_goto_state("wait_for_trigger", 50 * ms)
    elif event == "exit":
        RewardValve.off()


def run_end():
    # Ensure outputs are off if the run is stopped mid-sequence.
    GateLED.off()
    RewardValve.off()
