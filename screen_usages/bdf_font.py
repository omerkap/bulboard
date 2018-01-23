# -*- coding: utf8 -*-
import logging
import os
from disk_sapce_file_handlers import DiskSpaceRotatingFileHandler
from datetime import datetime
import numpy as np


class BdfFont(object):
    # some bdf file parameters
    STARTCHAR = 'STARTCHAR'
    ENDCHAR = 'ENDCHAR'
    BBX = 'BBX'
    ENCODING = 'ENCODING'
    BITMAP = 'BITMAP'
    FONTBOUNDINGBOX = 'FONTBOUNDINGBOX'

    def __init__(self, font_file):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info('creating BdfFont object with font: {}'.format(font_file))
        self._chars_dict = {}
        self._font_size = (0, 0)
        self._parse_file(font_file)

    def _parse_file(self, file_name):
        with open(file_name) as f:
            for line in f:
                try:
                    line = line.split(' ')
                    if line[0] == self.STARTCHAR:
                        char_name = line[1].strip()
                        self._parse_char(f, char_name)

                    elif line[0] == self.FONTBOUNDINGBOX:
                        self._font_size = [int(v) for v in line[1:3]]

                except Exception as ex:
                    self._logger.error('ex in line: {}'.format(line))
                    self._logger.exception(ex)

            self._logger.info('parsed {} characters'.format(len(self._chars_dict)))

    def _parse_char(self, file_iterator, char_name):
        char_data = {'name': char_name}
        enc = 0
        bitmap = []

        bitmap_reading_started = False
        for line in file_iterator:
            line = line.strip('\n')
            line = line.split(' ')

            if line[0] == self.ENCODING and bitmap_reading_started is False:
                enc = line[1]

            elif line[0] == self.BBX and bitmap_reading_started is False:
                char_data['bbx'] = [int(v) for v in line[1:]]

            elif line[0] == self.BITMAP and bitmap_reading_started is False:
                bitmap_reading_started = True
                continue

            if bitmap_reading_started:
                if line[0] != self.ENDCHAR:
                    bitmap.append(line[0])
                else:
                    char_data['bitmap'] = self._hex_list_to_ndarray(l=bitmap)
                    self._chars_dict[enc] = char_data
                    return

    def _hex_list_to_ndarray(self, l):
        #arr = np.zeros(self._font_size, dtype=int)
        arr = np.zeros((10, 8), dtype=int)
        for row_num, row in enumerate(l):
            bin_str = '{:08b}'.format(int(row, 16))
            bin_int = [int(c) for c in bin_str]
            arr[row_num, :] = bin_int

        return arr #arr[0:size[1], 0:size[0]]

    def char_to_matrix(self, c):
        char_str_val = str(ord(c))
        return self._chars_dict[char_str_val]['bitmap']

    def get_font_size(self):
        return self._font_size


def init_logging(level):
    root_logger = logging.getLogger()
    root_logger.setLevel(level=level)
    formatter = logging.Formatter(fmt=r'%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(hdlr=console_handler)


if __name__ == '__main__':
    init_logging(level=logging.DEBUG)
    font_path = r'fonts/bdf/5x8.bdf'
    font_path = r'fonts/bdf/6x10.bdf'
    bdf = BdfFont(font_file=font_path)
    print(bdf.char_to_matrix(u'ק'))
