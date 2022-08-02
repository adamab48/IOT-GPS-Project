#!/usr/bin/python
import RPi.GPIO as GPIO
import serial
import time
global debug
debug = 0
ser = serial.Serial('/dev/ttyS0',115200)
ser.flushInput()

power_key = 4
rec_buff = ''
APN = 'internet.ooredoo.tn'
MQTT = 'test.mosquitto.org'
Port = '1883'
message = '33.485742,11.110844'

def power_on(power_key):
    print('SIM7600X is starting:')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(power_key,GPIO.OUT)
    time.sleep(0.1)
    GPIO.output(power_key,GPIO.HIGH)
    time.sleep(2)
    GPIO.output(power_key,GPIO.LOW)
    time.sleep(2)
    ser.flushInput()
    print('SIM7600X is ready')

def power_down(power_key):
    print('SIM7600X is loging off:')
    GPIO.output(power_key,GPIO.HIGH)
    time.sleep(3)
    GPIO.output(power_key,GPIO.LOW)
    time.sleep(2)
    print('Good bye')
def send_at(command) :
	response = ''
	buffer2 = ''
	ser.write((command+  '\r\n' ).encode())
	time.sleep(1)
	if ser.inWaiting():
		time.sleep(0.01)
		buffer2 = ser.read(ser.inWaiting())
	if buffer2 != '' :
		response = buffer2.decode(errors='ignore')
	if buffer2 != '' and ('OK' in response):
		print("OK")
		if debug == 1 :
			print(response)
	else :
		if debug == 1 :
			print(response)
		buffer2 = ''
	return response
while True :
	power_on(power_key)
	try:
		ser = serial.Serial('/dev/ttyS0',115200)
		ser.flushInput()
#		send_at("AT+SMDISC")
#		send_at("AT+CNACT=0")
		send_at("AT+CFUN?")
		send_at('AT+CNACT=1,\"'+APN+'\"')
		send_at("AT+CNACT?")
		send_at('AT+SMCONF="URL\",\"'+MQTT+'\",\"'+Port+'\"')
		send_at('AT+SMCONF="KEEPTIME",60')
		time.sleep(1)
		send_at("AT+SMCONN")
		time.sleep(4)
		send_at("AT")
		print("conneting to server")
		for i in range(5) :
			print("sending message ",i)
			send_at('AT+SMPUB="miralm",'+str(len(message))+',1,1')
			time.sleep(1)
			ser.write((message).encode())
			time.sleep(4)
			send_at("AT")
#		send_at("AT+SMDISC")
#		send_at("AT+CNACT=0")
		print("Message Sent !")
	except OSError as e:
		print("[WARNING][Restablishing Connection ...]")
		ser.close()
	except KeyboardInterrupt :
		print("[INTERRUPT]--[Keyboeard Interrupt]")
		power_down(power_key)
		send_at("AT+SMDISC")
		send_at("AT+CNACT=0")
		break
	except Exception as e:
		print("[ERROR]----[Another Error]")
		print(e)
		power_down(power_key)
