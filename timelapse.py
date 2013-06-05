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
gphoto2Executable = 'export LD_LIBRARY_PATH=/usr/local/lib; gphoto2'

# specify the (full) path to the 'usbreset' executable
usbresetExecutable = '/home/pi/code/gphoto2-timelapse/usbreset'

# setup logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', 
                    level=logging.DEBUG)
    
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
logging.info('Taking a total of %d shots, and waiting %s minutes between each shot', 
            shootInfo.nbShots, str(shootInfo.delay))
logging.info('Each shot will have %d exposure(s)', len(shootInfo.exposures))

def run(cmd) :
  # try running the command once and if it fails, reset_camera
  # and then try once more
  logging.debug("running %s" % cmd)
    
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

def readNumImagesFromCamera() :
  # not sure what's going on, but it's better to reset more than not enough I guess.
  reset()
  
  cmd = gphoto2Executable + " --folder=" + shootInfo.folder + " --num-files --quiet"
  numExistingImages = int(run(cmd))
  
  logging.debug("Found %d images on the folder %s" % (numExistingImages, shootInfo.folder))
  
  return numExistingImages

def takeShot(filename = None) :
  # if we're not downloading images, first check how many images there are in the destination folder
  prevExistingImages = 0
  if not shootInfo.downloadImages:
    prevExistingImages = readNumImagesFromCamera()
  
  logging.info('Taking %d exposure(s)', len(shootInfo.exposures))
  (call, filenames) = shootInfo.toGphotoCaptureCall(gphoto2Executable)
  
  run(call)
  
  if shootInfo.downloadImages:
    for filename in filenames:
      # check if images were correctly saved to disk
      if not os.path.exists(filename):
        raise RuntimeError('File not successfully saved to disk: ' + filename)
      else: 
        logging.debug('File successfully saved to disk: ' + filename)
        
    logging.info('Image(s) saved to %s', shootInfo.filename)
        
  else:
    # we're leaving the images on the camera. check if they were correctly captured. how?
    curNumExistingImages = readNumImagesFromCamera()
    
    if (curNumExistingImages-prevExistingImages) != len(shootInfo.exposures):
      raise RuntimeError('Not all images were captured on the camera!')
    else:
      logging.info('Image(s) saved to %s', shootInfo.folder) 
      
    
def reset():
  # use gphoto2's reset command (new with gphoto 2.5.2 and above)
  cmd = gphoto2Executable + ' --reset'
  run(cmd)
  
  run("killall PTPCamera")


def initialize() :
  logging.info('Initializing settings')
  
  if shootInfo.onPi:
    # If we're on the Pi, disable the gphoto2 daemon process
    run("killall gphoto2")
    run("killall gvfsd-gphoto2")
    run("killall gvfs-gphoto2-volume-monitor")

  else:
    # In Mac OSX, disable the PTPCamera process
    run("killall PTPCamera")
    
  # Also, reset the usb to make sure everything works
  reset()
  
  # make sure picture mode is set to "faithful" (not sure if this affects RAW files...)
  # In our case, this should be equal to 5
  # TODO: add these checks to the configuration files
  #out = run(gphoto2Executable + " --get-config /main/capturesettings/picturestyle")
  #if not 'Current: Faithful' in out:
  #  raise RuntimeError('Camera needs to be set in the "Faithful" picture style')
  #logging.info('Camera in the faithful picture style')
  
  # we should also check whether we are in 'M' mode 
  out = run(gphoto2Executable + " --get-config /main/capturesettings/autoexposuremode")
  if not 'Current: Manual' in out:
    raise RuntimeError('Camera needs to be set in "Manual" mode')
  logging.info('Camera in manual mode')
    
  # capture full-resolution RAW files
  call = shootInfo.toGphotoInitCall(gphoto2Executable)
  run(call)
  
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
    logging.info('Waiting for the sun to come out')
  
  if nbShots < shootInfo.nbShots:
    # wait only if we still need to shoot
    tCur = datetime.utcnow()
  
    tDelay = tCur - tInit
    if tDelay < shootInfo.delay:
      # wait only if the delay is larger than the time it took to take the shot (gphoto2 can be quite slow)
      waitTime = shootInfo.delay - tDelay
    
      logging.info('Waiting ' + str(waitTime.seconds) + 's...')
      time.sleep(waitTime.seconds)
      
logging.info('All done!')
    
