# -*- coding: utf8 -*-
from __future__ import print_function
import logging
from disk_sapce_file_handlers import DiskSpaceRotatingFileHandler
from datetime import datetime
import os
import time
from bdf_font import BdfFont
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import numpy as np
from abstract_screen_usage import AbstractScreenUsage
try:
    import matplotlib.pyplot as plt
    from matplotlib import animation
except ImportError as ex:
    print(ex)
import sys
sys.path.append(r'../')


class MessagesWriter(AbstractScreenUsage):
    def __init__(self, font_path, font_size, screen_size=(17, 11), bdf=False):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info('initializing {}'.format(self.__class__.__name__))
        self._logger.info('screen size: {}'.format(screen_size))
        self._screen_size = screen_size
        self._font = None
        self._is_bdf = False
        self._font_size = None
        self._rtl = None
        self._text_matrix = None
        self._scrolling_step = 0
        self.set_font(font_path=font_path, font_size=font_size, bdf=bdf)
        self._logger.info('finished initializing MessagesWriter')

    def set_font(self, font_path, font_size, bdf=False):
        """
        Set the current used font of MessagesWriter
        :param font_path: path to used font
        :param font_size: size
        :return:
        """
        self._logger.info('setting new font, {}'.format(font_path))
        if bdf is False:
            self._font = ImageFont.truetype(font_path, font_size)
            self._font_size = font_size
        else:
            self._logger.info('bdf font is used, size is taken from Font parameters')
            self._font = BdfFont(font_file=font_path)
            self._font_size = self._font.get_font_size()[1]
            self._is_bdf = True

    def load_text(self, text, rtl=False):
        """
        Set the current shown text of MessagesWriter
        :param text: the text string
        :param rtl: should the text be interpreted as RTL (scroll the other direction)
        :return: the length of the full text matrix
        """
        self._rtl = rtl
        text_matrix = self._str_to_pixels(string=text)
        if text_matrix.shape[0] < self._screen_size[0]:
            self._logger.debug('text is shorter than screen, padding towards downside')
            a, b = divmod(self._screen_size[0] - text_matrix.shape[0], 2)
            top_size = self._screen_size[0] - text_matrix.shape[0] - a
            bottom_size = a
            top_padding_matrix = np.zeros([top_size, text_matrix.shape[1]])
            bottom_padding_matrix = np.zeros([bottom_size, text_matrix.shape[1]])
            text_matrix = np.concatenate([top_padding_matrix, text_matrix, bottom_padding_matrix], 0)

        # add to text matrix an 'empty' matrix with the screen size, so when we move the text we start from clean screen
        self._text_matrix = np.concatenate([np.zeros(self._screen_size, dtype=int), text_matrix], 1)
        self._scrolling_step = 0
        self._logger.debug('text size: {}'.format(self._text_matrix.shape))
        return self._text_matrix.shape[1]

    def get_next_step(self):
        """
        Roll the text in one pixel to the wanted direction (RTL: right, LTR: left) and return the next viewable matrix
        :return:
        """
        if not self._rtl:
            if self._scrolling_step + self._screen_size[1] <= self._text_matrix.shape[1]:
                result = self._text_matrix[:, self._scrolling_step: self._scrolling_step + self._screen_size[1]]
            else:
                result = np.concatenate([
                    self._text_matrix[:, self._scrolling_step: self._text_matrix.shape[1]],
                    self._text_matrix[:, 0: self._screen_size[1] - (self._text_matrix.shape[1] - self._scrolling_step)]
                ], 1)

            if self._scrolling_step < self._text_matrix.shape[1]:
                    self._scrolling_step += 1
            else:
                self._scrolling_step = 0

        else:
            if self._scrolling_step - self._screen_size[1] >= 0:
                result = self._text_matrix[:, self._scrolling_step - self._screen_size[1]: self._scrolling_step]
            else:
                result = np.concatenate([
                    self._text_matrix[:, self._text_matrix.shape[1] - (self._screen_size[1] - self._scrolling_step): self._text_matrix.shape[1]],
                    self._text_matrix[:, 0: self._scrolling_step]
                ], 1)

            if self._scrolling_step == 0:
                    self._scrolling_step = self._text_matrix.shape[1]
            else:
                self._scrolling_step -= 1

        return result

    def _str_to_pixels(self, string):
        #self._logger.info('converting {} to array'.format(string))
        string_array = np.zeros((self._font_size, 1), dtype=int)  # 0 column
        for c in string:
            arr = self._char_to_pixels(c)
            string_array = np.concatenate([string_array, arr], 1)
        return self._trim(string_array)

    def _char_to_pixels(self, char):
        """
        Based on https://stackoverflow.com/a/27753869/190597 (jsheperd)
        """
        if self._is_bdf:
            return self._font.char_to_matrix(char)
        w, h = self._font.getsize(char)
        self._logger.debug('char: {}, w: {}, h: {}'.format(char, w, h))
        image = Image.new('L', (w, h), 1)
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), char, font=self._font)
        arr = np.asarray(image)
        arr = np.where(arr, 0, 1)  # replace 1's and 0's
        if arr.shape[0] < self._font_size:
            return np.concatenate([np.zeros([self._font_size - arr.shape[0], arr.shape[1]], dtype=int), arr], 0)
        else:
            return arr

    @staticmethod
    def _trim(matrix):
        i = j = 0
        for i in range(matrix.shape[0]):
            if np.sum(matrix[i:i+1, :], 1) > 0:
                break

        for j in range(matrix.shape[0], 0, -1):
            if np.sum(matrix[j:j+1, :], 1) > 0:
                break

        return matrix[i:j+1, :]

    @staticmethod
    def mirror_string(string):
        """
        Mirror string, can be used for mirroring Hebrew text
        :param string:
        :return:
        """
        s = ''
        for i in range(len(string) - 1, -1, -1):
            s = s + string[i]
        return s


def init_logging(level):
    root_logger = logging.getLogger()
    root_logger.setLevel(level=level)
    try:
        os.mkdir('logs')
    except Exception:
        pass
    file_name = os.path.join('logs', 'GameOfLife_{}'.format(datetime.now().strftime('%d_%m_%y__%H_%M_%S')))
    file_handler = DiskSpaceRotatingFileHandler(folder_max_size=10E6, filename=file_name, maxBytes=1E6, backupCount=10000)
    formatter = logging.Formatter(fmt=r'%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger.addHandler(hdlr=file_handler)
    root_logger.addHandler(hdlr=console_handler)


if __name__ == '__main__':
    init_logging(level=logging.DEBUG)
    #font_path = r'/home/netanel/PycharmProjects/bulboard/screen_usages/fonts/arcade/ARCADE.TTF'
    font_path = r'/usr/share/fonts/truetype/freefont/FreeSans.ttf'
    #font_path = r'C:\Windows\Fonts\Arial.ttf'
    font_path = r'fonts/bdf/5x8.bdf'
    font_path = r'fonts/bdf/7x14B.bdf'
    font_path = r'fonts/bdf/helvR12.bdf'

    mw = MessagesWriter(font_path, 17, (17, 11), True)
    #steps = mw.load_text(mw.mirror_string(u'חג שמח!'), True)
    steps = mw.load_text(u'חג שמח!')

    plt.ion()
    f = plt.figure()
    #plt.show()
    for k in range(2 * steps):
        a = mw.get_next_step()
        f.clf()
        plt.imshow(a, cmap='hot')
        f.canvas.draw()
        time.sleep(0.01)

#    plt.show()

