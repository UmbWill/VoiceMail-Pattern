
#/////////////////////////////////////#
#		VoiceMail pattern 			  #
#/////////////////////////////////////#

# ************* PRODUCER **********#

# VoiceMail pattern example
# Producer-Customer communication via socket

import os
import socket
import sqlite3


CLNTSOCKHOST = 'localhost'
CLNTSOCKPORT = 65321

class Producer():

	def __init__(self, map_customers_host, map_customers_port):

		self._create_phonelist(map_customers_host, map_customers_port)
		self.prod_name = "ProducerName"


	def _create_phonelist(self, map_customers_host, map_customers_port):
		self.phonelist = {}
		if len(map_customers_host) != len(map_customers_port):
			return 
		else:
			for cust in map_customers_host:
				try:
					self.phonelist[cust] = (map_customers_host[cust],map_customers_port[cust])
				except KeyError as err:
					print("Customer host and port not found.")
					continue
  
 
	def main_producer(self):

		# call customer
		if(self.socketping(self.phonelist["FooFoo"])):
		# ok, customer in the house
			if self.sockesendmsg(self.phonelist["FooFoo"], "terminate"):
				print("Thank You to buy our goods.")
			else:
				print("Something wrong.")	 
		else:
			self.leave_msg_in_vm("Hi VM!")

	@staticmethod
	def socketping(phone_number):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sck:
			try:
				sck.settimeout(5)
				print(phone_number)
				sck.connect(phone_number)
			except socket.error as err:
				print("error in socket communication")
				return False
			except socket.timeout as err:
				print("socket timeout error")
				return False 	
		return True 

	@staticmethod
	def sockesendmsg(phone_number, msg):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sck:
			try:
				sck.settimeout(5)
				sck.connect(phone_number)
				sck.sendall(msg.encode('utf-8'))
				data = b""
				while True:
					buf = sck.recv(1024)
					if not buf:
						break
					data += buf
					print("Receive ",data)	 
			except socket.error as err:
				print("error in socket communication")
				return False
			except socket.timeout as err:
				print("socket timeout error")
				return False 	
		return True    

	def leave_msg_in_vm(self, msg):
		# leave a message in VoiceMail   
		# for this example I will use a fixed position
		database_path = "S:\Script\VoiceMail"
		database_name = "DBvoicemail.db"
		
		# check if path exists, not create a new directory.
		# Customer is the owner of the VoiceMail, we can't decide where place it! 
		# I will not enter in your house a move your furniture
		if os.path.exists(database_path):
			sqlconn = sqlite3.connect(os.path.join(database_path,database_name))
			
			sql = sqlconn.cursor()
			#create table in voicemail db if not present
			sql.execute("CREATE TABLE  IF NOT EXISTS voicemail_led( \
			id INTEGER PRIMARY KEY,\
			led_flag INTEGER NOT NULL UNIQUE \
			)")

			sql.execute("CREATE TABLE  IF NOT EXISTS voicemail_messages(\
			id INTEGER PRIMARY KEY,\
			Producer TEXT NOT NULL,\
			Message TEXT NOT NULL)\
			")

			#insert flag value and messages
			sql.execute(" INSERT OR REPLACE INTO voicemail_led (id, led_flag) VALUES (0,1)")
			sql.execute(" INSERT OR REPLACE INTO voicemail_messages (Producer, Message) \
			VALUES (\""+self.prod_name +"\",\""+msg+"\")")

			sqlconn.commit()
			sqlconn.close() 	 


if __name__ == "__main__":
	map_customers_host = {}
	map_customers_port = {}
	map_customers_host["FooFoo"] = CLNTSOCKHOST
	map_customers_port["FooFoo"] = CLNTSOCKPORT
	pr = Producer(map_customers_host, map_customers_port)
	pr.main_producer()