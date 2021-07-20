# encoding=utf-8

import logging
import logging.config
import io


class TestLogConfig(object):
    def __init__(self):
        self.messages = io.StringIO()

    def __enter__(self):
        logging.config.dictConfig(dict(
            version=1,
            disable_existing_loggers=False,
            formatters=dict(
                concise=dict(
                    format='[%(levelname)s] %(name)s %(message)s',
                    datefmt='%H:%M:%S'
                ),
            ),
            handlers=dict(
                default={
                    'level': 'DEBUG',
                    'formatter': 'concise',
                    'class': 'logging.StreamHandler',
                    'stream': self.messages
                },
            ),
            loggers={
                '': dict(
                    handlers=['default'],
                    level='DEBUG',
                    propagate=True
                ),
            }
        ))
        return self

    # noinspection PyUnusedLocal
    def __exit__(self, type_, value, traceback):
        logging.config.dictConfig(dict(
            version=1,
            disable_existing_loggers=False,
        ))
        return False
