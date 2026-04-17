from devices import *
import pyb

board = Breakout_1_2()

# Port 2 outputs for reward valve / indicator tests.
GateLED = Digital_output(board.port_2.POW_A)
RewardValve = Digital_output(board.port_2.POW_B)

# Port 3 digital outputs for state signal tests.
Code_data = Digital_output(board.port_3.DIO_A)
Code_clock = Digital_output(board.port_3.DIO_B)

# DAC1 audio output using pyControl Audio_board wrapper.
Speaker = Audio_board(board.port_3)

# DAC2 analog output for optogenetic pulse tests.
OptoLED = pyb.DAC(board.port_4.DAC, bits=12)

# BNC1 digital output for camera trigger tests.
CamTrigger = Digital_output(board.BNC_1)

# BNC2 analog input for treadmill velocity tests.
TreadmillVelocity = Analog_input(pin=board.BNC_2, name="treadmill_velocity", sampling_rate=100)
