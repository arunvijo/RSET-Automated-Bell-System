import socket
import json
import threading
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD) #setting board configaration
amp_in = 35
GPIO.setup(amp_in, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

port = 8000

"""thread to check amplifier 
"""
def amp_controller(Client_Socket):
	amp_status = {'status':' '} #json object to send amplifier status to pi's
	while True:
		if(check_amp_input):
			amp_status['status'] = 'on'
		else:
			amp_status['status'] = 'off'
		Client_Socket.send(json.dumps(amp_status))
		time.sleep(10)

def check_amp_input():
	if(GPIO.input(amp_in)):
		return True
	else:
		return False

if __name__ == "__main__":

	server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creating server socket

	try:            

	    server_socket.bind((socket.gethostname(),port))

	except socket.error as msg:

	    print 'socket not binding ' ,msg[0],'\n',msg[1]

	print 'socket binded to port {0} '.format(socket.gethostname())

	server_socket.listen(5)
	
	while True:

		(Client_Socket,address) = server_socket.accept()  #blocking call
		print "accepted ",address
		t = threading.Thread(target = amp_controller, args = (Client_Socket,)) #starting thread for each client
		t.start()
