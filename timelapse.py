#!/usr/bin/env python
"""
NOTE: many settings in here are specific to the NIKON3000 and will need to be 
tweaked for other cameras

TODO:
* slow down interval at night
* do an image diff between the past few images to see how fast things are
  changing.  If they are changing slowly, slow down the interval
* fix how the delay is computed (should just compute the time to sleep 
  directly instead of waiting by increments of 1 minute)
"""

from datetime import datetime
import time
import subprocess
import sys
import os
from Shoot import Shoot

import logging
import sun

DEBUG = False

# specify the path to the gphoto2 executable
gphoto2Executable = '/usr/bin/gphoto2'

# specify the (full) path to the 'usbreset' executable
usbresetExecutable = '/home/pi/code/gphoto2-timelapse/usbreset'

# setup logger
logger = logging.getLogger('TimelapseLogger')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
# setup console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

def usage():
  """ Prints usage information """
  print 'Usage: timelapse.py config.xml'
  
  
if len(sys.argv) < 2:
  # check if we're given an XML file.
  usage()
  
# create a default Shoot object, read the XML file
shootInfo = Shoot()
shootInfo.fromXMLFile(sys.argv[1])

# Display high-level information
logger.info('Taking a total of %d shots, and waiting %s minutes between each shot', 
            shootInfo.nbShots, str(shootInfo.delay))
logger.info('Each shot will have %d exposure(s)', len(shootInfo.exposures))

def run(cmd) :
  reset()
  
  # try running the command once and if it fails, reset_camera
  # and then try once more
  logger.debug("running %s" % cmd)
    
  if not DEBUG: 
    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                       )
      
    
    (stdout, stderr) = p.communicate()
    ret = p.returncode
      
    if ret == 1:
      if 'No camera found' in stderr:
        raise RuntimeError('Error talking to the camera: ' + stderr)
      
    return stdout
  
  return ''

def takeShot(filename = None) :
  logger.info('Taking %d exposure(s)', len(shootInfo.exposures))
  call = shootInfo.toGphotoCaptureCall(gphoto2Executable)
  
  run(call)
  
  if shootInfo.downloadImages:
    # TODO: check if images were correctly saved to disk! Crap out if not since this indicates an error...
    logger.info('Image(s) saved to %s', shootInfo.folder)
  
def reset():
  ret = os.popen('lsusb').read()
  for line in ret.split('\n') :
    if 'Canon' not in line : continue

    usbresetCmd = "%s /dev/bus/usb/%s/%s" % (usbresetExecutable, line[4:7], line[15:18])
    os.system(usbresetCmd)
    logger.debug("Resetting the USB port: %s", usbresetCmd)

def initialize() :
  logger.info('Initializing settings')
  
  if shootInfo.onPi:
    # If we're on the Pi, disable the gphoto2 daemon process
    run("killall gvfsd-gphoto2")
    
    # Also, reset the usb to make sure everything works
    reset()
    
  else:
    # In Mac OSX, disable the PTPCamera process
    run("killall PTPCamera")
  
  # make sure picture mode is set to "faithful" (not sure if this affects RAW files...)
  # In our case, this should be equal to 5
  # TODO: add these checks to the configuration files
  #out = run(gphoto2Executable + " --get-config /main/capturesettings/picturestyle")
  #if not 'Current: Faithful' in out:
  #  raise RuntimeError('Camera needs to be set in the "Faithful" picture style')
  #logger.info('Camera in the faithful picture style')
  
  # we should also check whether we are in 'M' mode 
  out = run(gphoto2Executable + " --get-config /main/capturesettings/autoexposuremode")
  if not 'Current: Manual' in out:
    raise RuntimeError('Camera needs to be set in "Manual" mode')
  logger.info('Camera in manual mode')
    
  # capture full-resolution RAW files
  call = shootInfo.toGphotoInitCall(gphoto2Executable)
  run(call)
  
  # TODO: set white balance

initialize()

nbShots = 0
# loop until we have the required number of shots
while nbShots < shootInfo.nbShots:
  tInit = datetime.utcnow()
  
  # only take pictures when it is light out
  if shootInfo.ignoreSun or sun.is_light(tInit):
    # reset_camera()
    takeShot()
    nbShots += 1
  else :
    logger.info('Waiting for the sun to come out')
  
  if nbShots < shootInfo.nbShots:
    # wait only if we still need to shoot
    tCur = datetime.utcnow()
  
    tDelay = tCur - tInit
    if tDelay < shootInfo.delay:
      # wait only if the delay is larger than the time it took to take the shot (gphoto2 can be quite slow)
      waitTime = shootInfo.delay - tDelay
    
      logger.info('Waiting ' + str(waitTime.seconds) + 's...')
      time.sleep(waitTime.seconds)
      
logger.info('All done!')
    
