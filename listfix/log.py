class Log:

	def __init__(self):
		self.log_file = open("/tmp/listfix_log.txt", "a")

	def info(self, txt):
		txt = txt.rstrip()
		self.log_file.write(f"[INFO] {txt}\n")

	def error(self, txt):
		txt = txt.rstrip()
		self.log_file.write(f"[ERROR] {txt}\n")

	def debug(self, txt):
		txt = txt.rstrip()
		self.log_file.write(f"[DEBUG] {txt}\n")

	def close(self):
		self.log_file.close()