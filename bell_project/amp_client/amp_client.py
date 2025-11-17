import socket
import json
import time
import threading
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD) #setting board configaration
amp_out = 40
GPIO.setup(amp_out, GPIO.OUT)
GPIO.output(amp_out,True) #setting relay out to high permanently



host=socket.gethostname() #change this to server IP 
port=8000
current_status = 'off'

def amp_controller(status):
	if status == 'on' and current_status == 'off':
		GPIO.output(amp_out,False)
		print "amp_on"
	if status == 'off' and current_status == 'on':
		GPIO.output(amp_out,True)
		print "amp_off"



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

		msg=client_socket.recv(4096)
		if(msg):
			msg=json.loads(msg)
			print msg
			amp_controller(str(msg['status']))
			