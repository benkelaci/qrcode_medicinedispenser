from config_parser import cfg
from mylogger import mylogger
from time import sleep
import threading
import RPi.GPIO as GPIO
from mylogger import mylogger as log
from multiprocessing import Queue
from myprocess import MyProcess


MY1=0
MY0=1

class Cutter(MyProcess):

	def __init__(self, cutter_event):
		super(Cutter, self).__init__()
		self.cutter_event = cutter_event
		self.pin = int(cfg.cutter.bcm_pin_number)
		self.on_period = float(cfg.cutter.on_period)

	def myrun(self):
		if self.cutter_event.wait(3600):
			log.info("cutter_event is set")
			self.motor_control(self.on_period)
			sleep(1)
			self.cutter_event.clear()
		else:
			log.info("no cutter_event in the last 60 minutes")
		sleep(0.5)

	def motor_control(self, period):
		GPIO.output(self.pin, MY1)
		log.debug("pin: 1")
		threading.Timer(period, self.motor_stop).start()

	def motor_stop(self):
		log.debug("pin: 0")
		GPIO.output(self.pin, MY0)


if __name__ == '__main__':
	q = Queue()

	print("finished")