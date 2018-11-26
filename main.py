from control import Control
from qrcode import QRCode
from motor import Motor
from cutter import Cutter
from notification import Notification
from multiprocessing import Queue, Event
from mylogger import mylogger as log
from time import sleep
from config_parser import cfg


def test():
	print("just test, nothing else")
	pass


def mymain():
	try:
		q_motor_on_period = Queue()
		q_last_qrcode_position = Queue()
		cutter_event = Event()
		notification_event = Event()
		moving_state_event = Event()
		log.info("Starting processes...")
		control = Control(
			q_last_qrcode_position=q_last_qrcode_position,
			q_motor_on_period=q_motor_on_period,
			cutter_event=cutter_event,
			notification_event=notification_event,
			moving_state_event=moving_state_event
		)
		if cfg.test.state:
			log.info("TESTING: Running")
		control.start()
		motor = Motor(q_motor_on_period)
		motor.start()
		qrcode = QRCode(q_last_qrcode_position, moving_state_event)
		qrcode.start()
		cutter = Cutter(cutter_event)
		# cutter.start()
		notification = Notification(notification_event)
		# notification.start()
		log.info("Running")
		if cfg.test.state:
			sleep(200)
			qrcode.terminate()
			control.terminate()
	except Exception as e:
		log.error(e, exc_info=True)



if __name__ == '__main__':
	test()
	mymain()