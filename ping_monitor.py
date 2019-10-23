import json
import subprocess
import requests
import time
from config_ping import *
def send_json_data(url, id_list, status_list, retry_count=3):
	measurements = [{"thing_id": thing_id, "is_up": thing_status} for thing_id, thing_status in zip(id_list, status_list)]
	print(measurements)
	json_data = {
	"ping_measurements": measurements,
	}
	while retry_count > 0:
		try:
			r = requests.post(url, json=json_data)
			if r.status_code == 201:
				return True
			else:
				time.sleep(2)
				print("resp status", r.status_code)
				retry_count -= 1
		except Exception as e:
			print(e)
			time.sleep(1)
			retry_count -= 1

def read_json_file(file_name):
	with open(file_name, "r") as read_file:
		data = json.load(read_file)
	return data

class ping_monitor(object):
	def __init__(self, config_dict, sleep_time=30):
		self.settings = config_dict
		self.sleep_time = sleep_time
		self.initialize()
	def initialize(self):
		self.id_list = [thing_to_monitor["id"] for thing_to_monitor in self.settings['things_to_monitor']]
		self.result_array = [False for i in range(len(self.settings['things_to_monitor']))]
		#self.result_ready_array = [False for i in range(len(self.settings['things_to_monitor']))]
		self.process_array = [False for i in range(len(self.settings['things_to_monitor']))]
		#self.process_init_array = [False for i in range(len(self.settings['things_to_monitor']))]
	def run_loop(self):
		for index, thing_to_monitor in enumerate(self.settings['things_to_monitor']):
			#if self.process_init_array[index] == False:
			self.process_array[index] = subprocess.Popen(['ping','-n', '-w5', '-c3', thing_to_monitor["ip"]], stdout=subprocess.DEVNULL)
				#self.process_init_array[index] = True
		time.sleep(self.sleep_time)
		for index, thing_to_monitor in enumerate(self.settings['things_to_monitor']):
			#if self.process_init_array[index] == False:
			if self.process_array[index].poll() is not None:
				self.result_array[index] = (self.process_array[index].returncode == 0)
			else:
				self.result_array[index] = False
		self.send_results()
	def send_results(self):
		send_json_data(self.settings["url"], self.id_list, self.result_array)
			#self.process_init_array[index] = True
a = ping_monitor(MAIN_CONFIG, 3)
a.run_loop()