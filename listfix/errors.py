import sys

class Errors:

	def __init__(self, log=None, debug=False):
		self.log = log
		self.debug = debug
		self._exception_handler = None

	def set_exception_handler(self):
		self._exception_handler = sys.excepthook
		sys.excepthook = self.exception_handler

	def exception_handler(self, exception_type, exception, traceback):
		if (self.log):
			self.log.error(f"{exception_type.__name__}, {exception}")
		if (self.debug):
			self._exception_handler(exception_type, exception, traceback)
		else:
			print(f"Error: {exception}")