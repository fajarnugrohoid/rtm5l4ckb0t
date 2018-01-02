from __future__ import unicode_literals
from rtmbot.core import Plugin
from core import MongoDBConn

class APICall(Plugin, MongoDBConn):
	def catch_all(self, data):
		print("data_catch_all_xxx:")
		self.insert()
		self.read()
		#self.process_message(data)

	def insert(self):
		try:
			employeeId = input('Enter Employee id :')
			employeeName = input('Enter Name :')
			employeeAge = input('Enter age :')
			employeeCountry = input('Enter Country :')
			karma_db=MongoDBConn.connDB(self)
			karma_db.coll_member.insert_one({
				"id": employeeId,
				"name":employeeName,
				"age":employeeAge,
				"country":employeeCountry
			})
			print('\nInserted data successfully\n')
		except Exception as e:
			print(str(e))

	def read(self):
		try:
			karma_db=MongoDBConn.connDB(self)
			empCol = karma_db.coll_member.find()
			print('\n All data from EmployeeData Database \n')
			for emp in empCol:
				print(emp)
		except Exception as e:
			print(str(e))

	def process_message(self, data):
		#if 'sync_member' in data['text']:
		print('tes1')
		print('tes2')
		print('tes3')
		for user in self.slack_client.api_call("users.list")["members"]:
			print(user["name"], user["id"])