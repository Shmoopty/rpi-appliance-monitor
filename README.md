# Raspberry Pi Appliance Monitor

_Get **Tweets**, **Slack** messages, **Pushover** notifications, **PushBullet** notifications, or **IFTTT triggers** when appliances begin or end their cycles_

**Raspberry Pi Appliance Monitor** just sticks onto an appliance, so no damage is done, no warranties are voided.  (That makes it Landlord Safe!)

Raspberry Pi Appliance Monitor makes use of the nicely sensitive 801s vibration sensor.  It will detect faint shaking and if the shaking lasts a specified amount of time, it will assume that the appliance is running. 

![On Phone](https://cloud.githubusercontent.com/assets/1101856/21469770/5d91e94e-ca2b-11e6-8c9c-d28eb902aefb.jpg "On Phone")

This works on clothes washers and dryers, dishwashers, garage door openers, fans, furnaces, and other machines that vibrate.

## Needed parts:

* A [Raspberry Pi Zero](https://www.raspberrypi.org/products/pi-zero/).  Or any Raspberry Pi.  (In the U.S., see if there's a Micro Center nearby.  They'll sell you a single Zero at cost.)
* Any old MicroSD card.  2GB is plenty.
* WiFi.  If you have a Raspberry Pi Zero W or Pi 3, you already have WiFi.  A Raspberry Pi A/B/2 will need a USB WiFi dongle.  My classic Pi Zero needs a dongle **and** a MicroUSB adapter.
* An [801s vibration sensor module](https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Dcomputers&field-keywords=801s+vibration+sensor)   You'll want one with a **voltage** (+V), **ground** (-V), and **digital signal pin**.  Mine has an extra analog sensor pin that I'm effectively ignoring.  Pi doesn't do analog easily.
* Any 1 amp microUSB power source (What most phones and tablets from the last 10 years use) 

![Parts](https://cloud.githubusercontent.com/assets/1101856/21469691/1141fa38-ca27-11e6-8c7e-c1d389709a06.jpg "Parts")

# Step 1: Create the OS

> *Note*: We can skip plugging the Pi into a TV and keyboard by configuring the SD card directly from your computer. If you'd rather do this directly from the booted Pi, that works too!

1. [Download Raspbian Stretch Lite](https://www.raspberrypi.org/downloads/raspbian/) and image it onto an SD card 

2. Mount the SD card on your computer.  There should be two partitions, a FAT32 **boot partition**, and an EXT3 **OS partition**.  On [Mac](https://osxfuse.github.io/) or [Windows](http://www.chrysocome.net/explore2fs), you may need to find a driver to see EXT3 partitions (see links).

3. Add an empty file named `ssh` to the **boot partition**.  This enables the ssh daemon when it boots.

4. Edit these files on the **OS partition**:
  * Edit `/etc/hostname` and `/etc/hosts` to change “raspberrypi” to a **unique host name**, like `dryerpi`.
  * Edit `/etc/wpa_supplicant/wpa_supplicant.conf` to add your WiFi authentication:

```
    network={
	    ssid="your WiFi name (SSID)"
	    psk="your WiFi password"
    }
```

Your OS should now be ready to boot and automatically jump on your home network!

# Step 2: Create the hardware

1. Insert the microSD card into the Raspberry Pi.

2. Add the WiFi dongle to Raspberry Pi USB port.  A Raspberry Pi Zero will need a [microUSB adaptor](https://www.amazon.com/gp/product/B015GZOHKW/).

3. Add the 801s Vibration Sensor to [Raspberry Pi GPIO pins](https://pinout.xyz/).  The pins of my sensor line up perfectly with 5V, GND, and GP14.  I'll be ignoring the analog pin that found its way into GP15.  You can rest the pins in place initially.  When everything is working, solder or tape them into place.
> Multiple sensor expert mode: Connect additional vibration modules to the same (or any) 5V and GND pins, but a different sensor GPIO pin. You'll want to use a very flexible or long cable, so one vibrating sensor doesn't shake everything.

4. Plug in a power source, and you’re good to go.  Within a few seconds, you should be able to connect to the Pi with:

    `ssh pi@{unique host name}`
    
(password: `raspberry`)

![Sensor inserted](https://cloud.githubusercontent.com/assets/1101856/21469689/113ee280-ca27-11e6-979f-a2d7c1aeb3bb.jpg "Sensor inserted")


# Step 3: Create the software

After you ssh to the pi, install a few essential libraries:

    $ sudo apt-get install python-pip
    $ sudo pip install requests tweepy slackclient
    
Set the timezone to make sure timestamps are correct

    $ sudo raspi-config
    [Internationalisation Options]
    [Change Timezone]

Create the program file [`/home/pi/vibration.py`](https://raw.githubusercontent.com/Shmoopty/rpi-appliance-monitor/master/vibration.py) (Click to view)

Create the settings file [`/home/pi/vibration_settings.ini`](https://raw.githubusercontent.com/Shmoopty/rpi-appliance-monitor/master/vibration_settings.ini).  This file specifies what sensor pin to monitor, what messages you want, and what services to send the message to. 

> Multiple sensor expert mode: Create additional settings files with their own timings, messages, and unique sensor pins.  One for each sensor.

* If you want PushBullet notifications, [create a PushBullet Access Token key here](https://www.pushbullet.com/#settings/account)
* If you want Twitter notifications, [create Twitter API keys here](http://nodotcom.org/python-twitter-tutorial.html) (Steps 1-4): 
* If you want Slack notifications, [create a bot user](https://api.slack.com/bot-users) **or** [create a Slack webhook](https://api.slack.com/incoming-webhooks)
* If you want an IFTTT trigger, create a new trigger with the Maker channel and note the channel and key.

Edit `/etc/rc.local` to make the program run when the device boots up.

Add before the `exit` line:

    python /home/pi/vibration.py /home/pi/vibration_settings.ini &

> Multiple sensor expert mode: Add and additional line for each additional sensor. One for each of the settings files you created.

You’re done!  Reboot and test it out.

Some mounting tape or Sugru will let you stick the device somewhere discrete on your appliance.

If you’ve soldered the sensor pins, you can bend the sensor to be flush with the Pi.

![Completed device](https://cloud.githubusercontent.com/assets/1101856/21469692/1143d1fa-ca27-11e6-9986-e12b9c23e189.jpg "Completed device")

# Optional tuning that you can probably skip over

### If your monitor is too sensitive and triggers when someone is just walking around the house:

Look for a potentiometer that looks like a screw head on your 801s sensor.  Give it a little twist _(probably in the "unscrew" direction)_ to make it less touchy.  If that doesn't help, read on...

### If your monitor triggers multiple events during one appliance usage:

Your appliance may have a rest cycle.  Modify your settings file to change `seconds_to_end` to a larger number.  It should be longer than the rest cycle.



