# Raspberry Pi Appliance Monitor

Get notified on your phone or desktop when appliances begin or end their cycles
This device makes use of the nicely sensitive 801s vibration sensor.  It will detect faint shaking and if the shaking lasts a specified amount of time, it will assume that the appliance is running. 

This works on clothes washers and dryers, dishwashers, garage door openers, fans, furnaces, and other machines that vibrate.

You can receive tweets or PushBullet notifications when a device starts vibrating or when it stops.

## Needed parts:

* A [Raspberry Pi Zero](https://www.raspberrypi.org/products/pi-zero/)
* Any old MicroSD card (2GB is plenty)
* A USB WiFi dongle (and a MicroUSB adapter if you choose the Pi Zero)
* An [801s vibration sensor module](https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Dcomputers&field-keywords=801s+vibration+sensor)
* Any 1 amp microUSB power source (What most phones and tablets from the last 10 years use) 

# Step 1: Create the OS

> *Note*: We can skip plugging the Pi into a TV and keyboard by configuring the SD card directly from your computer. If you'd rather do this directly from the booted Pi, that works too!

1. [Download Raspbian Jessie Lite](https://www.raspberrypi.org/downloads/raspbian/) and image it onto an SD card 

2. Mount the SD card on a your computer.  There should be two partitions, a FAT32 **boot partition**, and an EXT3 **OS partition**.  On Mac or Windows, you may need to find a driver to see EXT3 partitions.

3. Add an empty file named ssh to the **boot partition**.  This enables the ssh daemon.

4. Edit these files on the **OS partition**:
  * Edit /etc/hostname and /etc/hosts to change “raspberrypi” to a unique host name
  * Edit /etc/wpa_supplicant/wpa_supplicant.conf to add your WiFi authentication:

```
    network={
	    ssid="your WiFi name (SSID)"
	    psk="your WiFi password"
    }
```

# Step 2: Create the hardware

1. Insert the microSD card into the Raspberry Pi.

2. Add the WiFi dongle to Raspberry Pi USB port.  A Raspberry Pi Zero will need a microUSB adaptor.

3. Add the 801s Vibration Sensor to Raspberry Pi GPIO pins.  The pins of my sensor line up perfectly with 5V, GND, GP14, GP15.  You can rest the pins in place initially.  When everything is working, solder or tape them into place.

4. Plug in a power source, and you’re good to go.  Within a few seconds, you should be able to connect to the Pi with: “ssh pi@*{unique host name}*” (password: `raspberry`)

# Step 3: Create the software

After you ssh to the pi, install a few essential libraries:

    sudo pip install requests tweepy

Create the program file `/home/pi/vibration.py`

```
import sys
import os
import time
import threading
import RPi.GPIO as GPIO
import tweepy
import random
import requests
import json
from ConfigParser import SafeConfigParser

def pushbullet( cfg, msg ):
	try:
		data_send = {"type": "note", "title": "VibrationBot", "body": msg}
		resp = requests.post(
			'https://api.pushbullet.com/v2/pushes',
			data=json.dumps(data_send),
			headers={'Authorization': 'Bearer '+cfg, 'Content-Type': 'application/json'})
	except (KeyboardInterrupt, SystemExit):
		raise
	except:
		pass

def tweet(msg):
	try:
		tweet = msg + " (code %08x)" % random.getrandbits(32)
		auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
		auth.set_access_token(twitter_access_token, twitter_access_token_secret)
	   	tweepy.API(auth).update_status(status=tweet) 
	except (KeyboardInterrupt, SystemExit):
		raise
	except:
		pass

def send_alert(message):
	if len(message) > 1:
		print message;
		if len(pushbullet_api_key) > 0:
			pushbullet(pushbullet_api_key, message)
		if len(pushbullet_api_key2) > 0:
			pushbullet(pushbullet_api_key2, message)
		if len(twitter_api_key) > 0:
			tweet(message)

def send_appliance_active_message():
	send_alert(start_message)
	global appliance_active
	appliance_active = True

def send_appliance_inactive_message():
	send_alert(end_message)
	global appliance_active
	appliance_active = False

def vibrated(x):
	global vibrating
	global last_vibration_time
	global start_vibration_time
	last_vibration_time = time.time()
	if not vibrating:
		start_vibration_time = last_vibration_time
		vibrating = True

def heartbeat():
	print 'HB'
	current_time = time.time()
	global vibrating
	if vibrating \
		and last_vibration_time - start_vibration_time > begin_seconds \
		and not appliance_active:
			send_appliance_active_message()
	if not vibrating \
		and appliance_active \
		and current_time - last_vibration_time > end_seconds:
			send_appliance_inactive_message()
	vibrating = current_time - last_vibration_time < 2
	threading.Timer(1,heartbeat).start()

if len(sys.argv) == 1:
	print "No config file specified"
	sys.exit()

vibrating = False
appliance_active = False
last_vibration_time = time.time()
start_vibration_time = last_vibration_time

config = SafeConfigParser()
config.read(sys.argv[1])
sensor_pin = config.getint('main', 'SENSOR_PIN')
begin_seconds = config.getint('main', 'SECONDS_TO_START')
end_seconds = config.getint('main', 'SECONDS_TO_END')
pushbullet_api_key = config.get('pushbullet', 'API_KEY')
pushbullet_api_key2 = config.get('pushbullet', 'API_KEY2')
start_message = config.get('main', 'START_MESSAGE')
end_message = config.get('main', 'END_MESSAGE')
twitter_api_key = config.get('twitter', 'api_key')
twitter_api_secret = config.get('twitter', 'api_secret')
twitter_access_token = config.get('twitter', 'access_token')
twitter_access_token_secret = config.get('twitter', 'access_token_secret')
send_alert( config.get('main', 'BOOT_MESSAGE') )

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor_pin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(sensor_pin,GPIO.RISING)
GPIO.add_event_callback(sensor_pin,vibrated)

threading.Timer(1,heartbeat).start()
```


Create the settings file `/home/pi/vibration_settings.ini`

* Create a PushBullet API key here:  https://www.pushbullet.com/#settings/account
* Create Twitter API keys here (Steps 1-4): http://nodotcom.org/python-twitter-tutorial.html

```
[main]
sensor_pin = 14
seconds_to_start = 6
seconds_to_end = 3
start_message = Dryer has started
end_message = Dryer has finished
boot_message =

[pushbullet]
api_key = 
api_key2 = 

[twitter]
api_key = 
api_secret =
access_token =
access_token_secret =
```



Edit `/etc/rc.local` To make the program run at boot.

Add before the `exit` line:

    python /home/pi/vibration.py /home/pi/vibration_settings.ini &

You’re done!  Reboot and test it out.

If you’ve soldered the sensor pins, you can bend the sensor to be flush with the Pi.


