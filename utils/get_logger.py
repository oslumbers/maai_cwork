# -*- coding:utf-8  -*-
import logging
import time
import os


def get_logger(log_path, name, save_file=False, console_out=False, json_file=False):
    if not os.path.exists(log_path):
        os.mkdir(log_path)

    logger = logging.getLogger(name='Jidi')
    logger.setLevel(logging.INFO)
    rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
    log_name = log_path + rq + '_' + name+  '.log'
    json_log_name = log_path + rq + '_' + name + '.json'
    logfile = log_name
    if save_file:
        fh = logging.FileHandler(logfile, mode='a')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    if console_out:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logger.addHandler(console)

    if json_file:
        fh_json = logging.FileHandler(json_log_name, mode='a')
        fh_json.setLevel(logging.DEBUG)
        formatter_json = logging.Formatter("%(message)s")
        fh_json.setFormatter(formatter_json)
        logger.addHandler(fh_json)

    return logger