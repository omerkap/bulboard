import RPi.GPIO as GPIO
import math

FLIP_PAIRS = 0

#BOARD_ASSIGNMENT = [50,50,50,37]

class SRDriver(object):

    # Usage example:
    # For a 17*11 board use total_num_of_regs = 187
    # For a bus of 50 wires connected to a board use board_num_of_active_regs = 50
    # If we soldered the board in such a way that the first wire is connected to
    # the 7th reg, use board_starting_reg = 6
    def __init__(self,board_num_of_regs,board_num_of_active_regs,board_starting_reg,total_num_of_regs):
        self._num_of_boards = int(total_num_of_regs)/int(board_num_of_active_regs)
        self._flip_pairs = flip_pairs
        self._board_starting_reg = board_starting_reg
        self._board_num_of_regs = board_num_of_regs

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
