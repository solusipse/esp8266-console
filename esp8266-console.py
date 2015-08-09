#!/usr/bin/python

import cmd, os.path, serial, sys, os
from time import *

try:
    import configparser as cfgparser
except(ImportError):
    import ConfigParser as cfgparser



class Serial():
    # Standard baud rates for esp8266
    rates = [ 115200, 57600, 9600 ]
    error = 0
    s = serial.Serial()

    def __init__(self, speed=9600, timeout=0, nil=0, silent=0):
        if self._check_parameters():
            self.error = 1
            return

        if nil:
            return

        self.s = serial.Serial( c.get("device"), speed, timeout=timeout )
        if self.s.isOpen():
            self.s.close()
        self.s.open()
        if not silent:
            print("Connected to %s at speed %s." % (c.get("device"), c.get("speed")) )

    def __del__(self):
        try:
            self.s.close()
        except(AttributeError):
            pass

    def _check_parameters(self):
        if not c.get("device").strip():
            print("You provided no device name. Use `device` command.")
            return 1
        if not os.path.exists( c.get("device") ):
            print("Device %s does not exist!" % c.get("device") )
            return 1

        return 0

    def probe_speed(self):
        if self.error:
            return

        for r in self.rates:
            t = Serial(speed=r, timeout=1, silent=1)
            out = t.send('AT+GMR')
            if out[0] == "OK":
                print("Found correct speed: %s." % str(r))
                return r

        if (out != "OK"):
            print("Error: couldn't find correct baud rate!")
            sys.exit(1)
            

    def send(self, data):
        self.s.flushInput()
        self.s.write( data + "\r\n" )

        return self._read(self.s)

    def _read(self, s):
        buf = []
        out = s.readline()
        sleep(0.2)

        timer = time()

        while True:
            while s.inWaiting():
                out = s.readline().strip()
                if len(out) > 1:
                    buf.append(out)
                sleep(0.1)
            if "ERROR" in out:
                break
            if "OK" in out:
                break
            if s.timeout and not len(buf):
                if time() - timer > s.timeout:
                    break
            sleep(0.1)

        return [out, buf]


class Config():

    name = "esp8266-console"

    def __init__(self):
        self._check()

    def _create(self):

        directory = os.path.dirname(self._get_filename())

        if not os.path.exists(directory):
            os.makedirs(directory)

        cp = cfgparser.RawConfigParser()
        cp.add_section(self.name)
        cp.set(self.name, "device", "")
        cp.set(self.name, "speed", "")

        with open(self._get_filename(), 'wb') as cfile:
            cp.write(cfile)

    def _get_filename(self):
        
        if sys.platform == 'win32':
            appdata = os.path.join(os.environ['APPDATA'], self.name)
        else:
            appdata = os.path.expanduser(os.path.join("~", "." + self.name))

        return os.path.join(appdata, "config.ini")

    def _check_if_exists(self, f):
        return os.path.isfile(f)

    def get(self, var):
        cp = cfgparser.RawConfigParser()
        cp.read(self._get_filename())
        return cp.get(self.name, var)

    def set(self, var, val):
        cp = cfgparser.RawConfigParser()
        cp.read(self._get_filename())
        cp.set(self.name, var, val)

        with open(self._get_filename(), 'wb') as cfile:
            cp.write(cfile)

    def _display_warning(self):
        print("Program not configured. Please set device, e.g.:")
        print("  device /dev/cu.usbserial")
        print("Then set baud rate, e.g. `speed 115200` or use autodetection:")
        print("  speed auto")

    def _check(self):
        if not self._check_if_exists(self._get_filename()):
            self._display_warning()
            self._create()


class Console(cmd.Cmd):

    port = None
    prompt = "(cmd) "

    def do_device(self, device):
        'device: set default device.'
        if not device.strip():
            print(c.get("device"))
        else:
            c.set("device", device)

    def do_speed(self, speed):
        'speed: set baud rate (speed). Use `speed auto` for auto detection.'
        if not speed:
            print(c.get("speed"))
        else:
            if speed == "auto":
                c.set("speed", Serial(nil=1).probe_speed())
            else:
                c.set("speed", speed)

    def do_connect(self, dev):
        'connect: Connect to the default device. connect /dev/device: connect to selected device.'
        if self.port == None:
            self.port = Serial(c.get("speed"))
            self.prompt = "(serial) "
        else:
            if self.port.s.isOpen():
                print("Already connected!")
            
    def do_close(self, *args):
        'close: close current connection.'
        if self.port == None:
            print("Not connected!")
            return

        if self.port.s.isOpen():
            del self.port
            self.prompt = "(cmd) "
            print("Disconnected!")

    def do_send(self, cm):
        'send: send command to device.'
        if self.port == None:
            print("Not connected!")
            return

        if not self.port.s.isOpen():
            print("Not connected!")
            return
            
        out = self.port.send(cm)
        for l in out[1]:
            print(l)

    def do_quit(self, *args):
        self.do_close()
        return True

    def do_exit(self, *args):
        self.do_close()
        return True

    def cmdloop(self):
        try:
            cmd.Cmd.cmdloop(self)
        except KeyboardInterrupt as e:
            self.cmdloop()


if __name__ == '__main__':
    print("============================================================")
    print("Welcome to esp8266-console.")
    print("Type help or ? to list commands.")
    print("============================================================")
    c = Config()
    Console().cmdloop()