import RPi.GPIO as GPIO
import math
from time import sleep

FLIP_PAIRS = 0

#BOARD_ASSIGNMENT = [50,50,50,37]

class SRDriver(object):

    # Usage example:
    # For a 17*11 board use total_num_of_regs = 187
    # For a bus of 50 wires connected to a board use board_num_of_active_regs = 50
    # If we soldered the board in such a way that the first wire is connected to
    # the 7th reg, use board_starting_reg = 6
    def __init__(self, board_num_of_regs, board_num_of_active_regs, board_starting_reg, total_num_of_regs, clk_pin, store_pin, data_pin):
        self._num_of_boards = int(total_num_of_regs)/int(board_num_of_active_regs)
        self._flip_pairs = flip_pairs
        self._board_starting_reg = board_starting_reg
        self._board_num_of_regs = board_num_of_regs
        self.clk_pin = clk_pin
        self.store_pin = store_pin
        self.data_pin = data_pin

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.data_pin, GPIO.OUT)
        GPIO.setup(self.store_pin, GPIO.OUT)
        GPIO.setup(self.clk_pin, GPIO.OUT)

        GPIO.output(self.data_pin, 0)
        GPIO.output(self.store_pin, 0)
        GPIO.output(self.clk_pin, 0)

    def write_to_boards(self,pic_arr):
        flat_pic_arr = [x for sublist in pic_arr for x in sublist]
        # -------------> I stopped here:
        #send sublists to process board and create a bit sequence using list.extend for all outputs

    def process_board(self,data):
        return_val = [0 for x in range(_board_num_of_regs)]
        for i in range(len(data)):
            return_val[_board_starting_reg + i] = data[i]
        if _flip_pairs:
            # The following assumes _board_num_of_regs is even
            for i in range(len(data)/2):
                temp = return_val[i*2]
                return_val[i*2] = return_val[i*2+1]
                return_val[i*2+1] = temp
        return return_val

    def clear_register(self):
        """
        write 0 to all registers
        :return:
        """
        for i in range(self._num_of_boards * 50):
            self.shift_data(0)

        self.load_output()
        self.state = [0] * self.size

    def shift_data(self, data):
        """
        shift data into register, data should be 0, 1
        :param data:
        :return:
        """
        if data == 1:
            GPIO.output(self.data_pin, 1)
        else:
            GPIO.output(self.data_pin, 0)
        GPIO.output(self.clk_pin, 1)
        GPIO.output(self.clk_pin, 0)
        # return ser to 0, if the clocks togle, 0 will be inserted
        GPIO.output(self.data_pin, 0)

    def load_output(self):
        """
        load shift register data into output latches
        :return:
        """
        GPIO.output(self.store_pin, 1)
        GPIO.output(self.store_pin, 0)

    def write_ones(self):
        self.write_list(list=[1]* 50)

    def write_zeros(self):
        self.write_list(list=[0] * 50)

    def write_list(self, list):
        for d in list:
            self.shift_data(data=d)
        self.load_output()

    def blink(self):
        for i in range(10):
            self.write_ones()
            sleep(1)
            self.write_zeros()
            sleep(1)