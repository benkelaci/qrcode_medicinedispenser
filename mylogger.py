import sys
import logging
from config_parser import cfg
from logging.handlers import TimedRotatingFileHandler

logging.getLogger("qrcode_machinecontrol").setLevel(logging.ERROR)
log_formatter = logging.Formatter("%(asctime)s.%(msecs)03d %(levelname)7s %(processName)10s -  %(message)s", "%H:%M:%S")
mylogger = logging.getLogger()
mylogger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
rotate_logs_handler = TimedRotatingFileHandler(cfg.file.log_path, when="midnight", backupCount=30)
rotate_logs_handler.setFormatter(log_formatter)
mylogger.addHandler(console_handler)
mylogger.addHandler(rotate_logs_handler)
