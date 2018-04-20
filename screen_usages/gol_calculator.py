import logging
import numpy as np
from datetime import datetime
import os
import time

from disk_sapce_file_handlers import DiskSpaceRotatingFileHandler
from abstract_screen_usage import AbstractScreenUsage

try:
    import matplotlib.pyplot as plt
    from matplotlib import animation
except ImportError as ex:
    print ex
import sys
sys.path.append(r'../')
from SR_Board.sr_driver import SRDriver


class GameOfLife(AbstractScreenUsage):
    def __init__(self, initial_pattern=np.zeros((17, 11))):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info('initialized Game Of Life')
        self._logger.info('size: {}'.format(initial_pattern.shape))
        self._initial_pattern = initial_pattern
        self._state = self._initial_pattern
        self._size = self._state.shape
        self._step = 0

    def reset_initial_pattern(self, initial_pattern):
        self._logger.warning('resetting initial pattern, new size: {}'.format(initial_pattern.shape))
        self._state = initial_pattern
        self._initial_pattern = initial_pattern
        self._size = self._state.shape
        self._step = 0

    def get_next_step(self):
        """
        Advance the state 1 step
        :return:
        """
        t0 = time.time()
        next_state = np.zeros(self._size)
        v_bloated = np.concatenate((self._state, self._state, self._state), axis=0)
        bloated = np.concatenate((v_bloated, v_bloated, v_bloated), axis=1)
        self._logger.debug('bloated shape: {}'.format(bloated.shape))

        for index, x in np.ndenumerate(self._state):
            next_state[index] = self._calculate_one_cell(index=index, bloated=bloated)

        self._state = np.copy(next_state)
        self._step += 1
        t1 = time.time()
        self._logger.debug('step calculation time: {}'.format(t1 - t0))
        return self._state

    def _calculate_one_cell(self, index, bloated):
        """
        Calculate next state of one cell, from the current states of neighbors
        :param index: index of calculated cell
        :param bloated: a matrix that is bigger than state, that has sequences of state, this helps with indexing
            neighbors without wraparounds
        :return: next value of cell in index
        """
        current_value = self._state[index]
        neighbors_data = self._get_neighbors_data(index, bloated)
        sum_of_neighbors = np.sum(neighbors_data)
        self._logger.debug(current_value)

        if current_value == 1:
            if sum_of_neighbors < 2:
                return 0
            if sum_of_neighbors > 3:
                return 0
            else:
                return 1
        elif current_value == 0:
            if sum_of_neighbors == 3:
                return 1
            else:
                return 0

        self._logger.error('in _calculate_one_cell, none of rules matched,'\
                           '\n index: {}, current value: {}'.format(index, current_value))

    def _get_neighbors_data(self, index, bloated):
        x = index[0]
        y = index[1]

        bloated_x = x + self._size[0]
        bloated_y = y + self._size[1]

        neighbors_matrix = np.copy(bloated[bloated_x - 1: bloated_x + 2, bloated_y - 1: bloated_y + 2])
        flattened = neighbors_matrix.ravel()

        return np.concatenate((flattened[0:4], flattened[5:9]))

    def load_state(self, serialized_state):
        self._initial_pattern = serialized_state['initial_pattern']
        self._state = self._initial_pattern
        self._step = 0

    def serialize_state(self):
        container = dict()
        container['initial_pattern'] = self._initial_pattern
        return container

    @property
    def state(self):
        return np.copy(self._state)

    @property
    def step(self):
        return self._step

    @staticmethod
    def visualize_state(state, step, figure):
        t_start_vis = time.time()
        figure.clf()
        plt.title('Step: {}'.format(step))
        plt.imshow(state, cmap='hot')
        figure.canvas.draw()
        t_end_vis = time.time()
        logging.debug('visualizing time: {}'.format(t_end_vis - t_start_vis))
        return figure

    @staticmethod
    def get_demo_blinker():
        blinker = np.ones((3, 1))
        return blinker

    @staticmethod
    def get_demo_beacon():
        beacon = np.zeros((4, 4))
        beacon[0:2, 0:2] = 1
        beacon[2:4, 2:4] = 1
        return beacon

    @staticmethod
    def get_demo_glider():
        glider = np.zeros((3, 3))
        glider[0:3, 2:3] = 1
        glider[1:2, 0:1] = 1
        glider[2:3, 1:2] = 1
        return glider

    @staticmethod
    def get_demo_pentadecathlon():
        pentadecathlon = np.zeros((10, 3))
        pentadecathlon[0:10, 1:2] = 1
        pentadecathlon[2:3, 0:3] = 1
        pentadecathlon[7:8, 0:3] = 1
        pentadecathlon[2:3, 1:2] = 0
        pentadecathlon[7:8, 1:2] = 0
        return pentadecathlon


def init_logging(level):
    root_logger = logging.getLogger()
    root_logger.setLevel(level=level)
    try:
        os.mkdir('logs')
    except Exception:
        pass
    file_name = os.path.join('logs', 'GameOfLife_{}'.format(datetime.now().strftime('%d_%m_%y__%H_%M_%S')))
    #file_handler = RotatingFileHandler(filename=file_name, maxBytes=10e6, backupCount=5)
    file_handler = DiskSpaceRotatingFileHandler(folder_max_size=10E6, filename=file_name, maxBytes=1E6, backupCount=10000)
    formatter = logging.Formatter(fmt=r'%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler.setFormatter(formatter)

    #console_handler = logging.StreamHandler()
    #console_handler.setFormatter(formatter)

    root_logger.addHandler(hdlr=file_handler)
    #root_logger.addHandler(hdlr=console_handler)


if __name__ == '__main__':
    init_logging(logging.INFO)
    l = logging.getLogger()
    p = np.zeros((17, 11))

    # blinker = GameOfLife.get_demo_blinker()
    # blinker_x_size, blinker_y_size = blinker.shape
    # p[1:1+blinker_x_size, 1:1+blinker_y_size] = blinker
    #
    # beacon = GameOfLife.get_demo_beacon()
    # beacon_x_size, beacon_y_size = beacon.shape
    # p[7:7 + beacon_x_size, 7:7 + beacon_y_size] = beacon

    glider = GameOfLife.get_demo_glider()
    glider_x_size, glider_y_size = glider.shape
    p[2:2 + glider_x_size, 4:4 + glider_y_size] = glider

    # pentadecathlon = GameOfLife.get_demo_pentadecathlon()
    # pentadecathlon_x_size, pentadecathlon_y_size = pentadecathlon.shape
    # p[3:3 + pentadecathlon_x_size, 4:4 + pentadecathlon_y_size] = pentadecathlon

    l.info('\n{}'.format(p))

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

    for i in range(200):
        state = gol_obj.state
        step = gol_obj.step
        l.info('step: {}'.format(step))
        t0 = time.time()
        screen_writer.load_array(picture=state.astype(int))
        screen_writer.write_data()
        gol_obj.visualize_state(state=state, step=step, figure=f)
        gol_obj.calc_next_step()
        time.sleep(0.1)



    ## Create GIF

    # def animate(i):
    #     state = g.state
    #     step = g.step
    #     l.info(f'step: {step}')
    #     a = g.visualize_state(state=state, step=step, figure=f)
    #     g.calc_next_step()
    #     return (a,)
    #
    #
    # def init():
    #     return (f,)
    #
    # anim = animation.FuncAnimation(f, animate, init_func=init, frames=15, interval=150, blit=True)
    # anim.save('pentadecathlon.gif', writer='imagemagick', fps=5)
