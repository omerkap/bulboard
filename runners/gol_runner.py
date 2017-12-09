from datetime import datetime
from screen_usages.disk_sapce_file_handlers import DiskSpaceRotatingFileHandler
import logging
import os
import time
from screen_usages.gol_calculator import GameOfLife
import numpy as np

try:
    import matplotlib.pyplot as plt
    from matplotlib import animation
except ImportError as ex:
    print ex
import sys

sys.path.append(r'../')
from SR_Board.sr_driver import SRDriver


class GameOfLifeRunner(object):
    def __init__(self, initial_pattern, steps):
        self._steps = steps
        self._logger = logging.getLogger(self.__class__.__name__)
        self._initial_pattern = initial_pattern

    @staticmethod
    def create(pattern_str, steps):
        try:
            return GameOfLifeRunner(np.asarray(np.matrix(pattern_str.encode('ascii', 'ignore'))), steps)
        except Exception:
            return None

    @staticmethod
    def init_logging(level):
        root_logger = logging.getLogger()
        root_logger.setLevel(level=level)
        try:
            os.mkdir('logs')
        except Exception:
            pass
        file_name = os.path.join('logs', 'GameOfLife_{}'.format(datetime.now().strftime('%d_%m_%y__%H_%M_%S')))
        # file_handler = RotatingFileHandler(filename=file_name, maxBytes=10e6, backupCount=5)
        file_handler = DiskSpaceRotatingFileHandler(folder_max_size=10E6, filename=file_name, maxBytes=1E6,
                                                    backupCount=10000)
        formatter = logging.Formatter(fmt=r'%(asctime)s:%(name)s:%(levelname)s:%(message)s')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(hdlr=file_handler)

    def start(self):
        self.init_logging(logging.INFO)
        logger = logging.getLogger()
        p = np.zeros((17, 11))
        pattern_x_size, pattern_y_size = self._initial_pattern.shape
        p[0:pattern_x_size, 0:pattern_y_size] = self._initial_pattern
        gol_obj = GameOfLife(initial_pattern=p)
        screen_writer = SRDriver(board_num_of_regs=56,
                                 num_of_boards=4,
                                 clk_pin=11,
                                 store_pin=12,
                                 data_pin=13,
                                 index_map_file=os.path.join('..', 'SR_Board', 'index_map.csv'),
                                 is_simulated=True)

        plt.ion()
        f = plt.figure()

        for i in range(self._steps):
            state = gol_obj.state
            step = gol_obj.step
            logger.info('step: {}'.format(step))
            screen_writer.draw(pic=state.astype(int))
            gol_obj.visualize_state(state=state, step=step, figure=f)
            gol_obj.get_next_step()
            time.sleep(0.1)


if __name__ == '__main__':
    initial_beacon = GameOfLife.get_demo_glider()
    gol_runner = GameOfLifeRunner(initial_beacon, 100)
    gol_runner.start()
