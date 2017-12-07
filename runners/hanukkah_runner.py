from SR_Board.sr_driver import SRDriver
from time import sleep
import os

class HanukkahRunner(object):
    def __init__(self):
        self.phi = 0;
        self.dtheta_self = 0
        self.dtheta_inclined = 0
        self.shift_origin = (0,0,0)
        self.delay = 0.1
        self.sr_driver = SRDriver(board_num_of_regs=56,
                                 num_of_boards=4,
                                 clk_pin=11,
                                 store_pin=12,
                                 data_pin=13,
                                 index_map_file=os.path.join('..', 'SR_Board', 'index_map.csv'),
                                 is_simulated=True)
        self.sovsov = sovsov(phi = self.phi,
                             dtheta_self = self.dtheta_self,
                             dtheta_inclined = self.dtheta_inclined,
                             shift_origin = self.shift_origin)

    def run(self):
        while True:
            sovsov_data = self.sovsov.get_next_step()
            self.sr_driver.draw(sovsov_data)
            sleep(self.delay)