#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO

import serial
import time

ser = serial.Serial('/dev/ttyS0',115200)
ser.flushInput()

power_key = 4
rec_buff2 = ''
time_count = 0


def send_at_input() :
    buffer = ''
    command_input = input('Please input the AT command:')
    ser.write((command_input+  '\r\n' ).encode())
    time.sleep(0.1)
    if ser.inWaiting():
        time.sleep(0.01)
        buffer = ser.read(ser.inWaiting())
    if buffer != '':
        print(buffer.decode())
        buffer = ''
def send_at(command) :
    response = ''
    buffer2 = ''
    ser.write((command+  '\r\n' ).encode())
    time.sleep(0.1)
    if ser.inWaiting():
        time.sleep(0.01)
        buffer2 = ser.read(ser.inWaiting())
        response = buffer2.decode()
    if buffer2 != '' and ('+CGNSINF: ' in response):
        GPSDATA = str(response)
        new  = GPSDATA[GPSDATA.index("CGNSINF: ")+len("CGNSINF: "):]
        date = new[4:12]
        year = date[:4]
        month = date[4:6]
        day = date[6:8]
        timing = new[12:18]
        hours = timing[:2]
        minutes = timing[2:4]
        seconds = timing[4:6]
        print("Coordinates : [",new[23:42],"][TIME][",year,"-",month,"-",day,"/",hours,"-",minutes,"-",seconds,"]")
        buffer2 = ''
    else :
        print("[INFO]---[No Coordinates Recieved !]")
        buffer2 = ''

def power_on(power_key):
	print('GPS Module is starting:')
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(power_key,GPIO.OUT)
	time.sleep(0.1)
	GPIO.output(power_key,GPIO.HIGH)
	time.sleep(2)
	GPIO.output(power_key,GPIO.LOW)
	time.sleep(2)
	ser.flushInput()
	print('GPS Module is ready')


def power_down(power_key):
	print('GPS Module is logging off:')
	GPIO.output(power_key,GPIO.HIGH)
	time.sleep(3)
	GPIO.output(power_key,GPIO.LOW)
	time.sleep(2)
	print('Good bye')
def main() :
    send_at("AT+CGNSPWR=1")
    time.sleep(2)
    for i in range(10) :
        print("[INFO]----[READING NUMBER ",i,"]")
        send_at("AT+CGNSINF")
        time.sleep(1)



power_on(power_key)
time.sleep(2)
while True :
    try :
        ser = serial.Serial('/dev/ttyS0',115200)
        ser.flushInput()
        main()
    except OSError as e:
        print("[WARNING][Restablishing Connection ...]")
        ser.close()
    except KeyboardInterrupt :
        print("[INTERRUPT]--[Keyboeard Interrupt]")
        power_down(power_key)
        break
    except Exception as e:
        print("[ERROR]----[Another Error]")
        print(e)
        power_down(power_key)
