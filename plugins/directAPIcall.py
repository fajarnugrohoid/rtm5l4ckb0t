from __future__ import unicode_literals
from rtmbot.core import Plugin
from core import MongoDBConn
import re
import datetime, json, requests
from pymongo import MongoClient
import datetime

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
					if user["is_bot"]==False:
						print('start insert data:', user)
						karma_db.coll_member.insert_one({
							"slack_id": user["id"],
							"name":user["name"],
							"real_name":user["real_name"],
							"display_name":user["profile"]["display_name"],
							"point":0,
							"updated_at":datetime.datetime.today(),
							"created_at":datetime.datetime.today()
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

	def check_point(self):
		try:
			today = datetime.datetime.today()
			karma_db=self.connDB()
			members_coll = karma_db.coll_member.find()
			for member in members_coll:
				#var_update_at=datetime.datetime.strptime(str(member["updated_at"]), "%Y-%m-%d")
				
				updated_at = str(member["updated_at"])
				print("\n")
				my_time = datetime.datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S.%f")
				my_format = "%Y-%m-%d"

				update_str_formated = my_time.strftime(my_format)
				today_str_formated = today.strftime(my_format)

				update_str_date = datetime.datetime.strptime(update_str_formated, my_format)
				today_str_date = datetime.datetime.strptime(today_str_formated, my_format)

				print("update_str_date:", update_str_date)
				print("today:", today_str_date)
				if today_str_date != update_str_date:
					print("inside today_str_date != update_str_date")
					diff = today - update_str_date
					diffdays=diff.days
					print("diffdays:",diffdays)
					sum_point = int(member["point"]) + (int(diffdays)*10)
					print("sum_point:", sum_point)
					karma_db.coll_member.update_one(
						{"slack_id": member["slack_id"]},
						{
							'$set': {
								'point': sum_point,
								"updated_at":datetime.datetime.today()
							}
						}, upsert=False)

		except Exception as e:
			raise

	def update(self, resp_thanks, all_info):
		try:
			karma_db=self.connDB()
			#for user in self.slack_client.api_call("users.list")["members"]:
			print("all_info:", all_info)
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
				sum_point = int(slack_id_target["point"]) + 1
				print("slack_id_target:", slack_id_target["point"])

			karma_db.coll_member.update_one(
			{"slack_id": cls_display_name},
			{
				'$set': {
						'point': sum_point
					}
			}, 
			upsert=False)
			send_by = self.get_info_member_by_id(all_info['user'])
			receive_by = self.get_info_member_by_id(cls_display_name)
			message = str(receive_by) + ' receives 1 point from ' + str(send_by) + '. '+ str(receive_by) +' now has ' + str(sum_point) + '  points'
			var_channel = all_info['channel']
			self.slack_client.api_call("chat.postMessage",channel=var_channel,text=message)

		except Exception as e:
			raise

	def formatLeaderMessage(self, members):
		message = ""
		print("membersFormatLeaderMessage : " + str(members))
		global LEADERBOARD_URL
		LEADERBOARD_URL = "https://riak-chat.slack.com"
		for name, real_name, point, stars in members:
			print("name:" + name)
			print("point:" + str(point))
			print("stars:" + str(stars))
			message += "\n*{}* , {} Points {} , {} Stars".format(name, real_name, point, stars)
			print("message in loop:" + str(message))
		
		message += "\n\n<{}|View Online Leaderboard>".format(LEADERBOARD_URL)
		print("message : " + str(message))
		return message

	def parseMembers(self, members_json):
		# get member name, point and stars
		print("members_json:", str(members_json))
		print("\n")
		print("members_json.values:", members_json.values())
		print("\n")
		members = [(m["name"], m["real_name"], m["point"], m["stars"]) for m in members_json.values()]
		# sort members by point, decending
		members.sort(key=lambda s: (-s[2], -s[3]))
		print("members_sort:", members)
		return members

	def postMessage(self, message):
		print("postMessage:" + str(message))
		payload = json.dumps({
			"icon_emoji": ":ghost:",
			"username": "Karma Leaderboard",
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
		#json2 = {"296557":{"stars":0,"last_star_ts":"1969-12-31T19:00:00-0500","name":"Fajar N","l_score":0,"g_score":0,"level":{},"id":"296557"},"296558":{"stars":0,"last_star_ts":"1969-12-31T19:00:00-0500","name":"Agung N","l_score":0,"g_score":0,"level":{},"id":"296558"}}
		
		try:
			print("inside try")
			karma_db=self.connDB()
			print("conn__karma_db:", karma_db)
			get_limit_members = karma_db.coll_member.find().limit(5).sort('point', -1)
			print("got data")
			print(get_limit_members)

			temp_arrjson = []
			a = 5
			i=0
			json = [{},{},{},{},{}]
			final_arrjson = {}
			for row_member in get_limit_members:
				json[i]["stars"] = 0
				json[i]["name"] = row_member["name"]
				json[i]["real_name"] = row_member["real_name"]
				json[i]["point"] = row_member["point"]
				json[i]["slack_id"] = row_member["slack_id"]
				final_arrjson[i] = json[i]
				i=i+1
				#json += {"296557":{"stars":0,"last_star_ts":"1969-12-31T19:00:00-0500","name":row_member["name"],"l_score":row_member["score"],"g_score":row_member["score"],"level":{},"id":"296557"}}
				#print(row_member)
			print(final_arrjson)
		except Exception as e:
			raise

		# get members from json
		members = self.parseMembers(final_arrjson)
		print("members_leaderboard : {}", members)
		# generate message to send to slack
		message = self.formatLeaderMessage(members)
		print("message_leaderboard : " + str(message))
		# send message to slack
		self.postMessage(message)

	def get_info_member_by_id(self, member_id):
		member_name = ''
		try:
			karma_db=self.connDB()
			members_coll = karma_db.coll_member.find({"slack_id": member_id})
			print('\n All data from Database \n')
			for member in members_coll:
				member_name = member["real_name"]
		except Exception as e:
			print(str(e))

		return member_name

	def process_message(self, data):
		print("data:",data)
		if 'message' in data['type']:
			if 'resync_member' in data['text']:
				#for user in self.slack_client.api_call("users.list")["members"]:
				#	print(user["name"], user["id"])
				self.insert()
				self.check_point()
				self.read()

		if 'message' in data['type']:
			if 'thanks' in data['text']:
				self.update(data['text'], data)

		if 'message' in data['type']:
			print(data['text'])
			if '<@U8NEAL2M6> leaderboard' in data['text']:
				print("start to leaderboard")
				self.display_leaderboard()
