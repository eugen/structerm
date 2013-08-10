import os

class PsHandler:

	CommandsHandled = ["ps"]

	def __init__(self):
		pass
		
	def handle(self, command, *args):
		result = []
		pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
		return [{'pid': pid,
		  'name': open(os.path.join('/proc', pid, 'comm'), 'rb').read(),
		  'cmdline': open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()}
		  for pid in pids]
