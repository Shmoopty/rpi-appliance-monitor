# Raspberry Pi Appliance Monitor

Get notified on your phone or desktop when appliances begin or end their cycles
This device makes use of the nicely sensitive 801s vibration sensor.  It will detect faint shaking and if the shaking lasts a specified amount of time, it will assume that the appliance is running. 

![Completed device](https://cloud.githubusercontent.com/assets/1101856/21469692/1143d1fa-ca27-11e6-9986-e12b9c23e189.jpg "Completed device")

This works on clothes washers and dryers, dishwashers, garage door openers, fans, furnaces, and other machines that vibrate.

You can receive tweets or PushBullet notifications when a device starts vibrating or when it stops.

## Needed parts:

* A [Raspberry Pi Zero](https://www.raspberrypi.org/products/pi-zero/)
* Any old MicroSD card (2GB is plenty)
* A USB WiFi dongle (and a MicroUSB adapter if you choose the Pi Zero)
* An [801s vibration sensor module](https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Dcomputers&field-keywords=801s+vibration+sensor)
* Any 1 amp microUSB power source (What most phones and tablets from the last 10 years use) 

![Parts](https://cloud.githubusercontent.com/assets/1101856/21469691/1141fa38-ca27-11e6-8c7e-c1d389709a06.jpg "Parts")

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

![Sensor inserted](https://cloud.githubusercontent.com/assets/1101856/21469689/113ee280-ca27-11e6-979f-a2d7c1aeb3bb.jpg "Sensor inserted")


# Step 3: Create the software

After you ssh to the pi, install a few essential libraries:

    $ sudo apt-get install python-pip
    $ sudo pip install requests tweepy

Create the program file [`/home/pi/vibration.py`](https://raw.githubusercontent.com/Shmoopty/rpi-appliance-monitor/master/vibration.py) (Click to view)


Create the settings file [`/home/pi/vibration_settings.ini`](https://raw.githubusercontent.com/Shmoopty/rpi-appliance-monitor/master/vibration_settings.ini)

* Create a PushBullet Access Token key here:  https://www.pushbullet.com/#settings/account
* Create Twitter API keys here (Steps 1-4): http://nodotcom.org/python-twitter-tutorial.html

Edit `/etc/rc.local` To make the program run at boot.

Add before the `exit` line:

    python /home/pi/vibration.py /home/pi/vibration_settings.ini &

You’re done!  Reboot and test it out.

If you’ve soldered the sensor pins, you can bend the sensor to be flush with the Pi.


