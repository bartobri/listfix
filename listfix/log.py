from datetime import datetime

class Log:

	def __init__(self):
		self.log_file = "/tmp/listfix_log.txt"

	def write(self, type, txt):
		txt = txt.rstrip()
		date = datetime.now()
		f = open(self.log_file, "a")
		f.write(f"[{type}] {date}, {txt}\n")
		f.close()

	def info(self, txt):
		self.write("INFO", txt)

	def error(self, txt):
		self.write("ERROR", txt)

	def debug(self, txt):
		self.write("DEBUG", txt)
