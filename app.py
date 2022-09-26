import logging
import os.path

import pyperclip
from flask import Flask, render_template, request

g3b1_logging_level = 30
logging.basicConfig(force=False,
                    level=g3b1_logging_level, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
app = Flask(__name__)
# not well:
logging.getLogger('werkzeug').setLevel(g3b1_logging_level)


class CBGlobal:
    cb_remote: str = pyperclip.paste()
    cb_remote_push: str = pyperclip.paste()
    cb_remote_history: list[str] = None
    # // logging.ERROR 40 - logging.DEBUG == 10
    logging_level: int = g3b1_logging_level


route__index = '/'
route__cb_remote_read = '/cb_remote/read'
route__form_cb_submit = '/form_cb_submit'


@app.route(route__cb_remote_read)
def cb_remote_read():
    upd_logging_level(route__cb_remote_read)
    _p_history_Idx = request.args.get('history_Idx')
    if _p_history_Idx:
        history_idx = int(_p_history_Idx) - 1
        logging.debug(f'URL parameter "history_Idx" / history_idx: {_p_history_Idx} / {history_idx}')
        logging.debug('history joined entries:' + ', '.join(CBGlobal.cb_remote_history))
        if 0 <= history_idx < len(CBGlobal.cb_remote_history):
            value_at = CBGlobal.cb_remote_history[history_idx]
            logging.warning(f'value_at: {value_at}')
            return value_at
    upd_cb_remote_history()
    return CBGlobal.cb_remote


@app.route(route__index)
def index():
    upd_logging_level(route__index)
    upd_cb_remote_history()
    kwargs = {'cb_remote_current': CBGlobal.cb_remote, 'cb_remote_push': CBGlobal.cb_remote_push,
              'job_interval__s': 3,
              'logging_level': CBGlobal.logging_level}
    logging.info(kwargs)
    kwargs['cb_remote_history'] = CBGlobal.cb_remote_history;
    return render_template('g3b1.html', **kwargs)


@app.route(route__form_cb_submit, methods=['POST'])
def cb_remote_push_ifnew():
    upd_logging_level(route__form_cb_submit)
    # CBGlobal.cb_remote_push is not rendered on the client side
    # for easier paste from client - no need to CTRL-A prior CTRL-V
    cb_remote_push_before = CBGlobal.cb_remote_push
    CBGlobal.cb_remote_push = request.form['cb_remote_push']
    if cb_remote_push_before != CBGlobal.cb_remote_push:
        pyperclip.copy(CBGlobal.cb_remote_push)
        upd_cb_remote_history()
    return index()


# URL parameter set_logging_level, eg value: logging.DEBUG 10 - logging.ERROR 40
def upd_logging_level(route_info_str=''):
    if route_info_str:
        logging.debug(f'@app.route: {route_info_str}')
    logging.debug(f'request.args: {request.args}')
    _do_set_logging_level: str = request.args.get('set_logging_level')
    logging.debug(f'_do_set_logging_level: {_do_set_logging_level}')
    if _do_set_logging_level is None:
        return
    if not _do_set_logging_level.isdigit():
        return
    logging.warning(f'logging.basicConfig(level={_do_set_logging_level})')
    logging.basicConfig(force=True, level=int(_do_set_logging_level))
    # not working well
    # logging.getLogger('werkzeug').setLevel(g3b1_logging_level)
    CBGlobal.logging_level = _do_set_logging_level


def upd_cb_remote_history(history_count_max=25):
    synch_cb_remote_history()
    logging.debug(f'cb_remote/cb_remote_push: {CBGlobal.cb_remote} / {CBGlobal.cb_remote_push}')
    cb_remote_current = pyperclip.paste()
    logging.debug(f'cb_remote_current: {cb_remote_current}')
    CBGlobal.cb_remote = cb_remote_current
    if CBGlobal.cb_remote_history[0] != cb_remote_current:
        logging.debug(f'insert-0 cb_remote_history: {cb_remote_current}')
        CBGlobal.cb_remote_history.insert(0, cb_remote_current)
        if len(CBGlobal.cb_remote_history) > history_count_max:
            CBGlobal.cb_remote_history.pop()
        synch_cb_remote_history()


def synch_cb_remote_history():
    cb_remote_history_fl = '__cb_remote_history.7342'
    if not os.path.exists(cb_remote_history_fl):
        with open(cb_remote_history_fl, encoding='UTF-8', mode='x') as file:
            pass

    if CBGlobal.cb_remote_history is None:
        with open(cb_remote_history_fl, encoding='UTF-8') as file:
            entry__split = file.read().split('$7342$')
        CBGlobal.cb_remote_history = entry__split

    os.remove(cb_remote_history_fl)
    with open(cb_remote_history_fl, encoding='UTF-8', mode='w') as file:
        history__joined = "$7342$".join(CBGlobal.cb_remote_history)
        file.write(history__joined)
