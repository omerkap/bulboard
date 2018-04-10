import numpy as np
from abstract_screen_usage import AbstractScreenUsage


class MatrixScroller(AbstractScreenUsage):
    def __init__(self, screen_size=(17, 11)):
        self._screen_size = screen_size
        self._data_matrix = None
        self._rtl = None
        self._scrolling_step = 0

    def set_data_matrix(self, matrix, rtl=False):
        self._data_matrix = matrix
        self._rtl = rtl
        self._scrolling_step = 0

    def get_next_step(self):
        """
        Roll the text in one pixel to the wanted direction (RTL: right, LTR: left) and return the next viewable matrix
        :return:
        """
        if not self._rtl:
            if self._scrolling_step + self._screen_size[1] <= self._data_matrix.shape[1]:
                result = self._data_matrix[:, self._scrolling_step: self._scrolling_step + self._screen_size[1]]
            else:
                result = np.concatenate([
                    self._data_matrix[:, self._scrolling_step: self._data_matrix.shape[1]],
                    self._data_matrix[:, 0: self._screen_size[1] - (self._data_matrix.shape[1] - self._scrolling_step)]
                ], 1)

            if self._scrolling_step < self._data_matrix.shape[1]:
                self._scrolling_step += 1
            else:
                self._scrolling_step = 0

        else:
            if self._scrolling_step - self._screen_size[1] >= 0:
                result = self._data_matrix[:, self._scrolling_step - self._screen_size[1]: self._scrolling_step]
            else:
                result = np.concatenate([
                    self._data_matrix[:,
                    self._data_matrix.shape[1] - (self._screen_size[1] - self._scrolling_step): self._data_matrix.shape[
                        1]],
                    self._data_matrix[:, 0: self._scrolling_step]
                ], 1)

            if self._scrolling_step == 0:
                self._scrolling_step = self._data_matrix.shape[1]
            else:
                self._scrolling_step -= 1

        return result