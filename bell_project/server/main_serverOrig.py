import socket
import json
import threading
import time
import sqlite3
import datetime

import logging as log
log.basicConfig(
		format='%(asctime)s %(levelname)s:%(name)s:%(message)s',
		datefmt='%d/%m/%Y %I:%M:%S %p',
		filename= '/var/log/bell.log',
		level=log.DEBUG
		)

def debug(message):
	print (message)
	log.debug(message)

port = 8888
db_url = "/home/bell/db.sqlite3" #database URL

""" Reading time from sqllite3 database 
function returns list of times for bell rings of current profile"""

def get_profileName(block_ip):

	if block_ip == '192.168.0.155':
		block = 'web_main_blk'
	elif block_ip == '192.168.0.156':
		block = 'web_pg'
	elif block_ip == '192.168.0.157':
 		block = 'web_ke'
	else:
		block  = 'web_main_blk'
	conn = sqlite3.connect(db_url)
	c = conn.cursor()   
	c.execute("select name from "+block.rstrip('_blk')+"_current")
	s=c.fetchone() #current profile read

	return (str(s[0]))

def get_time(block_ip):

	d = {}

	if block_ip == '192.168.0.155':
		block = 'web_main_blk'
 
	elif block_ip == '192.168.0.156':
		block = 'web_pg'

	elif block_ip == '192.168.0.157':
 		block = 'web_ke'
    
	else:
		block  = 'web_main_blk'

	#print 'reading db'
	conn = sqlite3.connect(db_url)
	c = conn.cursor()   
	c.execute("select name from "+block.rstrip('_blk')+"_current")
	s=c.fetchone() #current profile read
#	print str(s[0])
#        debug (str(s[0]))
	c.execute("select * from web_blk where name = '"+str(s[0])+"'") 
	l = c.fetchall()
	l = list(l[0])
	fieldnames=[f[0] for f in c.description]
	for i in range(len(l)):                  
            d[fieldnames[i]] = l[i]           
    
	return d

""" Sends the list of times to each of the client_socket accepts the socket 
this function is going to be the target function for the thread"""

def send_list(Client_Socket):

	debug ("Thread started")
	old_profile = {}
	
	while (True):
		#debug ( Client_Socket.getpeername()[0])
		block_IP = Client_Socket.getpeername()[0]
		times = get_time(Client_Socket.getpeername()[0])
		#DBG: Biju
		#print "Data fetched: ", times
		#debug (block_IP + ": " + str(times))

		if (times != old_profile):
			old_profile=times
			Client_Socket.send((json.dumps(times)+'?').encode()) #sending times in JSON format
			ShowTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			#block_IP = Client_Socket.getpeername()[0]
			profileName = get_profileName(Client_Socket.getpeername()[0])
			#print ShowTime, "Data send to: ", block_IP, " Profile: ", profileName
			#Biju: DBG
			#debug ( "".join([ShowTime, " Data send to: ", block_IP, " Profile: ", profileName]))
			debug (ShowTime + " Data send to: " + block_IP + " Profile: " + profileName)
		time.sleep(60)

if __name__ == "__main__":

	server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creating server socket

	try:            

	    server_socket.bind((socket.gethostname(),port)) #change

	except socket.error as msg:

	    debug ('socket not binding '+ str(msg[0]) + '\n'+ msg[1])

	#print 'socket binded to port {0} '.format(socket.gethostname())
	debug ('socket binded to port ' + str(port))

	server_socket.listen(5)
	
	while True:
		(Client_Socket,address) = server_socket.accept()
		print(("Accepted ", address))
		#debug (address)
		t = threading.Thread(target = send_list, args = (Client_Socket,)) #starting thread for each client
		t.start()   

