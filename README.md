# esp8266-console
Handy console for serial communication with ESP8266 chip. Linux, OS X and Windows support.

## Install
```
sudo easy_install pyserial
```

```
sudo bash -c 'curl \
https://raw.githubusercontent.com/solusipse/esp8266-console/master/esp8266-console.py > \
/usr/bin/esp8266-console && chmod a+x /usr/bin/esp8266-console'
```

## Usage
esp8266-console is used for serial communication with your ESP8266-based board. I use it with cheap USB-Serial converter `PL2303HX`.

Example usage:

[![asciicast](https://asciinema.org/a/cbzpp05m9af8e7si6wq4ov7us.png)](https://asciinema.org/a/cbzpp05m9af8e7si6wq4ov7us)

### Commands

#### device
```
device /dev/device_name
```
Set path to serial port.

#### speed
```
speed auto
```
Automatically detect baud rate.
```
speed 9600
```
Set baud rate to 9600.

#### connect
```
connect
```
Connect to selected device at selected speed.

#### close
```
close
```
Disconnect from the device.

## License
See `LICENSE`.
