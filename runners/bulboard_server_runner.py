# -*- coding: utf8 -*-
import os
import StringIO
from datetime import datetime
import numpy as np
import logging
import json
from flask import Flask, url_for, render_template, request, make_response

from screen_usages_orchestrator import ScreenUsagesOrchestrator
from screen_usages.dual_line_message_writer import DualLineMessageWriter
from screen_usages.messages_writer import MessagesWriter
from screen_usages.matrix_scroller import MatrixScroller
from screen_usages.gol_calculator import GameOfLife

from SR_Board.sr_driver import SRDriver
from screen_usages.disk_sapce_file_handlers import DiskSpaceRotatingFileHandler

try:
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
except ImportError as ex:
    print ex


app = Flask(__name__)

# TODO: move to config file sometime
ONE_LINE_FONT_FILE = r'/usr/share/fonts/truetype/msttcorefonts/Arial.ttf'
FONT_PATH = r'../screen_usages/fonts/arcade/ARCADE.TTF' #['..', 'screen_usages', 'fonts', 'arcade', 'ARCADE.TTF'])
FONT_PATH = r'../screen_usages/fonts/Ozone.ttf'
ONE_LINE_FONT_FILE = r'../screen_usages/fonts/bdf/8x13.bdf'
FONT_PATH = r'../screen_usages/fonts/bdf/6x9.bdf'

DELAY_BETWEEN_PIXEL_SCROLL = 0.2  #[S]
LOG_LEVEL = logging.INFO


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/two_line_message")
def two_line_message(first_line_text='line1', first_line_rtl='', second_line_text='line2', second_line_rtl=''):
    return render_template('2_line_message.html',
                           first_line_text=first_line_text,
                           first_line_rtl=first_line_rtl,
                           second_line_text=second_line_text,
                           second_line_rtl=second_line_rtl)


@app.route("/horizontal_pixel_message")
def horizontal_pixel_message():
    return render_template('horizontal_pixel_message.html', row_number=17, col_number=11 * 10)


@app.route("/game_of_life")
def game_of_life():
    return render_template('game_of_life.html', row_number=17, col_number=11)


@app.route("/one_line_message")
def one_line_message(message='demo message', message_rtl=''):
    return render_template('one_line_message.html',
                           message=message,
                           message_rtl=message_rtl)


@app.route("/set_one_line_message_text")
def set_one_line_message_text():
    message = request.values['FirstLine']
    try:
        rtl = bool(request.values['FirstLineRtl'])
    except Exception:
        rtl = False

    try:
        runner.set_active_runner(runner_name='OneMessagesWriter')
        r = runner.get_active_runner()
        if rtl:
            message = r.mirror_string(message)
        r.load_text(text=message, rtl=rtl)
        message_rtl = 'checked' if rtl is True else ''
        return one_line_message(message=message, message_rtl=message_rtl)

    except Exception as ex:
        logging.exception(ex)

    return one_line_message()


@app.route("/save_current_state")
def save_current_state():
    runner.save_state_to_file()
    return index()


@app.route("/set_two_line_message_text")
def set_two_line_message_text():
    first_line_text = request.values['FirstLine']
    try:
        first_line_rtl = bool(request.values['FirstLineRtl'])
    except Exception:
        first_line_rtl = False
    second_line_text = request.values['SecondLine']
    try:
        second_line_rtl = bool(request.values['SecondLineRtl'])
    except Exception:
        second_line_rtl = False

    try:
        runner.set_active_runner(runner_name='DualLineMessageWriter')
        r = runner.get_active_runner()
        r.set_text(first_line=first_line_text, second_line=second_line_text,
                   first_line_rtl=first_line_rtl, second_line_rtl=second_line_rtl)
        first_checked = 'checked' if first_line_rtl is True else ''
        second_checked = 'checked' if second_line_rtl is True else ''
        return two_line_message(first_line_text=first_line_text,
                                first_line_rtl=first_checked,
                                second_line_text=second_line_text,
                                second_line_rtl=second_checked)

    except Exception as ex:
        logging.exception(ex)

    return two_line_message()


@app.route("/set_horizontal_pixel_message", methods=['POST'])
def set_horizontal_pixel_message():
    logging.info('in set_horizontal_pixel_message')
    data = request.data
    parsed_pixel_message = json.loads(data)
    logging.debug(parsed_pixel_message)
    rtl = True if parsed_pixel_message['rtl'] == 1 else False
    try:
        runner.set_active_runner(runner_name='MatrixScroller')
        r = runner.get_active_runner()
        m = np.array(parsed_pixel_message['outputArray'], dtype=int)
        r.set_data_matrix(m, rtl=rtl)
    except Exception as ex:
        logging.exception(ex)

    return make_response()


@app.route("/set_game_of_life_initial_state", methods=['POST'])
def set_game_of_life_initial_state():
    logging.info('in set_game_of_life_initial_state')
    data = request.data
    parsed_pixel_message = json.loads(data)
    logging.debug(parsed_pixel_message)

    try:
        runner.set_active_runner(runner_name='GameOfLife')
        r = runner.get_active_runner()
        m = np.array(parsed_pixel_message['outputArray'], dtype=int)
        r.reset_initial_pattern(m)
    except Exception as ex:
        logging.exception(ex)

    return make_response()


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


def init_logging(level):
    root_logger = logging.getLogger()
    root_logger.setLevel(level=level)
    try:
        os.mkdir('logs')
    except Exception:
        pass
    file_name = os.path.join('logs', 'BulboardServer_{}'.format(datetime.now().strftime('%d_%m_%y__%H_%M_%S')))
    file_handler = DiskSpaceRotatingFileHandler(folder_max_size=10E6, filename=file_name, maxBytes=1E6, backupCount=10000)
    formatter = logging.Formatter(fmt=u'%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logging._defaultFormatter = logging.Formatter(u"%(message)s")  # so utf8 messages will not crash the logging
    root_logger.addHandler(hdlr=file_handler)
    root_logger.addHandler(hdlr=console_handler)


if __name__ == '__main__':
    init_logging(level=LOG_LEVEL)
    sr = SRDriver(board_num_of_regs=56,
                  num_of_boards=4,
                  clk_pin=11,
                  store_pin=12,
                  data_pin=13,
                  index_map_file=os.path.join('..', 'SR_Board', 'index_map.csv'),
                  is_simulated=True)

    runners = {
        'DualLineMessageWriter': DualLineMessageWriter(font_path=FONT_PATH),
        'OneMessagesWriter': MessagesWriter(font_path=ONE_LINE_FONT_FILE, font_size=1, screen_size=(17, 11), bdf=True),
        'MatrixScroller': MatrixScroller(),
        'GameOfLife': GameOfLife()
    }

    runner = ScreenUsagesOrchestrator(sr_driver=sr,
                                      screen_scroll_delay=0.2,
                                      runners=runners)
    runner.start()
    app.run()  # don't do that, use FLASK_APP env

