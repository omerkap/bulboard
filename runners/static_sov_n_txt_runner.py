# -*- coding: utf8 -*-
from SR_Board.sr_driver import SRDriver
from screen_usages.sovsov import Sovsov
import time
import os
import numpy as np

from screen_usages.messages_writer import MessagesWriter
import matplotlib.pyplot as plt


class StaticSovNTextRunner(object):
    def __init__(self):
        nun_sov = [[0,0,0,0,0,1,0,0,0,0,0,0],
[0,0,0,0,0,1,0,0,0,0,0,0],
[0,0,1,1,1,1,1,1,1,0,0,0],
[0,0,1,0,0,0,0,0,1,0,0,0],
[0,0,1,0,0,1,1,0,1,0,0,0],
[0,0,1,0,0,0,1,0,1,0,0,0],
[0,0,1,0,0,0,1,0,1,0,0,0],
[0,0,1,0,1,1,1,0,1,0,0,0],
[0,0,0,1,0,0,0,1,0,0,0,0],
[0,0,0,0,1,0,1,0,0,0,0,0],
[0,0,0,0,0,1,0,0,0,0,0,0]]
        gimel_sov = [[0,0,0,0,0,1,0,0,0,0,0,0],
[0,0,0,0,0,1,0,0,0,0,0,0],
[0,0,1,1,1,1,1,1,1,0,0,0],
[0,0,1,0,0,0,0,0,1,0,0,0],
[0,0,1,0,1,1,1,0,1,0,0,0],
[0,0,1,0,0,0,1,0,1,0,0,0],
[0,0,1,0,0,1,1,0,1,0,0,0],
[0,0,1,0,1,0,1,0,1,0,0,0],
[0,0,0,1,0,0,0,1,0,0,0,0],
[0,0,0,0,1,0,1,0,0,0,0,0],
[0,0,0,0,0,1,0,0,0,0,0,0]]
        he_sov = [[0,0,0,0,0,1,0,0,0,0,0,0],
[0,0,0,0,0,1,0,0,0,0,0,0],
[0,0,1,1,1,1,1,1,1,0,0,0],
[0,0,1,0,0,0,0,0,1,0,0,0],
[0,0,1,0,1,1,1,0,1,0,0,0],
[0,0,1,0,0,0,1,0,1,0,0,0],
[0,0,1,0,1,0,1,0,1,0,0,0],
[0,0,1,0,1,0,1,0,1,0,0,0],
[0,0,0,1,0,0,0,1,0,0,0,0],
[0,0,0,0,1,0,1,0,0,0,0,0],
[0,0,0,0,0,1,0,0,0,0,0,0]]
        pe_sov = [[0,0,0,0,0,1,0,0,0,0,0,0],
[0,0,0,0,0,1,0,0,0,0,0,0],
[0,0,1,1,1,1,1,1,1,0,0,0],
[0,0,1,0,0,0,0,0,1,0,0,0],
[0,0,1,0,1,1,1,0,1,0,0,0],
[0,0,1,0,1,0,1,0,1,0,0,0],
[0,0,1,0,0,0,1,0,1,0,0,0],
[0,0,1,0,1,1,1,0,1,0,0,0],
[0,0,0,1,0,0,0,1,0,0,0,0],
[0,0,0,0,1,0,1,0,0,0,0,0],
[0,0,0,0,0,1,0,0,0,0,0,0]]
        self.sovim = [nun_sov,gimel_sov,he_sov,pe_sov]
        self.sr_driver = SRDriver(board_num_of_regs=56,
                                  num_of_boards=4,
                                  clk_pin=11,
                                  store_pin=12,
                                  data_pin=13,
                                  index_map_file=os.path.join('..', 'SR_Board', 'index_map.csv'),
                                  is_simulated=True)
        self.mw = MessagesWriter(font_path, 10, (7, 11))
        self.mw.load_text(self.mw.mirror_string(u'חנוכה שמח!'), True)

    def start(self):
        plt.ion()
        f = plt.figure()
        counter = 0
        while (True):
            if (counter >= 28):
                counter = 0
            sov_index = counter / 7
            sov = self.sovim[sov_index]
            counter += 1

            a = self.mw.get_next_step()
            a = a[1:7, :]
            a = np.asarray(a)
            sov = np.asarray(sov)
            sov = sov[:,0:11]
            b = np.concatenate([sov,a],0)
            self.sr_driver.draw(pic=b.astype(int))
            # f.clf()
            # plt.imshow(b, cmap='hot')
            # f.canvas.draw()
            time.sleep(0.2)

if __name__ == '__main__':
    #font_path = r'/home/netanel/PycharmProjects/bulboard/screen_usages/fonts/arcade/ARCADE.TTF'
    #font_path = r'/usr/share/fonts/truetype/freefont/FreeSans.ttf'
    font_path = r'C:\Windows\Fonts\Arial.ttf'
    runner = StaticSovNTextRunner()
    runner.start()
