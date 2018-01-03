from __future__ import unicode_literals
from rtmbot.core import Plugin
from core import MongoDBConn
import re

class APICall(Plugin, MongoDBConn):

	def catch_all(self, data):
		print("data_catch_all_xxx:")
		#print(self.xxxx())
		#print(self.outputs)
		#print(tests)
		self.process_message(data)

	def insert(self):
		try:
			karma_db=self.connDB()
			for user in self.slack_client.api_call("users.list")["members"]:
				print(karma_db.coll_member.find({"slack_id": user["id"]}).count())
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
			#get_slack_id_target=karma_db.coll_member.find(
			#		{"display_name":cls_display_name}
			#	)
			#for slack_id_target in get_slack_id_target:
			#	print(slack_id_target)
			#	get_slack_id_target=str(get_slack_id_target)
			#	print("get_slack_id_target:" + get_slack_id_target)

			karma_db.coll_member.update_one(
			{"slack_id": cls_display_name},
			{
				'$set': {
						'point': 15
					}
			}, 
			upsert=False)
		except Exception as e:
			raise

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

