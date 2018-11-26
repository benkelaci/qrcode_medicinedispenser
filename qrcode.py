from config_parser import cfg
from mylogger import mylogger as log
from time import sleep, strptime
from multiprocessing import Queue
from pyzbar import pyzbar
import cv2
from myprocess import MyProcess
from control import Control, MOVING


class QRCode(MyProcess):

	def __init__(self, q_last_qrcode_position, moving_state_event):
		super(QRCode, self).__init__()
		self.type = 1
		self.q_last_qrcode_position = q_last_qrcode_position
		self.last_position = 0
		self.source = "/home/pi/qrcode_detect/3.jpg"
		self.moving_state_event = moving_state_event

	def myrun(self):
		if self.moving_state_event.wait(60*10):
			current_position, ts = self.get_qrcode_position()
			#TODO: hysteresis
			# if current_position != self.last_position:
			self.q_last_qrcode_position.put((current_position, ts))
			self.last_position = current_position
			#wait for 2 seconds, while this the motor can move to the required position
		else:
			log.info("no MOVING state in the last 10 minutes")
		sleep(2)

	def get_qrcode_position(self):
		# load the input image
		image = cv2.imread(self.source)
		# find the barcodes in the image and decode each of the barcodes
		barcodes = pyzbar.decode(image)
		# loop over the detected barcodes
		cnt = 0
		x = -1
		delivery_ts = 0
		for barcode in barcodes:
			# extract the bounding box location of the barcode and draw the
			# bounding box surrounding the barcode on the image
			(x, y, w, h) = barcode.rect
			cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

			# the barcode data is a bytes object so if we want to draw it on
			# our output image we need to convert it to a string first
			barcode_data = barcode.data.decode("utf-8")
			barcode_type = barcode.type

			# draw the barcode data and barcode type on the image
			text = "{} ({})".format(barcode_data, barcode_type)
			try:
				delivery_ts = strptime(barcode_data, "%d.%m.%Y%H:%M")
				log.debug("delivery_ts: " + str(delivery_ts))
			except Exception as e:
				log.error(e, exc_info=True)
				continue
			if not "qr" in barcode_type.lower():
				log.info("no QR code type found: " + str(barcode_type))
				continue

			cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
			            0.5, (0, 0, 255), 2)

			# print the barcode type and data to the terminal
			log.info("Found QR code: {}".format(barcode_type, barcode_data))

			# show the output image
			# cv2.imwrite(cfg.file.root_directory + "Image_" + str(cnt) + " .jpg", image)
			break
		# cv2.waitKey(0)
		return x, delivery_ts

if __name__ == '__main__':
	q = Queue()
	qrcode = QRCode(q)
	# qrcode.start()
	qrcode.get_qrcode_position()
	sleep(5)
	print("finished")