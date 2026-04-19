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


states = ["ITI", "Gate", "Reward"]

events = [
    "iti_timer",
    "gate_check",
    "reward_check",
    "reward_valve_off",
    "session_timer",
]

initial_state = "ITI"

# Parameters (GUI editable).
v.ITI_min = 3.0  # seconds
v.ITI_max = 6.0  # seconds
v.Gate_length = 1.5  # seconds
v.Threadmill_threshold = 8  # threshold units from treadmill analog channel
v.NoLick_length = 0.4  # seconds
v.RewardSize = 50  # ms

# GUI counters / metrics.
v.nGateEntry = 0
v.nGateSuccess = 0
v.GateSuccessRate = 0.0
v.nMaxConsectiveSuccess = 0

# Internal variables.
v._poll_interval_ms = 10
v._gate_entry_time = 0
v._last_lick_time = -1000000000
v._consecutive_success = 0
v._last_lick_value = 0
v._latest_treadmill_sample = 0


def run_start():
    set_timer("session_timer", 30 * minute)
    v._last_lick_value = hw.Lick.value()
    print_variables(["nGateEntry", "nGateSuccess", "GateSuccessRate", "nMaxConsectiveSuccess"])


def run_end():
    hw.RewardLED.off()
    hw.RewardValve.off()
    if hasattr(hw, "off"):
        hw.off()


def ITI(event):
    if event == "entry":
        iti_ms = randint(int(v.ITI_min * 1000), int(v.ITI_max * 1000))
        set_timer("iti_timer", iti_ms * ms)
    elif event == "iti_timer":
        goto_state("Gate")


def Gate(event):
    if event == "entry":
        v.nGateEntry += 1
        v._gate_entry_time = get_current_time()
        _update_lick_and_speed(v._gate_entry_time)
        _schedule_gate_check()
    elif event == "gate_check":
        now = get_current_time()
        _update_lick_and_speed(now)

        if v._latest_treadmill_sample >= int(v.Threadmill_threshold):
            _register_gate_result(success=False)
            goto_state("ITI")
            return

        gate_complete = (now - v._gate_entry_time) >= int(v.Gate_length * 1000)
        no_lick_window_ok = (now - v._last_lick_time) >= int(v.NoLick_length * 1000)
        if gate_complete and no_lick_window_ok:
            _register_gate_result(success=True)
            goto_state("Reward")
        else:
            _schedule_gate_check()


def Reward(event):
    if event == "entry":
        hw.RewardLED.on()
        hw.RewardValve.on()
        set_timer("reward_valve_off", int(v.RewardSize) * ms)
        _schedule_reward_check()
    elif event == "reward_valve_off":
        hw.RewardValve.off()
    elif event == "reward_check":
        now = get_current_time()
        lick_onset = _update_lick_and_speed(now)
        if lick_onset:
            goto_state("ITI")
        else:
            _schedule_reward_check()
    elif event == "exit":
        hw.RewardLED.off()
        hw.RewardValve.off()


def all_states(event):
    if event == "session_timer":
        stop_framework()


def _schedule_gate_check():
    set_timer("gate_check", v._poll_interval_ms * ms)


def _schedule_reward_check():
    set_timer("reward_check", v._poll_interval_ms * ms)


def _update_lick_and_speed(now):
    v._latest_treadmill_sample = hw.TreadmillVelocity.ADC.read()
    lick_value = hw.Lick.value()
    lick_onset = False
    if lick_value and not v._last_lick_value:
        v._last_lick_time = now
        lick_onset = True
    v._last_lick_value = lick_value
    return lick_onset


def _register_gate_result(success):
    if success:
        v.nGateSuccess += 1
        v._consecutive_success += 1
        if v._consecutive_success > v.nMaxConsectiveSuccess:
            v.nMaxConsectiveSuccess = v._consecutive_success
    else:
        v._consecutive_success = 0

    if v.nGateEntry > 0:
        v.GateSuccessRate = v.nGateSuccess / v.nGateEntry
    else:
        v.GateSuccessRate = 0.0

    print_variables(["nGateEntry", "nGateSuccess", "GateSuccessRate", "nMaxConsectiveSuccess"])
    _check_training_completion()


def _check_training_completion():
    if v.Gate_length < 3.0:
        return

    if v._consecutive_success >= 20 or v.GateSuccessRate >= 0.7:
        stop_framework()
