from config_parser import cfg
from mylogger import mylogger
from time import sleep
import threading
import RPi.GPIO as GPIO
from mylogger import mylogger as log
from multiprocessing import Queue
from myprocess import MyProcess

#TODO: change to negated(because my relay is negated)
MY1=0
MY0=1
#estimated speed:
# 6 seconds, 0.06 m => 0.01 m/s
class Motor(MyProcess):

	def __init__(self, q_motor_on_period):
		super(Motor, self).__init__()
		self.type = 1
		self.q_motor_on_period = q_motor_on_period
		self.pin = cfg.motor.bcm_pin_number
		GPIO.setmode(GPIO.BCM)
		#TODO: change to GPIO.LOW (because my relay is negated) or uncomment next line
		#GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.HIGH)

	def myrun(self):
		self.period = None
		if not self.q_motor_on_period.empty():
			self.period = self.q_motor_on_period.get()
			self.mydebug("period")
		if self.period is not None:
			self.motor_control(self.period)
		sleep(0.1)

	def motor_control(self, period):
		GPIO.output(self.pin, MY1)
		log.debug("pin: 1")
		threading.Timer(period, self.motor_stop).start()

	def motor_stop(self):
		log.debug("pin: 0")
		GPIO.output(self.pin, MY0)


if __name__ == '__main__':
	q = Queue()
	motor = Motor(q)
	motor.start()
	motor.motor_control(3)
	sleep(4)
	motor.motor_control(1)
	sleep(2)
	print("finished")