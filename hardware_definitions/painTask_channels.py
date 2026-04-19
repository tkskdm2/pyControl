from devices import *
import pyb

board = Breakout_1_2()

# Port 2 outputs for reward valve / LED.
RewardLED = Digital_output(board.port_2.POW_A)
RewardValve = Digital_output(board.port_2.POW_B)

# Port 3 digital outputs for state code and clock.
CodeData = Digital_output(board.port_3.DIO_A)
CodeClock = Digital_output(board.port_3.DIO_B)

# Port 6 digital inputs for lick detection.
Lick = Digital_input(board.port_6.DIO_A)

# DAC1 audio output using pyControl Audio_board wrapper.
Speaker = Audio_board(board.port_3)

# DAC2 analog output for optogenetic stimulus.
OptoLED = pyb.DAC(board.port_4.DAC, bits=12)

# BNC1 digital output for camera trigger.
CamTrigger = Digital_output(board.BNC_1)

# BNC2 analog input for treadmill velocity.
TreadmillVelocity = Analog_input(pin=board.BNC_2, name="treadmill_velocity", sampling_rate=100)
