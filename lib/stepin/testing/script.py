# encoding: UTF8

import argparse
import codecs
import os
import re
import subprocess
import sys
import datetime as dtm

from stepin.file_utils import ensure_path, check_remove
from stepin.script import script_log_config, spath
from stepin.testing.proc_utils import wait_process

__modulePath = os.path.abspath(os.path.dirname(__file__))


def sub_prj_path(*pp):
    sub_root = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.abspath(os.path.join(sub_root, os.pardir, os.pardir, *pp))


def prj_path(*pp):
    return os.path.abspath(os.path.join(__modulePath, os.pardir, os.pardir, os.pardir, os.pardir, *pp))


def parse_config(path):
    config = {}
    for line in open(path):
        data = line.rstrip().split('\t')
        config[data[0]] = data[1]
    return config


def _prefix_file_name(path, prefix):
    dir_path, file_name = os.path.split(path)
    return os.path.join(dir_path, prefix + file_name)


def file2str(f, encoding=None):
    if encoding is None:
        with open(f, 'rb') as of:
            return of.read()
    else:
        with codecs.open(f, 'rb', encoding=encoding) as of:
            return of.read()


def str2file(s, f, encoding=None):
    if encoding is None:
        with open(f, 'wb') as of:
            of.write(s)
            of.close()
    else:
        with codecs.open(f, 'wb', encoding=encoding) as of:
            of.write(s)
            of.close()


class SystemTest(object):
    def __init__(self):
        self.args = None
        self.original_config_path = None
        self.config_path = None
        self.result_path = None
        self.config = None
        self.is_profiling = False

    def get_profile_path(self):
        return self.rpath('profile.bin')

    def set_is_profiling(self, value):
        self.is_profiling = value

    def rpath(self, *pp):
        return os.path.join(self.result_path, *pp)

    def prepare_options(
        self, config_path=None, config_statements=False, result_path=None,
        locs=None, globs=None
    ):
        if globs is None:
            globs = globals()
        if locs is None:
            locs = locals()
        if config_path is None:
            config_path = spath('test.conf.py')
        if result_path is None:
            result_path = spath('result')

        def fill_req(name, value):
            if name not in locs and name not in globs:
                locs[name] = value

        self.original_config_path = config_path
        self.result_path = result_path
        fill_req('dtm', dtm)
        locs['spath'] = spath
        locs['cpath'] = spath
        locs['app_name'] = 'test'
        from stepin.script import ensured_dir, ensured_path, file_exp
        locs['ensured_dir'] = ensured_dir
        locs['ensured_path'] = ensured_path
        locs['include'] = file_exp
        fill_req('file_text', file2str)
        if result_path is not None:
            locs['rpath'] = lambda *pp: spath(result_path, *pp)
        p = argparse.ArgumentParser()
        p.add_argument('--debug', action='store_true')
        p.add_argument('--keep-results', dest='keep_results', action='store_true')
        self.args = p.parse_args()

        script_log_config(level='DEBUG' if self.args.debug else 'ERROR')
        if config_path is None:
            return None
        if self.args.debug:
            config_path = _prefix_file_name(config_path, '__')
            config_text = file2str(self.original_config_path, encoding='utf-8')
            config_text = re.sub(
                r"'((?:screen_)?level)'\s*:\s*'ERROR'", "'\\1' : 'DEBUG'", config_text, re.MULTILINE
            )
            config_text = re.sub(
                r"\b((?:screen_)?level)\s*=\s*'ERROR'", "\\1 = 'DEBUG'", config_text, re.MULTILINE
            )
            str2file(config_text, config_path, encoding='utf-8')
        self.config_path = config_path

        if config_statements:
            exec(open(config_path).read(), globs, locs)
            if 'config' not in locs:
                raise Exception('Configuration variable "config" has not been defined in configuration file')
            config = locs['config']
        else:
            config = file_exp(config_path, locs=locs, globs=globs)
        self.config = config
        return config

    def start_process(self, cmd=None, script=None, init_method=None):
        if script is not None:
            python = 'python' + str(sys.version_info[0])
            cmd = [python]
            if self.is_profiling:
                cmd += ['-m', 'cProfile', '-o', self.get_profile_path()]
            cmd += [
                sub_prj_path(script),
                '--config', self.config_path,
                '--result-path', self.result_path
            ]
        if self.result_path is not None:
            if not self.args.keep_results:
                check_remove(self.result_path)
                # subprocess.check_call('rm -rf ' + self.result_path, shell=True)
            ensure_path(self.result_path)
        if init_method is not None:
            init_method()
        return subprocess.Popen(cmd)

    @staticmethod
    def finish_process(p, check_method, timeout=30, terminate_timeout=5):
        try:
            res = wait_process(p, dtm.timedelta(seconds=timeout))
        except KeyboardInterrupt:
            return
        if res is None:
            print('ERROR: Timeout waiting process finish')
            p.terminate()
            wait_process(p, dtm.timedelta(seconds=terminate_timeout))
        elif res == 0:
            if check_method is not None:
                check_method()
        else:
            print('WARNING: test returned ' + str(p.poll()))

    def run_process(
        self, cmd=None, script=None,
        check_method=None, init_method=None,
        timeout=30, terminate_timeout=5
    ):
        p = self.start_process(cmd=cmd, script=script, init_method=init_method)
        self.finish_process(p, check_method, timeout=timeout, terminate_timeout=terminate_timeout)

    def begin_test(self):
        if self.result_path is not None:
            if not self.args.keep_results:
                check_remove(self.result_path)
            ensure_path(self.result_path)


def std_system_test(script_name, conf_name='test.conf.py', check_proc=None, **kwargs):
    test = SystemTest()
    config = test.prepare_options(
        spath(conf_name),
        result_path=spath('result'),
        locs=locals(), globs=globals()
    )

    test.run_process(
        [
            'python', script_name if os.path.isabs(script_name) else sub_prj_path(script_name),
            '--config', test.config_path,
            '--result-path', test.result_path
        ],
        None if check_proc is None else lambda: check_proc(config),
        **kwargs
    )
