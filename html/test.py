#!/usr/bin/python

# example taken from http://davidderiso.com/post/6168199987/using-python-and-jquery

import cgi, cgitb 
import logging
import os
import subprocess

cgitb.enable()  # for troubleshooting

#the cgi library gets vars from html
#form = cgi.FieldStorage()
#jquery_input = form.getvalue("stuff_for_python", "nothing sent")

cmd = "/home/pi/code/gphoto2-timelapse/timelapse.py /home/pi/code/gphoto2-timelapse/test.xml"

#ret = subprocess.call(cmd, shell=True)

p = subprocess.Popen(cmd, shell=True,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE,
                     )

(stdout, stderr) = p.communicate()
ret = p.returncode

#the next 2 'print' statements are important for web
print "Content-type: text/html"
print

if ret == 0:
    print "Shoot successful! \n" + stderr

else:
    print "Shoot failed! \n" + stderr

