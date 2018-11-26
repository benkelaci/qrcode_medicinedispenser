import multiprocessing as mp
from mylogger import mylogger as log
from time import sleep
import inspect

class MyProcess(mp.Process):

	def __init__(self):
		super(MyProcess, self).__init__()


	def run(self):
		while self.is_alive():
			try:
				self.myrun()
			except Exception as e:
				log.error(e, exc_info=True)
				sleep(2)
		log.info(self.__class__.__name__ + " finished")

	def myrun(self):
		raise NotImplementedError()

	def retrieve_name(self, var):
		"""
		Gets the name of var. Does it from the out most frame inner-wards.
		:param var: variable to get name from.
		:return: string
		"""
		for fi in reversed(inspect.stack()):
			names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]
			if len(names) > 0:
				return names[0]
		return "<unknown>"


	def mydebug(self, var):
		log.debug("{}: {}".format(var, getattr(self, var)))

	def myinfo(self, var):
		log.info("{}: {}".format(var, getattr(self, var)))

	def test_info(self, var):
		log.info("TEST: set {} to {}".format(var, getattr(self, var)))