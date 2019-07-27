import time
import datetime
import threading


class Logger:
    def __init__(self, module_name, log_checks=False, debug_level=4):
        self.last_time = time.time()
        self.debug_level = debug_level
        self.last_percentage = 0
        self.module_name = module_name
        self.log_checks = log_checks
        self.colors = {
            'HEADER': '\033[95m',
            'OKBLUE': '\033[94m',
            'OKGREEN': '\033[92m',
            'WARNING': '\033[93m',
            'FAIL': '\033[91m',
            'ENDC': '\033[0m',
            'BOLD': '\033[1m',
            'UNDERLINE': '\033[4m',
            'WHITE': ''
        }
        self.checks = []
        self.operations = []
        self.last_check = None
        self.progress_started = False

    def debug(self, msg, color='WHITE'):
        if self.debug_level > 3:
            color = self.colors[color]
            if self.progress_started: print('\n')
            print(color + f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: {self.module_name} DEBUG: {msg}' + self.colors['ENDC'])

    def info(self, msg, color='WHITE'):
        if self.debug_level > 2:
            color = self.colors[color]
            if self.progress_started: print('\n')
            print(color + f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: {self.module_name} INFO: {msg}' + self.colors['ENDC'])

    def warning(self, msg, color='WARNING'):
        if self.debug_level > 1:
            color = self.colors[color]
            if self.progress_started: print('\n')
            print(color + f'{datetime.datetime.now()}: {self.module_name} WARNING: {msg}' + self.colors['ENDC'])

    def error(self, msg, color='FAIL'):
        if self.debug_level > 0:
            color = self.colors[color]
            if self.progress_started: print('\n')
            print(color + f'{datetime.datetime.now()}: {self.module_name} ERROR: {msg}' + self.colors['ENDC'])

    def progress(self, iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
        # Print New Line on Complete
        if iteration == total:
            self.progress_started = False
        else:
            self.progress_started = True




