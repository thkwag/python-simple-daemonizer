import sys
import os
import time
import logging
import logging.handlers
import traceback
import re
import signal

if sys.platform != "win32":
    from simple_daemonizer import SimpleDaemonizer

script_base_dir = os.path.dirname(os.path.realpath(__file__))
daemon_name = os.path.splitext(os.path.basename(__file__))[0]

cnt = 0


def do_something(arg1, arg2):
    global logger
    global cnt

    logger.debug("arg1: " + arg1 + ", arg2: " + arg2)

    while True:
        cnt = cnt + 1
        logger.debug(cnt)
        time.sleep(2)


def get_logger(name, log_dir):
    # Logging
    default_log_level = logging.DEBUG

    if not os.path.exists(log_dir): os.makedirs(log_dir)

    logger = logging.getLogger(name)
    logger.setLevel(default_log_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(default_log_level)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(console_handler)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_dir + name + '.log',
        when='midnight',
        interval=1,
        encoding='utf-8'
    )
    file_handler.suffix = '.%Y%m%d'
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s'
    ))
    logger.addHandler(file_handler)

    return logger, file_handler


def main():
    if sys.platform == "win32" or (len(sys.argv) > 1 and sys.argv[1] == '--'):
        do_something('foo', 'bar')

    else:
        if len(sys.argv) == 1:
            print(f"Usage: python {daemon_name}.py [ start | stop | restart | status ]")
            sys.exit(0)

        cmd = sys.argv[1]
        daemon = SimpleDaemonizer(
            daemon_name,
            script_base_dir,
            log_file_handler=file_handler
        )
        daemon.register_func(do_something, 'foo', 'bar')
        daemon.run_command(cmd)


if __name__ == "__main__":
    logger, file_handler = get_logger(daemon_name, script_base_dir + os.sep + 'logs' + os.sep)

    main()
