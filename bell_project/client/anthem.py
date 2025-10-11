#this program will ring the bell, set a pin high for few seconds 
# add pins for ringing bell

import time
import RPi.GPIO as GPIO
import os
import sys
import datetime

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #setting board configaration
#relay_out = 37 #pin 37 for relay output
amp_out = 40 #pin 40 for amplifier output
#GPIO.setup(relay_out, GPIO.OUT)
GPIO.setup(amp_out, GPIO.OUT)
#GPIO.output(relay_out,True) #setting relay out to high permanently
GPIO.output(amp_out,True) #setting amp relay out to high permanently

if __name__ == '__main__':
	now = datetime.datetime.now()
	#Do not ring if on Sunday
	if (now.isoweekday() == 7) :
		sys.exit(0)
        #Uncomment one of the following
	#Do not play if on Second Saturday
	#if (now.isoweekday() == 6 and now.day > 7 and now.day < 15) :
	#Do not play if on First or Second Saturday
	if (now.isoweekday() == 6 and now.day < 15) :
		sys.exit(0)
	# Turn on Amplifier
	GPIO.output(amp_out,False) #setting amp relay out to low - amp ON
	f = open('anth.txt','r+')
	i = f.read()
	os.system("python ring.py "+str(sys.argv[1]))
	time.sleep(2)
	if i == '1':
		os.system('omxplayer --vol 600 --no-osd RajagiriAnthemEnglish.mp3')
		i = '0'
	else:
		os.system('omxplayer --vol 600 --no-osd RajagiriAnthemMalayalam.mp3')
		i = '1'
	f.seek(0)
	f.write(i)
	f.close()
	# Turn off Amplifier
	GPIO.output(amp_out,True) #setting amp relay out to high - amp OFF
