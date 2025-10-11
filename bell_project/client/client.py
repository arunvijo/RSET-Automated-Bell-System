from crontab import CronTab
import socket
import json
import time
import threading
import os

host="192.168.0.154"
#host = socket.gethostname()
port=8888
usr = "pi" #change user name to client name for crontab

""" this function edits the cron file of the pi 
    accepts list of bell rings (times)"""
def editcron(msg):

	cron = CronTab(usr)
	cron.remove_all()

	#Read the profile name
	pname = str(msg['name'])

	times = [ str(msg['b'+str(i)]) for i in range(1,29)]
	print times

	for i in xrange(len(times)):
			Createjob(msg,times[i],cron,i+1,pname)
	cron.write()

def Createjob(d,time,cron,n,pname):

	if time == 'None':	#Ignore profile time of no value is given
		#print "Invalid time value at ", n
		return
	hour = int(time[0:2])
	minute = int(time[3:5])
	days = [ d['b'+str(n)+'_d'+str(i)] for i in xrange(7)]

	if d['a'+str(n)] == 0 :
		cmd = '(cd /home/pi/bell/bell_project/client; python ring.py ' + str(d['t'+str(n)]+')')
	else:
		cmd = '(cd /home/pi/bell/bell_project/client; python anthem.py '+str(d['t'+str(n)]+')')

	job = cron.new(command = cmd,comment = pname)

	daylist = []
	for i in xrange(len(days)):
		if days[i] == 1:
			#job.dow.on(job.day, job.day.on(i))
			daylist = daylist + [i]
	job.dow.parts = daylist

	job.hour.on(hour)
	job.minute.on(minute)
	job.enable()
	#cron.write()
	print "job added ",job.render()

def recv_msg(sock):
	msg = ''
	while True:
		data = sock.recv(4096)
		msg = msg + data
		if(msg):
			if msg[len(msg)-1] == '?':
				return msg.rstrip('?')

if __name__ == '__main__':
	
	connect = False
	client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	while(connect == False):
		try:
			client_socket.connect((host,port))
			connect=True
		except socket.error:
			print("waiting for server to respond........")
			time.sleep(5)

	while(True):
		msg=recv_msg(client_socket)
		if(msg):
			msg=json.loads(msg)
			print msg
			t = threading.Thread(target = editcron, args = (msg,))
			t.start()
