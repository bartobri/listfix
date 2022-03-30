import sys

class Errors:

	def __init__(self, debug=False):
		self.debug = debug
		self._exception_handler = None

	def set_exception_handler(self):
		self._exception_handler = sys.excepthook
		sys.excepthook = self.exception_handler

	def exception_handler(self, exception_type, exception, traceback):
		if (self.debug):
			self._exception_handler(exception_type, exception, traceback)
		else:
			print(f"Error: {exception}")