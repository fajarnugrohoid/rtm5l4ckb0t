from __future__ import print_function
from __future__ import unicode_literals
from rtmbot.core import Plugin
from slackclient import SlackClient as sc

class RepeatPlugin(Plugin):

    def process_message(self, data):
        print(data)
        #print(sc.api_call("users.list")["members"])
		#for user in sc.api_call("users.list")["members"]:
        #	print(user["name"], user["id"])
        #if data['channel'].startswith("g"):#self.outputs.append([data['channel'], 'from repeat1 "{}" in channel {}'.format(data['text'], data['channel'])])