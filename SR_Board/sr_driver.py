try:
    import RPi.GPIO as GPIO
except ImportError as ex:
    print ex
from time import sleep
import re
import pprint


class SRDriver(object):

    # Usage example:
    # For a 17*11 board use total_num_of_regs = 187
    # For a bus of 50 wires connected to a board use board_num_of_active_regs = 50
    # If we soldered the board in such a way that the first wire is connected to
    # the 7th reg, use board_starting_reg = 6
    def __init__(self, board_num_of_regs, num_of_boards,
                 clk_pin, store_pin, data_pin, index_map_file, is_simulated=False):
        self._index_map = self._read_csv(index_map_file)
        self._num_of_boards = num_of_boards
        self._board_num_of_regs = board_num_of_regs
        self.clk_pin = clk_pin
        self.store_pin = store_pin
        self.data_pin = data_pin
        self.num_of_lines = len(self._index_map)
        self.num_of_columns = len(self._index_map[0])
        self.simulated = is_simulated
        self.data = [0] * (self._num_of_boards * self._board_num_of_regs)
        for i in range(0, len(self.data)):
            self.data[i] = 0

        if is_simulated is False:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.data_pin, GPIO.OUT)
            GPIO.setup(self.store_pin, GPIO.OUT)
            GPIO.setup(self.clk_pin, GPIO.OUT)

            GPIO.output(self.data_pin, 0)
            GPIO.output(self.store_pin, 0)
            GPIO.output(self.clk_pin, 0)

    def _read_csv(self,index_map_file):
        file = open(index_map_file)
        index_map = []
        line_format_str = "(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)"
        line_format = re.compile(line_format_str)
        for line in file:
            re_result = line_format.match(line)
            index_map_line = []
            for i in range(1, 12):
                index_map_line.extend([int(re_result.group(i))])
            index_map.append(index_map_line)
        return index_map

    def load_array(self,picture):
        for i in range(0,self.num_of_lines):
            for j in range(0,self.num_of_columns):
                self.data[self._index_map[i][j]] = picture[i][j]

    def shift_data(self, data):
        """
        shift data into register, data should be 0, 1
        :param data:
        :return:
        """
        if self.simulated is False:
            GPIO.output(self.data_pin, data)
            sleep(0.00005)
            GPIO.output(self.clk_pin, 1)
            sleep(0.00001)
            GPIO.output(self.clk_pin, 0)
            sleep(0.00001)

    def load_output(self):
        """
        load shift register data into output latches
        :return:
        """
        if self.simulated is False:
            GPIO.output(self.store_pin, 1)
            sleep(0.00001)
            GPIO.output(self.store_pin, 0)
            sleep(0.00001)

    def write_data(self):
        for d in self.data:
            self.shift_data(data=d)
        self.load_output()

    def draw(self, pic):
        self.load_array(picture=pic)
        self.write_data()

    def test_board(self):
        for i in range(0, self.num_of_lines):
            for j in range(0, self.num_of_columns):
                pic = [self.num_of_columns * [0] for k in range(0, self.num_of_lines)]
                pic[i][j] = 1
                self.load_array(picture=pic)
                self.write_data()
                print '{},{}'.format(i,j)
                sleep(0.5)

    def test_board_no_pic(self):
        for d in range(2):
            for i in range(0, self._board_num_of_regs * self._num_of_boards):
                print 'line {}'.format(i)
                self.shift_data(d)
        
            self.load_output()
            sleep(2)

    def test_blink(self):                
        pic = [self.num_of_columns * [0] for k in range(0, self.num_of_lines)]
        self.load_array(picture=pic)
        self.write_data()
        sleep(0.2)
        pic = [self.num_of_columns * [1] for k in range(0, self.num_of_lines)]
        self.load_array(picture=pic)
        self.write_data()
        sleep(0.2)

    def light_line(self, line):
        pic = []
        for i in range(self.num_of_lines):
            if i == line:
                pic.append(self.num_of_columns * [1])
            else:
                pic.append(self.num_of_columns * [0])
        return pic

    def light_column(self, c):
        pic = []
        for i in range(self.num_of_lines):
            line = [0] * self.num_of_columns
            line[c] = 1
            pic.append(line)
        return pic
    
    def test_columns(self):
        for i in range(self.num_of_columns):
            pic = self.light_column(i)
            self.load_array(pic)
            self.write_data()
            sleep(1)
 
    def test_lines(self):
        for i in range(self.num_of_lines):
            print 'line: {}'.format(i)

            pic = self.light_line(line=i)
            pprint.pprint(pic)
            self.load_array(pic)
            self.write_data()
            sleep(1)


if __name__ == '__main__':
    driver = SRDriver(board_num_of_regs=56,
                      num_of_boards=4,
                      clk_pin=11,
                      store_pin=12,
                      data_pin=13,
                      index_map_file="index_map.csv")

    
    while True:  # for testing just start running the pixel
        #driver.test_board()
        #driver.test_lines()
        #driver.test_columns()  
        driver.test_board_no_pic()
    '''
    while True:
        a = raw_input("press 'd' for demo, 'q' for quit")
        if a == 'd':
            driver.test_board()
        elif a == 'q':
            exit(0)
    '''
