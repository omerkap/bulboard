import logging
import time
import threading
import cPickle
import pickle
from screen_usages.abstract_screen_usage import AbstractScreenUsage


class ScreenUsagesOrchestrator(threading.Thread):
    def __init__(self, sr_driver, screen_scroll_delay=0.2, runners={}):
        super(ScreenUsagesOrchestrator, self).__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._sr_driver = sr_driver
        self._screen_scroll_delay = screen_scroll_delay
        self._current_frame = None

        for runner_name, runner in runners.items():
            assert isinstance(runner, AbstractScreenUsage)

        self._runners = runners
        # default runner is the first one
        self._active_runner = self._runners[self._runners.keys()[0]]
        self._active_runner_name = self._runners.keys()[0]
        try:
            self._logger.info('trying to load previously saved state')
            self.load_state_from_file()
        except Exception as ex:
            self._logger.exception(ex)

        self._should_run = False

    def set_active_runner(self, runner_name):
        self._logger.info('setting active runner to: {}'.format(runner_name))
        try:
            self._active_runner = self._runners[runner_name]
            self._active_runner_name = runner_name
            self._logger.info('runner {} was set successfully'.format(runner_name))
        except KeyError:
            self._logger.error('runner {} not found, runners names: {}'.format(runner_name, self._runners.keys()))

    def get_active_runner(self):
        return self._active_runner

    def kill_runner(self):
        self._should_run = False

    def calc_next_frame(self):
        return self._active_runner.get_next_step()

    def get_current_frame(self):
        return self._current_frame

    def save_state_to_file(self):
        with open('orchestrator_back_up_file.pickle', 'w') as f:
            current_runner_data = self._active_runner.serialize_state()
            container = dict()
            container['runner_data'] = current_runner_data
            container['runner_name'] = self._active_runner_name
            cPickle.dump(container, f, pickle.HIGHEST_PROTOCOL)

        self._logger.info('saved state to file')

    def load_state_from_file(self):
        with open('orchestrator_back_up_file.pickle', 'r') as f:
            container = cPickle.load(f)
            self._active_runner_name = container['runner_name']
            self._active_runner = self._runners[self._active_runner_name]
            self._active_runner.load_state(container['runner_data'])

        self._logger.info('loaded state, active runner: {}'.format(self._active_runner_name))

    def run(self):
        self._should_run = True
        while self._should_run:
            try:
                self._current_frame = self.calc_next_frame()
                self._sr_driver.draw(pic=self._current_frame)
            except Exception as ex:
                self._logger.exception(ex)

            time.sleep(self._screen_scroll_delay)

