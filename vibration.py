import sys
import time
import threading
import RPi.GPIO as GPIO
import requests
import json
from time import localtime, strftime
import urllib

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


def iftt(msg):
    try:
        iftt_url = "https://maker.ifttt.com/trigger/{}/with/key/{}".format(iftt_maker_channel_event,
                                                                           iftt_maker_channel_key)
        report = {"value1" : msg}
        resp = requests.post(iftt_url, data=report)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        pass

def slack_webhook(msg):
    try:
        payload = urllib.urlencode({'payload': '{"text": "' + msg+ '"}'})
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        response = requests.request("POST", slack_webhook , data=payload, headers=headers)

    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        pass

def tweet(msg):
    try:
        # Twitter is the only API that NEEDS something like a timestamp,
        # since it will reject identical tweets.
        tweet = msg + ' ' + strftime("%Y-%m-%d %H:%M:%S", localtime())
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
        slack = msg + ' ' + strftime("%Y-%m-%d %H:%M:%S", localtime())
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
        if len (slack_webhook) > 0:
            slack_webhook(message)
        if len(iftt_maker_channel_key) > 0:
            iftt(message)

def sensor_switch(x):
    global last_signal_on_time
    global sensor_on
    sensor_on = GPIO.input(sensor_pin)
    if (sensor_on):
        print 'Sensor ON'
        last_signal_on_time = time.time()
    else:
        print 'Sensor OFF'
        last_signal_off_time = time.time()


def heartbeat():
    global appliance_active
    global last_quiet_time
    global sensor_on
    print 'HB'

    current_time = time.time()

    # Test if there's been any quiet lately
    if ( not sensor_on and current_time - last_signal_on_time > 1):
        last_quiet_time = current_time

    # Test for appliance off
    if (appliance_active):
        # If there hasn't been an on signal for a while
        if (current_time - last_signal_on_time > end_seconds):
            appliance_active = False
            send_alert(end_message)

    # Test for appliance on
    else:
        # If there hasn't been a quiet period for a while
        if (current_time - last_quiet_time > begin_seconds):
            appliance_active = True
            send_alert(start_message)

    threading.Timer(1, heartbeat).start()


if len(sys.argv) == 1:
    print "No config file specified"
    sys.exit()

appliance_active = False
sensor_on = False
last_signal_on_time = time.time()
last_signal_off_time = time.time()
last_quiet_time = time.time()

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
slack_webhook = config.get('slack','webhook_url')
iftt_maker_channel_event = config.get('iftt','maker_channel_event')
iftt_maker_channel_key = config.get('iftt','maker_channel_key')

send_alert(config.get('main', 'BOOT_MESSAGE'))

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(sensor_pin, GPIO.BOTH, callback=sensor_switch)

print 'Running config file {} monitoring GPIO pin {}'\
      .format(sys.argv[1], str(sensor_pin))
threading.Timer(1, heartbeat).start()
