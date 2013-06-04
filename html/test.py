#!/usr/bin/python

# example taken from http://davidderiso.com/post/6168199987/using-python-and-jquery

import cgi, cgitb 
import logging
import os
import subprocess

cgitb.enable()  # for troubleshooting

#the cgi library gets vars from html
form = cgi.FieldStorage()
jquery_input = form.getvalue("input", "")

basePath = "/home/pi/code/gphoto2-timelapse"
xmlInit = os.path.join(basePath, "init.xml")
xmlShoot = os.path.join(basePath, "shoot.xml")

xmlFile = ""

if jquery_input == "init":
    # use the initialization xml file
    xmlFile = xmlInit

else:
    # use the main xml file
    xmlFile = xmlShoot


cmd = "/home/pi/code/gphoto2-timelapse/timelapse.py " + xmlFile

# launch the command
# TODO: use the timelapse module directly!
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

