from devices import *
import pyb

board = Breakout_1_2()

# Port 2 outputs for reward valve / indicator tests.
port2_pow_a = Digital_output(board.port_2.POW_A)
port2_pow_b = Digital_output(board.port_2.POW_B)

# Port 3 digital outputs for state signal tests.
port3_dio_a = Digital_output(board.port_3.DIO_A)
port3_dio_b = Digital_output(board.port_3.DIO_B)

# DAC1 audio output using pyControl Audio_board wrapper.
speaker = Audio_board(board.port_3)

# DAC2 analog output for optogenetic pulse tests.
dac2_out = pyb.DAC(board.port_4.DAC, bits=12)

# BNC1 digital output for camera trigger tests.
bnc1_out = Digital_output(board.BNC_1)

# BNC2 analog input for treadmill velocity tests.
bnc2_in = Analog_input(pin=board.BNC_2, name="treadmill_velocity", sampling_rate=100)
