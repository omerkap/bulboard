import sys
sys.path.append(r'../')
from SR_Board.sr_driver import SRDriver
from screen_usages.sovsov import Sovsov
from time import sleep
import os
try:
    import matplotlib.pyplot as plt
except ImportError as ex:
    print ex


class HanukkahRunner(object):
    def __init__(self):
        self.phi = 40
        self.dtheta_self = 5
        self.dtheta_inclined = 10
        self.shift_origin = (0,0,0)
        self.delay = 0.01
        self.sr_driver = SRDriver(board_num_of_regs=56,
                                 num_of_boards=4,
                                 clk_pin=11,
                                 store_pin=12,
                                 data_pin=13,
                                 index_map_file=os.path.join('..', 'SR_Board', 'index_map.csv'),
                                 is_simulated=True)
        self.sovsov = Sovsov(phi = self.phi,
                             dtheta_self = self.dtheta_self,
                             dtheta_inclined = self.dtheta_inclined,
                             shift_origin = self.shift_origin)

    def start(self):
        plt.ion()
        f = plt.figure()
        while True:
            sovsov_data = self.sovsov.get_next_step()
            self.sr_driver.draw(sovsov_data)
            f.clf()
            plt.imshow(sovsov_data, cmap='hot')
            f.canvas.draw()
            sleep(self.delay)

if __name__ == '__main__':
    hanukkah_runner = HanukkahRunner()
    hanukkah_runner.start()