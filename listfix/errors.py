import sys
from .log import Log

class Errors:

	def __init__(self, debug=False):
		self.debug = debug
		self._exception_handler = None
		self.log = Log()

	def set_exception_handler(self):
		self._exception_handler = sys.excepthook
		sys.excepthook = self.exception_handler

	def exception_handler(self, exception_type, exception, traceback):
		self.log.error(f"{exception_type.__name__}, {exception}")
		if (self.debug):
			self._exception_handler(exception_type, exception, traceback)
		else:
			print(f"Error: {exception}")