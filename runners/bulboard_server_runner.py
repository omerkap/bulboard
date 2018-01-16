import threading
import os
import time
import StringIO
from datetime import datetime
import numpy as np
import logging
from flask import Flask, url_for, render_template, request, make_response
from screen_usages.messages_writer import MessagesWriter
from screen_usages.disk_sapce_file_handlers import DiskSpaceRotatingFileHandler
from SR_Board.sr_driver import SRDriver

try:
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
except ImportError as ex:
    print ex


app = Flask(__name__)

# TODO: move to config file sometime
FONT_PATH = r'/usr/share/fonts/truetype/msttcorefonts/Arial.ttf'
DELAY_BETWEEN_PIXEL_SCROLL = 0.2  #[S]
LOG_LEVEL = logging.DEBUG


@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/set_text")
def set_text():
    first_line_text = request.values['FirstLine']
    try:
        first_line_rtl = request.values['FirstLineRtl']
    except Exception:
        first_line_rtl = False
    second_line_text = request.values['SecondLine']
    try:
        second_line_rtl = request.values['SecondLineRtl']
    except Exception:
        second_line_rtl = False

    try:
        runner.set_text(first_line=first_line_text, second_line=second_line_text,
                        first_line_rtl=first_line_rtl, second_line_rtl=second_line_rtl)
    except Exception as ex:
        logging.exception(ex)
    return hello()


@app.route("/cur_img", methods=['GET', 'POST'])
def cur_img():
    c = runner.get_current_frame()
    fig = Figure()
    ax = fig.add_subplot(111)
    ax.imshow(c, cmap='hot')
    canvas = FigureCanvasAgg(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


class DualMessageRunner(threading.Thread):
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        super(DualMessageRunner,  self).__init__()
        self._line_1_mw = MessagesWriter(font_path=FONT_PATH, font_size=10, screen_size=(8, 11))
        self._line_2_mw = MessagesWriter(font_path=FONT_PATH, font_size=10, screen_size=(8, 11))
        self._sr_driver = SRDriver(board_num_of_regs=56,
                                   num_of_boards=4,
                                   clk_pin=11,
                                   store_pin=12,
                                   data_pin=13,
                                   index_map_file=os.path.join('..', 'SR_Board', 'index_map.csv'),
                                   is_simulated=True)
        self._should_run = True
        self._current_frame = None
        self.set_text()
        self._logger.info('initialized {}'.format(self.__class__.__name__))

    def set_text(self, first_line=' ', second_line=' ', first_line_rtl=False, second_line_rtl=False):
        self._logger.info('in set_text, first_line: {}, second_line: {}, first_line_rtl: {}, second_line_rtl: {}'
                           .format(first_line, second_line, first_line_rtl, second_line_rtl))
        self._line_1_mw.load_text(text=first_line, rtl=first_line_rtl)
        self._line_2_mw.load_text(text=second_line, rtl=second_line_rtl)

    def kill_runner(self):
        self._should_run = False

    def get_current_frame(self):
        return self._current_frame

    def _calc_next_frame(self):
        first_row_m = self._line_1_mw.get_next_step()
        second_row_m = self._line_2_mw.get_next_step()
        seperator = np.zeros((1, first_row_m.shape[1]))

        m = np.concatenate([first_row_m, seperator, second_row_m], 0)
        self._logger.debug('calculated frame with shape: {}'.format(m.shape))
        return m.astype(dtype=int)

    def run(self):
        while self._should_run:
            self._current_frame = self._calc_next_frame()
            self._sr_driver.draw(pic=self._current_frame)
            time.sleep(DELAY_BETWEEN_PIXEL_SCROLL)


def init_logging(level):
    root_logger = logging.getLogger()
    root_logger.setLevel(level=level)
    try:
        os.mkdir('logs')
    except Exception:
        pass
    file_name = os.path.join('logs', 'BulboardServer_{}'.format(datetime.now().strftime('%d_%m_%y__%H_%M_%S')))
    file_handler = DiskSpaceRotatingFileHandler(folder_max_size=10E6, filename=file_name, maxBytes=1E6, backupCount=10000)
    formatter = logging.Formatter(fmt=r'%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger.addHandler(hdlr=file_handler)
    root_logger.addHandler(hdlr=console_handler)


init_logging(level=LOG_LEVEL)
runner = DualMessageRunner()


if __name__ == '__main__':

    runner.start()
    app.run()  # don't do that, use FLASK_APP env

