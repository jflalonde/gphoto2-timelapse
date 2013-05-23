Description
===========

`gphoto2-timelapse` allows you to create timelapse photography using a supported DSLR camera 
connected via USB (http://gphoto.org/proj/libgphoto2/support.php), and the gphoto2 unix tool 
(http://www.gphoto.org/).

Supports:
- single photo
- continuous time-lapse
- continous day-time time-lapse
- multiple exposures
- automatic configuration from XML file.

Installation
============

You will need to install python to run the scripts: http://www.python.org/getit/

You can use the install scripts - gphoto2-install / install

It's a great idea to install `gphoto2` from source as the pre-built libraries are generally old. 
The `gphoto2-install` script does just this.

Dependencies 
------------

You will need the `ephem` python toolbox, available from: http://rhodesmill.org/pyephem/.

Use
===

Once everything is installed, you need to tweak the script and the XML configuration file a bit to get 
it to work with your own camera. Once you have the camera specific parameters and functions in place, 
you can use the python scripts to start taking images:

    python timelapse.py test.xml
    
See [config-example.md](https://github.com/jflalonde/gphoto2-timelapse/blob/master/config-example.md) 
for additional documentation on the XML configuration file. Editing this file 
will allow you to easily change the behavior of the time-lapse sequence you're capturing. 

Credits
=======

This code originated from the following python script by `dwiel`:

- http://dwiel.net/blog/raspberry-pi-timelapse-camera/

Thank you for the inspiration!
