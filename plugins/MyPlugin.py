from __future__ import print_function
from __future__ import unicode_literals
from rtmbot.core import Plugin
from core import Plugin, Job

class myJob(Job):
	def run(self, slack_client):
		return [["C12345667", "hello world"]]

class MyPlugin(Plugin):
	def catch_all(self, data):
		print("data_catch_all:" + data)
		self.process_message(data)

	def process_message(self, data):
		self.outputs.append([data['channel'], 'from repeat1 "{}" in channel {}'.format(data['text'], data['channel'])])