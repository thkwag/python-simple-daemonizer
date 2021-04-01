import sys
import os
import signal
import traceback
import re
import daemon
from daemon import pidfile
import logging
import logging.handlers

class SimpleDaemonizer:

    def __init__(
            self,
            daemon_name,
            working_directory,
            pid_dir = "./.pids",
            log_dir = "./logs",
            log_file_handler:logging.Handler = None,
        ) -> None:

        self.daemon_name = daemon_name
        self.working_directory = working_directory
        self.log_file_handler = log_file_handler

        self.log_dir = re.sub("/$", "", log_dir) + os.sep
        if not os.path.exists(self.log_dir): os.makedirs(self.log_dir)

        self.pid_dir = re.sub("/$", "", pid_dir) + os.sep
        if not os.path.exists(self.pid_dir): os.makedirs(self.pid_dir)

        self.pid_lock_file = pidfile.PIDLockFile(self.pid_dir + daemon_name + '.pid')

        self._init_logger()

    def _init_logger(self):

        log_level = logging.DEBUG

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        if self.log_file_handler is None:
            file_log_formatter = logging.Formatter(
                    '[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s'
                )
            file_handler = logging.handlers.TimedRotatingFileHandler(
                filename = self.log_dir + self.daemon_name + '.log',
                when='midnight', 
                interval=1,
                encoding='utf-8'
                )
            file_handler.suffix = '.%Y%m%d'
            file_handler.setFormatter(file_log_formatter)

            self.log_file_handler = file_handler
            
        self.logger.addHandler(self.log_file_handler)

    def _daemonize(self):
        try:
            with daemon.DaemonContext(
                    working_directory = self.working_directory,
                    umask = 0o077,
                    pidfile = self.pid_lock_file,
                    stdout = None,
                    stderr = None,
                    files_preserve=[self.log_file_handler.stream]
                ) as context:

                self.logger.info(f"Daemon '{self.daemon_name}' started")

                self.func(*self.args)

        except Exception as e:
            self.logger.info(e)
            traceback.print_exc()

    def register_func(self, func, *args):
        self.func = func
        self.args = args

    def run_command(self, command):
        try:
            if command == 'start':
                self.start()
            elif command == 'stop':
                self.stop()
            elif command == 'restart':
                self.stop(restart = True)
            elif command == 'status':
                self.status()
            else:
                print(f"Command '{command}' does not exists.")

        except Exception as e:
            traceback.print_exc()
            
    def start(self):
        if self.pid_lock_file.is_locked():
            lock_pid = self.pid_lock_file.read_pid()
            print(f"Daemon '{self.daemon_name}' is already running. (pid: {lock_pid})")
            exit(0)

        print(f"Daemon '{self.daemon_name}' started.")
        
        self._daemonize()

    def stop(self, restart = False):
        if not self.pid_lock_file.is_locked():
            print(f"Daemon '{self.daemon_name}' is not started.")
            exit(0)

        lock_pid = int(self.pid_lock_file.read_pid())
        print(f"Stopping daemon '{self.daemon_name}' (pid: {lock_pid})")

        try:
            os.kill(lock_pid, signal.SIGQUIT)
        except OSError:
            traceback.print_exc()
        except TypeError:
            traceback.print_exc()

        self.pid_lock_file.break_lock()

        stop_msg = f"Daemon '{self.daemon_name}' is stopped."
        print(stop_msg)
        self.logger.info(stop_msg)

        if restart is True:
            self.start()
        else:
            exit(0)

    def status(self):
        if self.pid_lock_file.is_locked():
            running_pid = self.pid_lock_file.read_pid()
            print(f"Daemon '{self.daemon_name}' is running. (pid: {running_pid})")
            exit(0)
        else:
            print(f"Daemon '{self.daemon_name}' is not running.")
