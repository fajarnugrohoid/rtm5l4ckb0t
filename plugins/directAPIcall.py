from __future__ import unicode_literals
from rtmbot.core import Plugin
from core import MongoDBConn
import re
import datetime, json, requests

class APICall(Plugin, MongoDBConn):

	def catch_all(self, data):
		print("data_catch_all:")
		#print("SLACK_TOKENxxx")

		#print(self.config.get('SLACK_TOKEN', None))
		#print(self.xxxx())
		#print(self.outputs)
		#print(tests)
		#self.process_message(data)

	def insert(self):
		try:
			karma_db=self.connDB()
			for user in self.slack_client.api_call("users.list")["members"]:
				if karma_db.coll_member.find({"slack_id": user["id"]}).count() <= 0:
					print('start insert data')
					karma_db.coll_member.insert_one({
						"slack_id": user["id"],
						"name":user["name"],
						"real_name":user["real_name"],
						"display_name":user["profile"]["display_name"],
						"point":0
					})
				print('\nInserted data successfully\n')
		except Exception as e:
			print(str(e))

	def read(self):
		try:
			karma_db=self.connDB()
			empCol = karma_db.coll_member.find()
			print('\n All data from EmployeeData Database \n')
			for emp in empCol:
				print(emp)
		except Exception as e:
			print(str(e))

	def update(self, resp_thanks):
		try:
			karma_db=self.connDB()
			#for user in self.slack_client.api_call("users.list")["members"]:
			print("resp_thanks:" + resp_thanks)
			split_resp=resp_thanks.split("@")
			print(split_resp)
			print("split_resp[1]:" + split_resp[1])
			cls_display_name=re.sub('[^A-Za-z0-9]+', '', split_resp[1])
			print("cls_display_name:" + cls_display_name)
			get_info_target=karma_db.coll_member.find(
					{"slack_id":cls_display_name}
				)
			for slack_id_target in get_info_target:
				sum_point = int(slack_id_target["point"]) + 10
				print(slack_id_target["point"])

			karma_db.coll_member.update_one(
			{"slack_id": cls_display_name},
			{
				'$set': {
						'point': sum_point
					}
			}, 
			upsert=False)
		except Exception as e:
			raise

	def formatLeaderMessage(self, members):
		message = ""
		print("members : " + str(members))
		global LEADERBOARD_URL
		LEADERBOARD_URL = "https://fmi-talk.slack.com"
		# add each member to message
		for username, score, stars in members:
			print("username:" + username)
			print("score:" + str(score))
			print("stars:" + str(stars))
			message += "\n*{}* {} Points, {} Stars".format(username, score, stars)
			print("message in loop:" + str(message))
		
		message += "\n\n<{}|View Online Leaderboard>".format(LEADERBOARD_URL)
		print("message : " + str(message))
		return message

	def parseMembers(self, members_json):
		# get member name, score and stars
		print("members_json:{}", members_json)
		print(members_json.values())
		members = [(m["name"], m["l_score"], m["stars"]) for m in members_json.values()]
		# sort members by score, decending
		members.sort(key=lambda s: (-s[1], -s[2]))
		return members

	def postMessage(self, message):
		print("postMessage:" + str(message))
		payload = json.dumps({
			"icon_emoji": ":ghost:",
			"username": "Advent Of Code Leaderboard",
			"text": message
		})
		SLACK_WEBHOOK = "https://hooks.slack.com/services/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"
		requests.post(
			SLACK_WEBHOOK,
			data=payload,
			headers={"Content-Type": "application/json"}
		)

	def display_leaderboard(self):
		print("display_leaderboard")
		json = {"296557":{"stars":0,"last_star_ts":"1969-12-31T19:00:00-0500","name":"Fajar N","l_score":0,"g_score":0,"level":{},"id":"296557"}}
		print("json_leaderboard : " + str(json))
		try:
			karma_db=self.connDB()
			get_limit_members = karma_db.coll_member.find().limit(5).sort("point",pymongo.ASCENDING)
			for row_member in get_limit_members:
				json += {"296557":{"stars":0,"last_star_ts":"1969-12-31T19:00:00-0500","name":row_member["name"],"l_score":row_member["score"],"g_score":row_member["score"],"level":{},"id":"296557"}}
				print(row_member)
		except Exception as e:
			raise
		# get members from json
		members = self.parseMembers(json)
		print("members_leaderboard : {}", members)
		# generate message to send to slack
		message = self.formatLeaderMessage(members)
		print("message_leaderboard : " + str(message))
		# send message to slack
		self.postMessage(message)

	def process_message(self, data):
		if 'message' in data['type']:
			if 'sync_member' in data['text']:
				#for user in self.slack_client.api_call("users.list")["members"]:
				#	print(user["name"], user["id"])
				self.insert()
				self.read()

		if 'message' in data['type']:
			if 'thanks' in data['text']:
				self.update(data['text'])

		if 'message' in data['type']:
			print(data['text'])
			if '<@U89QAG4N5> leaderboard' in data['text']:
				print("start to leaderboard")
				self.display_leaderboard()
