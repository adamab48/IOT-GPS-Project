#!/usr/bin/python
import RPi.GPIO as GPIO
import serial
import time
global debug
debug = 1
ser = serial.Serial('/dev/ttyS0',115200)
ser.flushInput()
global message
message = ""
power_key = 4
rec_buff = ''
APN = 'internet.ooredoo.tn'
MQTT = 'test.mosquitto.org'
Port = '1883'

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
		send_at("AT+SMDISC")
		send_at("AT+CNACT=0")
		send_at("AT+CGNSPWR=1")
		if "ERROR" in send_at("AT+CFUN?") :
			print("retrying")
			continue
		if "ERROR" in send_at('AT+CNACT=1,\"'+APN+'\"') :
			print("retrying")
			continue
		time.sleep(1)
		send_at("AT+CNACT?")
		send_at('AT+SMCONF="URL\",\"'+MQTT+'\",\"'+Port+'\"')
		send_at('AT+SMCONF="KEEPTIME",60')
		time.sleep(1)
		if "ERROR" in send_at("AT+SMCONN") :
			print("retrying")
			continue
		time.sleep(4)
		send_at("AT")
		print("conneting to server")
		for i in range(5) :
			coordinates = send_at("AT+CGNSINF")
			if "CGNSINF: " in coordinates :
				GPSDATA = str(coordinates)
				new  = GPSDATA[GPSDATA.index("CGNSINF: ")+len("CGNSINF: "):]
				date = new[4:12]
				year = date[:4]
				month = date[4:6]
				day = date[6:8]
				timing = new[12:18]
				hours = timing[:2]
				minutes = timing[2:4]
				seconds = timing[4:6]
				message = new[23:42]+seconds
				print("Coordinates : [",new[23:42],"][TIME][",year,"-",month,"-",day,"/",hours,"-",minutes,"-",seconds,"]")
				time.sleep(2)
				print("getting reading",i)
				print("sending message ",i)
				send_at('AT+SMPUB="miralm",'+str(len(message))+',1,1')
				time.sleep(1)
				ser.write((message).encode())
				time.sleep(4)
				send_at("AT")
		send_at("AT+SMDISC")
		send_at("AT+CNACT=0")
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



