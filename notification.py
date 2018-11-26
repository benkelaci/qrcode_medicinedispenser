from config_parser import cfg
from mylogger import mylogger
from time import sleep
import threading
from mylogger import mylogger as log
from multiprocessing import Queue
from myprocess import MyProcess


MY1=0
MY0=1

class Notification(MyProcess):

	def __init__(self, notification_event):
		super(Notification, self).__init__()
		self.notification_event = notification_event

	def myrun(self):
		if self.notification_event.wait(3600):
			log.info("notification_event is set")
			self.show()
			sleep(1)
			self.notification_event.clear()
		else:
			log.info("no notification_event in the last 60 minutes")
		sleep(1)

	def show(self):
		#TODO
		pass


if __name__ == '__main__':
	q = Queue()

	print("finished")