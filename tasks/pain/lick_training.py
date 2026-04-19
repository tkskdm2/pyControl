from pyControl.utility import *

try:
    import hardware_definition as hw
except ImportError:
    from devices import Analog_input, Breakout_1_2, Digital_input, Digital_output, off

    class _HW:
        pass

    hw = _HW()
    board = Breakout_1_2()
    hw.RewardLED = Digital_output(board.port_2.POW_A)
    hw.RewardValve = Digital_output(board.port_2.POW_B)
    hw.Lick = Digital_input(board.port_6.DIO_A)
    hw.TreadmillVelocity = Analog_input(pin=board.BNC_2, name="treadmill_velocity", sampling_rate=100)
    hw.off = off


states = ["ITI", "LickWait", "Reward"]

events = [
    "iti_timer",
    "lickwait_timeout",
    "lickwait_check",
    "reward_end",
    "reward_valve_off",
    "reward_check",
    "session_timer",
]

initial_state = "ITI"

# Parameters (GUI editable).
v.ITI_min = 3.0  # seconds
v.ITI_max = 6.0  # seconds
v.LickWait_length = 3.0  # seconds
v.Reward_length = 1.0  # seconds
v.RewardSize = 50  # ms

# GUI counters / metrics.
v.nReward = 0
v.nMaxConsectiveReward = 0

# Internal variables.
v._poll_interval_ms = 10
v._last_lick_value = 0
v._reward_had_lick = False
v._consecutive_reward = 0


def run_start():
    set_timer("session_timer", 30 * minute)
    v._last_lick_value = hw.Lick.value()
    print_variables(["nReward", "nMaxConsectiveReward"])


def run_end():
    hw.RewardLED.off()
    hw.RewardValve.off()
    if hasattr(hw, "off"):
        hw.off()


def ITI(event):
    if event == "entry":
        hw.RewardLED.off()
        v._consecutive_reward = 0
        iti_ms = randint(int(v.ITI_min * 1000), int(v.ITI_max * 1000))
        set_timer("iti_timer", iti_ms * ms)
    elif event == "iti_timer":
        goto_state("LickWait")


def LickWait(event):
    if event == "entry":
        hw.RewardLED.on()
        set_timer("lickwait_timeout", int(v.LickWait_length * 1000) * ms)
        _schedule_lickwait_check()
    elif event == "lickwait_check":
        if _lick_onset():
            goto_state("Reward")
        else:
            _schedule_lickwait_check()
    elif event == "lickwait_timeout":
        goto_state("ITI")
    elif event == "exit":
        disarm_timer("lickwait_check")
        disarm_timer("lickwait_timeout")


def Reward(event):
    if event == "entry":
        hw.RewardLED.off()
        hw.RewardValve.on()
        set_timer("reward_valve_off", int(v.RewardSize) * ms)
        set_timer("reward_end", int(v.Reward_length * 1000) * ms)
        v._reward_had_lick = False
        v.nReward += 1
        v._consecutive_reward += 1
        if v._consecutive_reward > v.nMaxConsectiveReward:
            v.nMaxConsectiveReward = v._consecutive_reward
        print_variables(["nReward", "nMaxConsectiveReward"])
        _check_training_completion()
        _schedule_reward_check()
    elif event == "reward_check":
        if _lick_onset():
            v._reward_had_lick = True
        _schedule_reward_check()
    elif event == "reward_valve_off":
        hw.RewardValve.off()
    elif event == "reward_end":
        if v._reward_had_lick:
            goto_state("LickWait")
        else:
            goto_state("ITI")
    elif event == "exit":
        disarm_timer("reward_check")
        disarm_timer("reward_valve_off")
        disarm_timer("reward_end")
        hw.RewardValve.off()


def all_states(event):
    if event == "session_timer":
        stop_framework()


def _schedule_lickwait_check():
    set_timer("lickwait_check", v._poll_interval_ms * ms)


def _schedule_reward_check():
    set_timer("reward_check", v._poll_interval_ms * ms)


def _lick_onset():
    lick_value = hw.Lick.value()
    lick_onset = bool(lick_value and not v._last_lick_value)
    v._last_lick_value = lick_value
    return lick_onset


def _check_training_completion():
    if v._consecutive_reward >= 50:
        stop_framework()
