from config_parser import cfg
from mylogger import mylogger as log
from time import sleep, mktime
from datetime import datetime as dt
from datetime import timedelta as td
from myprocess import MyProcess

MOVING=0
WAIT_FOR_TIME=1
WAIT_FOR_BUTTON=2
CUT = 3

class Control(MyProcess):

	def __init__(self,
	             q_last_qrcode_position,
	             q_motor_on_period,
	             cutter_event,
	             notification_event,
	             moving_state_event):
		super(Control, self).__init__()
		self.type = 1
		self.q_last_qrcode_position = q_last_qrcode_position
		self.q_motor_on_period = q_motor_on_period
		self.last_ts = dt.now()
		self.last_qrcode_position = 0
		Control.state = MOVING
		self.cutter_event = cutter_event
		self.notification_event = notification_event
		self.delivery_datetime = dt.now()
		self.moving_state_event = moving_state_event

	def myrun(self):
		if Control.state == MOVING:
			self.moving_state_event.set()
			if not self.q_last_qrcode_position.empty():
				cnt = 0
				#TODO: wait until the period is pretty small - this means it is in good area
				while True:
					self.period, self.last_qrcode_position, delivery_ts = self.get_required_period()
					if cfg.test.state == 1:
						additional = cnt * cfg.test.case_active.per_cnt
						self.last_qrcode_position = cfg.test.case_active.last_qrcode_position1 + additional
						self.test_info("last_qrcode_position")
						self.test_info("last_qrcode_position")
						self.period = Control.calculate_period(self.last_qrcode_position, cfg.position.expected_cut_position)
						self.test_info("period")
						cnt += 1
					if self.last_qrcode_position > cfg.position.expected_cut_position:
						break
					self.q_motor_on_period.put(self.period)
					if self.period > 2:
						self.period = 2
					sleep(self.period + 0.5)
				log.info("over the expected position: {}".format(self.last_qrcode_position))
				self.delivery_datetime = dt.fromtimestamp(mktime(delivery_ts))
				#if the delivery time is elapsed, then you do not need to wait for button
				# (skip WAIT_FOR_TIME and WAIT_FOR_BUTTON state)
				mynow = dt.now().replace(second=0)
				if cfg.test.state == 1:
					new_datetime = (dt.now() + td(seconds=10)).replace(second=0)
					self.delivery_datetime = new_datetime
				self.mydebug("delivery_datetime")
				if self.delivery_datetime < mynow:
					Control.state = CUT
				else:
					Control.state = WAIT_FOR_TIME
					if cfg.test.state == 1:
						new_datetime = dt.now().replace(second=0) - td(seconds=121)
						self.delivery_datetime = new_datetime
						self.test_info("delivery_datetime")
		else:
			self.moving_state_event.clear()
			if Control.state == WAIT_FOR_TIME:
				current_minute = dt.now().replace(second=0)
				if self.delivery_datetime < current_minute:
					self.dt_diff_total_seconds = (current_minute - self.delivery_datetime)
				else:
					self.dt_diff_total_seconds = (self.delivery_datetime - current_minute)
				minute_1 = td(seconds=60)
				if self.dt_diff_total_seconds > minute_1:
					self.myinfo("dt_diff_total_seconds")
					self.notification_event.set()
					Control.state = WAIT_FOR_BUTTON
			else:
				if Control.state == WAIT_FOR_BUTTON:
					#TODO: EVENT based, instead of check current status
					self.mybutton_state = self.button_pressed()
					if cfg.test.state == 1:
						self.mybutton_state = bool(cfg.test.case_active.button1)
						self.test_info("mybutton_state")
						sleep(1)
						log.info("TEST: wait 1 seconds")
					if self.mybutton_state:
						log.info("button_pressed")
						Control.state = CUT
				else:
					if Control.state == CUT:
						log.info("cut")
						self.cutter_event.set()
						#wait the cutter time plus 0.5 seconds for safe reason
						sleep(cfg.cutter.on_period + 0.5)
						log.debug("change state to MOVING")
						Control.state = MOVING
		sleep(0.05)

	def get_required_period(self):
		last_qrcode_position, delivery_ts = self.q_last_qrcode_position.get()
		if last_qrcode_position == -1:
			#skip
			return 0, 0, 0
		current_ts = dt.now()

		log.debug("qrcode pos: {}".format(last_qrcode_position))
		elapsed_time = (current_ts - self.last_ts).seconds
		calculated_qrcode_position = Control.calculate_position(self.last_qrcode_position, elapsed_time)
		if last_qrcode_position != calculated_qrcode_position:
			log.warning("measured/calculated: {}/{}".format(last_qrcode_position, calculated_qrcode_position))
		period = Control.calculate_period(last_qrcode_position, cfg.position.expected_cut_position)
		log.debug("period: {}".format(period))
		if period > 1.5:
			log.warning("period is close to 2 seconds")
		self.last_ts = current_ts
		return period, last_qrcode_position, delivery_ts

	@staticmethod
	def calculate_position(last_position, elapsed_time):
		return last_position + (cfg.motor.speed * elapsed_time * cfg.position.m_per_pixel)

	@staticmethod
	def calculate_period(current_position, expected_position):
		return (expected_position - current_position) / (cfg.motor.speed * cfg.position.m_per_pixel)

	def button_pressed(self):
		return False