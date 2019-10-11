#/////////////////////////////////////#
#		VoiceMail pattern 			  #
#/////////////////////////////////////#

# ************* CUSTOMER **********#

# VoiceMail pattern example
# Producer-Customer communication via socket

import os
import socket
import select
import sqlite3
import queue
from multiprocessing import Manager, Process

SERVSOCKHOST = "localhost"
SERVSOCKPORT = 65321

class Customer():
 
	def __init__(self):
		self.mp = Manager()
		self.in_phone_queue = self.mp.Queue()
		self.database_path = "S:\Script\VoiceMail"
		self.database_name = "DBvoicemail.db"
	 
	def main_customer(self):
		multip = Process(target = self.server_sck_phone, args=(self.in_phone_queue,))
		multip.start()
		
		multivm = Process(target = self.chk_msg_in_voicemail, args=(self.database_path, self.database_name))
		multivm.start()
		
		while True:
			if not self.in_phone_queue.empty():
				msg = self.in_phone_queue.get()
				print("Received data: ", msg)
				if msg == b"terminate":
					print("HP = 0. Customer scarred run away!")
					multip.terminate()
					break
				
	@staticmethod 
	def chk_msg_in_voicemail(database_path, database_name):
		
		try:
		    # check if path exists
			if os.path.exists(database_path):
				sqlconn = sqlite3.connect(os.path.join(database_path, database_name))
				
				sql = sqlconn.cursor()
				
				sql.execute(" \
					SELECT led_flag FROM voicemail_led \
				")
				VM_flag = sql.fetchall()
				for row in VM_flag:
					print("VM flag: ", row[0])
					
					if row[0] == 1:
						sql.execute(" INSERT OR REPLACE INTO\
						voicemail_led (id, led_flag) \
						VALUES (0,0)")
						
						sql.execute(" \
						SELECT * FROM voicemail_messages \
						")
						VM_msgs = sql.fetchall()
						for row in VM_msgs:
							print("VM Producer and msgs: ", row)
						
						sql.execute(" \
						DROP TABLE IF EXISTS voicemail_messages \
						")
				sqlconn.commit()
				sqlconn.close()
			else:
			# Customer is the owner of the VoiceMail, he can decide where place it! 
				try:
					os.makedirs(database_path)
				except OSError as err:
					print("can't create voicemail directory. " , err)	
		except sqlite3.Error as err:
			print("error ", err)
		
	@staticmethod 
	def server_sck_phone(in_phone_queue):
		
		try:
			sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sck.setsockopt(socket.SOL_SOCKET , socket.SO_REUSEADDR, 1)
			sck.setblocking(0)
			sck.bind((SERVSOCKHOST,SERVSOCKPORT))
			sck.listen(1)

			inputs = [sck]
			outputs = []
			msg_queue = {}
			data = b""
			while inputs:
				readable, writeable, exceptional = select.select(inputs, outputs, msg_queue)
				for s in readable:
					if s is sck:
						conn, add = s.accept()
						conn.setblocking(0)
						inputs.append(conn)
						msg_queue[conn] = queue.Queue()
					else:
						data = s.recv(1024)
						if data:
							msg_queue[s].put(data)
							print("data ", data)
							in_phone_queue.put(data)
							if s not in outputs:
								outputs.append(s)
						else:
							if s in outputs:
								outputs.remove(s)
							inputs.remove(s)
							s.shutdown(socket.SHUT_WR)
							s.close()
							del msg_queue[s]
		
				for s in writeable:
					try:
						next_msg = msg_queue[s].get_nowait()
						print("next_msg ", next_msg)
					except queue.Empty:
						outputs.remove(s)
					else:				
						s.send(b"Goods in store!")
						s.shutdown(socket.SHUT_WR)
		
				for s in exceptional:
					inputs.remove(s)
					if s in outputs:
						outputs.remove(s)
					s.shutdown(socket.SHUT_WR)	
					s.close()
					del msg_queue[s]
		except:
			pass
		
if __name__ == "__main__":
	cs = Customer()
	cs.main_customer()