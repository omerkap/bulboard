import logging
import time
import threading
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
        self._should_run = False

    def set_active_runner(self, runner_name):
        self._logger.info('setting active runner to: {}'.format(runner_name))
        try:
            self._active_runner = self._runners[runner_name]
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
        #TODO: save state to file, when raspberry pi resets we can load the state and message will be saved
        pass

    def load_state_from_file(self):
        pass

    def run(self):
        self._should_run = True
        while self._should_run:
            try:
                self._current_frame = self.calc_next_frame()
                self._sr_driver.draw(pic=self._current_frame)
            except Exception as ex:
                self._logger.exception(ex)

            time.sleep(self._screen_scroll_delay)

