from __future__ import unicode_literals
from rtmbot.core import Plugin
from core import MongoDBConn
import re
import datetime, json, requests
import datetime
from argparse import ArgumentParser
import sys
import os
import yaml

sys.path.append(os.getcwd())

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
				print("user:", user)
				if karma_db.coll_member.find({"slack_id": user["id"]}).count() <= 0:
					#if user["is_bot"]==False:
					print('start insert data:', user)
					karma_db.coll_member.insert_one({
						"slack_id": user["id"],
						"name":user["name"],
						"real_name":user["real_name"],
						"display_name":user["profile"]["display_name"],
						"given_point":0,
						"received_point_user":0,
						"received_point_perday":10,
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
					sum_point = int(member["received_point_perday"]) + (int(diffdays)*10)
					print("sum_point:", sum_point)
					karma_db.coll_member.update_one(
						{"slack_id": member["slack_id"]},
						{
							'$set': {
								'received_point_perday': sum_point,
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
			slack_id_receiver=re.sub('[^A-Za-z0-9]+', '', split_resp[1])
			print("cls_display_name:" + slack_id_receiver)
			get_info_receiver=karma_db.coll_member.find({"slack_id":slack_id_receiver})
			for row_receiver in get_info_receiver:
				sum_received_point = int(row_receiver["received_point_user"]) + 1

			get_info_sender=karma_db.coll_member.find({"slack_id":all_info['user']})
			for row_sender in get_info_sender:
				print("slack_id_sender:", row_sender)
				minus_point = int(row_sender["given_point"]) + 1

			karma_db.coll_member.update_one(
			{"slack_id": slack_id_receiver},
			{
				'$set': {
						'received_point_user': sum_received_point
					}
			}, 
			upsert=False)
			karma_db.coll_member.update_one(
			{"slack_id": all_info['user']},
			{
				'$set': {
						'given_point': minus_point
					}
			}, 
			upsert=False)

			sum_point=self.get_sum_point(slack_id_receiver)

			send_by = self.get_info_member_by_id(all_info['user'])
			receive_by = self.get_info_member_by_id(slack_id_receiver)
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
			message += "\n*{}* , {}, Points {} , {} Stars".format(name, real_name, point, stars)
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
			get_limit_members = karma_db.coll_member.find().limit(10).sort('point', -1)
			print("got data")
			print(get_limit_members)

			temp_arrjson = []
			a = 5
			i=0
			json = [{},{},{},{},{}]
			final_arrjson = {}
			for row_member in get_limit_members:
				json[i]["stars"] = 0
				sum_point = (int(row_member["received_point_perday"]) + int(row_member["received_point_user"])) - int(row_member["given_point"])
				json[i]["name"] = row_member["name"]
				json[i]["real_name"] = row_member["real_name"]
				json[i]["point"] = sum_point
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

	def get_sum_point(self, member_id):
		sum_point = 0
		try:
			karma_db=self.connDB()
			get_member=karma_db.coll_member.find({"slack_id":member_id})
			for row in get_member:
				sum_point = (int(row["received_point_perday"]) + int(row["received_point_user"])) - int(row["given_point"])
		except Exception as e:
			print(str(e))

		return sum_point

	def handle_direct_message_to_bot(self, allinfo):
		#im_list = self.slack_client.api_call("im.list")[""]
		#print("im.list:", im_list)
		#Sending “karma” through DM to @karmabot should return the number of karma points you
		#have received and the number of karma points you have left to give
		for imlist in self.slack_client.api_call("im.list")["ims"]:
			print("channel message from : ", allinfo["channel"])
			print("ims list:", imlist)
			print("ims id : ", imlist["id"])
			if imlist["id"]==allinfo["channel"]:
				given_point=0
				received_point_user=0
				received_point_perday=0
				sum_point_perday_n_users = 0
				sum_point = 0
				try:
					karma_db=self.connDB()
					members_coll = karma_db.coll_member.find({"slack_id": imlist["user"]})
					for member in members_coll:
						given_point = member["given_point"]
						received_point_user = member["received_point_user"]
						received_point_perday = member["received_point_perday"]
						sum_point_perday_n_users = received_point_perday + received_point_user
						sum_point = (received_point_perday + received_point_user) - given_point
				except Exception as e:
					print(str(e))

				msg = "Now, your points is " + str(sum_point) + ", you have left points is " + str(given_point)
				self.slack_client.api_call("chat.postMessage",channel=imlist["id"],text=msg)
				#self.slack_client.api_call("im.replies", channel=imlist["ims"]["id"], )

	def process_message(self, data):
		#print("data:",data)
		#channels_call = self.slack_client.api_call("im.list")
		#print("im.list:", channels_call)
		parser = ArgumentParser()
		parser.add_argument(
			'-c',
			'--config',
			help='Full path to config file.',
			metavar='path'
		)
		
		args = parser.parse_args()
		config = yaml.load(open(args.config or 'rtmbot.conf', 'r'))
		print("config:", config)

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

		if 'message' in data['type']:
			if 'karma' in data['text']:
				print("direct message to bot")
				self.handle_direct_message_to_bot(data)
