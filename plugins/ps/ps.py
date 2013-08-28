import os
import psutil
import getpass

class PsHandler:

	CommandsHandled = ["ps"]

	def __init__(self):
		pass
	
	def handle(self, command, *args):
		return [{'name': p.name, 'cmdline': " ".join(p.cmdline), 'pid': p.pid} 
			for p in psutil.get_process_list() 
			if p.username == getpass.getuser()]
