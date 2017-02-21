import sys
import time
import threading
import RPi.GPIO as GPIO
import requests
import json
from time import gmtime, strftime

from ConfigParser import SafeConfigParser
from tweepy import OAuthHandler as TweetHandler
from slackclient import SlackClient


def pushbullet(cfg, msg):
    try:
        data_send = {"type": "note", "title": "VibrationBot", "body": msg}
        requests.post(
            'https://api.pushbullet.com/v2/pushes',
            data=json.dumps(data_send),
            headers={'Authorization': 'Bearer ' + cfg,
                     'Content-Type': 'application/json'})
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        pass


def tweet(msg):
    try:
        tweet = msg + ' ' + strftime("%Y-%m-%d %H:%M:%S", gmtime())
        auth = TweetHandler(twitter_api_key, twitter_api_secret)
        auth.set_access_token(twitter_access_token,
                              twitter_access_token_secret)
        tweepy.API(auth).update_status(status=tweet)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        pass


def slack(msg):
    try:
        slack = msg + ' ' + strftime("%Y-%m-%d %H:%M:%S", gmtime())
        sc = SlackClient(slack_api_token)
        sc.api_call(
            'chat.postMessage', channel='#random', text=slack)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        pass


def send_alert(message):
    if len(message) > 1:
        print message
        if len(pushbullet_api_key) > 0:
            pushbullet(pushbullet_api_key, message)
        if len(pushbullet_api_key2) > 0:
            pushbullet(pushbullet_api_key2, message)
        if len(twitter_api_key) > 0:
            tweet(message)
        if len(slack_api_token) > 0:
            slack(message)


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
    print 'Vibrated'
    last_vibration_time = time.time()
    if not vibrating:
        start_vibration_time = last_vibration_time
        vibrating = True


def heartbeat():
    print 'HB'
    current_time = time.time()
    global vibrating
    delta_vibration = last_vibration_time - start_vibration_time
    if (vibrating and delta_vibration > begin_seconds
            and not appliance_active):
        send_appliance_active_message()
    if (not vibrating and appliance_active
            and current_time - last_vibration_time > end_seconds):
        send_appliance_inactive_message()
    vibrating = current_time - last_vibration_time < 2
    threading.Timer(1, heartbeat).start()


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
slack_api_token = config.get('slack', 'api_token')
send_alert(config.get('main', 'BOOT_MESSAGE'))

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(sensor_pin, GPIO.RISING)
GPIO.add_event_callback(sensor_pin, vibrated)

print 'Running config file {} monitoring GPIO pin {}'\
      .format(sys.argv[1], str(sensor_pin))
threading.Timer(1, heartbeat).start()
