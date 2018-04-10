import logging
from abstract_screen_usage import AbstractScreenUsage
from screen_usages.messages_writer import MessagesWriter
import numpy as np


class DualLineMessageWriter(AbstractScreenUsage):

    def __init__(self, font_path, font_size=8, half_screen_size=(8, 11), bdf_font=True):
        super(DualLineMessageWriter,  self).__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._line_1_mw = MessagesWriter(font_path=font_path, font_size=font_size, screen_size=half_screen_size, bdf=bdf_font)
        self._line_2_mw = MessagesWriter(font_path=font_path, font_size=font_size, screen_size=half_screen_size, bdf=bdf_font)

        self._current_frame = None
        self.set_text()
        self._logger.info('initialized {}'.format(self.__class__.__name__))

    def set_text(self, first_line=' ', second_line=' ', first_line_rtl=False, second_line_rtl=False):

        self._logger.info('in set_text, first_line: {}, second_line: {}, first_line_rtl: {}, second_line_rtl: {}'
                           .format(first_line, second_line, first_line_rtl, second_line_rtl))
        if first_line_rtl is True:
            first_line = MessagesWriter.mirror_string(first_line)
        if second_line_rtl is True:
            second_line = MessagesWriter.mirror_string(second_line)

        self._line_1_mw.load_text(text=first_line, rtl=first_line_rtl)
        self._line_2_mw.load_text(text=second_line, rtl=second_line_rtl)

    def get_next_step(self):
        first_row_m = self._line_1_mw.get_next_step()
        second_row_m = self._line_2_mw.get_next_step()
        seperator = np.zeros((1, first_row_m.shape[1]))

        m = np.concatenate([first_row_m, seperator, second_row_m], 0)
        self._logger.debug('calculated frame with shape: {}'.format(m.shape))
        return m.astype(dtype=int)





