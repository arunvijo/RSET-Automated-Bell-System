#This program will switch OFF the Amplifier 

# add pins for ringing bell
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #setting board configaration
#bell_out = 40 #pin 37 for relay output
amp_out = 40 #pin 40 for amplifier output
#GPIO.setup(bell_out, GPIO.OUT)
GPIO.setup(amp_out, GPIO.OUT)
GPIO.output(amp_out,False) #setting amp relay out to low permanently (OFF)

if __name__ == '__main__':
	# Turn of Amplifier
	GPIO.output(amp_out,False) #setting amp relay out to low - switch OFF
