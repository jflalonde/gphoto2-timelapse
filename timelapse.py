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

from datetime import datetime, timedelta
import os
import time
import subprocess
import sys
from Shoot import Shoot

import sun

# the time between photos
#DELTA = timedelta(seconds = 20)
#DELTA = timedelta(minutes = 5)
#picture_folder = '/home/pi/gphoto2-timelapse/photos'
DEBUG = False
#ignore_sun = True

# specify the path to the gphoto2 executable
gphoto2Executable = '/usr/local/bin/gphoto2'

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
print 'Taking a total of ' + str(shootInfo.nbShots) + ' shots, and waiting ' + \
str(shootInfo.delay) + ' minutes between each shot'
print 'Each shot will have  ' + str(len(shootInfo.exposures)) + ' exposure(s)'



def parse_int(s) :
  try :
    return int(s)
  except ValueError:
    return None
  except TypeError:
    return None

def get_prefix() :
  """
  look at the filenames already in the picture folder and look for files with a prefix.  Find the biggest prefix 
  and make the new prefix 1 larger.  This is so that even if the clock gets reset (as it does if the raspberrypi
  looses power), the pictures can still be reassembled in the order that they were taken
  """
  
  import glob
  filenames = glob.glob(shootInfo.folder + '*.jpg')
  max_prefix = 0
  for filename in filenames :
    parts = filenames.split('_')
    if len(parts) > 1 :
      possible_prefix = parse_int(parts[0])
      if possible_prefix > max_prefix :
        max_prefix = possible_prefix
  
  max_prefix += 1
  return '%04d' % max_prefix

prefix = get_prefix()
# or if you prefer no prefix, uncomment the following line
# prefix = ''

def log(message) :
  print datetime.utcnow(), message

def run(cmd) :
  # reset_camera()
  
  # try running the command once and if it fails, reset_camera
  # and then try once more
  for i in range(2) :
    log("running %s" % cmd)
    
    p = subprocess.Popen(
      cmd,
      shell=True,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
    )
    (stdout, stderr) = p.communicate()
    ret = p.returncode
    
    if stdout.strip() != '' or DEBUG :
      if stdout[-1] == '\n' :
        stdout = stdout[:-1]
      print 'stdout'
      print '>> '+stdout.replace('\n', '\n>> ')
      print 'end stdout'
    if stderr.strip() != '' or DEBUG :
      if stderr[-1] == '\n' :
        stderr = stderr[:-1]
      print 'stderr'
      print '>> '+stderr.replace('\n', '\n>> ')
      print 'end stderr'
    if DEBUG :
      print 'ret', ret
    
    if ret == 0 :
      return ret, stdout, stderr
    elif ret == 1 :
      if 'No camera found' in stderr :
        print '#### no camera found'
        print 'TODO: reboot?'
        print 'TODO: reset power on camera via GP IO?'
        return ret, stdout, stderr
      else :
        # other error like tried to delete a file where there was none, etc
        return ret, stdout, stderr
    
  return ret, stdout, stderr

def reset_camera() :
  log('reset usb')
  
  # not sure what the 'lsusb' command does...
  ret = os.popen('lsusb').read()
  for line in ret.split('\n') :
    if 'Nikon' not in line : continue
    
    ret = os.popen("./usbreset /dev/bus/usb/%s/%s" % (line[4:7], line[15:18])).read()
    if 'successful' not in ret :
      print 'ret', ret

import re

def list_files() :
  folder = ''
  files = []
  
  stdout, _ = run('gphoto2 --list-files')
  for line in stdout.split('\n') :
    if not line : continue
    
    if line[0] == '#' :
      files.append((folder, line.split()[0][1:], line.split()[1]))
    else :
      m = re.match(".*'(.*)'", line)
      if m :
        folder = m.group(1)
        if folder[-1] != '/' :
          folder += '/'
      else :
        log('warning, unknown output of --list-files: ' + line)
  
  return files

workaround = True
def take_picture(filename = None) :
  if not filename :
    filename = prefix + '_' + datetime.utcnow().strftime("%Y%m%d-%H%M%S.jpg")
  
  log('taking picture')
  if workaround :
    # this works around --capture-image-and-download not working
    # get rid of any existing files on the card
    for folder, _ in list_files() :
      delete_picture(from_folder = folder)
    
    # take the picture
    run(gphoto2Executable + " --capture-image")
    
    # copy the picture from the camera to local disk
    run(gphoto2Executable + " --get-file=1 --filename=%s/%s" % (shootInfo.folder, filename))
    
    ## delete file off of camera
    #delete_picture()
  else :
    return run(gphoto2Executable + " --capture-image-and-download --filename %s/%s" % (shootInfo.folder, filename))

def delete_picture(from_folder = None) :
  log('deleting picture')
  
  if from_folder :
    print 'from_folder', from_folder
    ret, stdout, _ = run(gphoto2Executable + " --delete-file=1 --folder=%s" % from_folder)
    if 'There are no files in folder' in stdout :
      return ret
  
  # try deleting from all 3 known folders, in the order of most likely
  ret, stdout, stderr = run(gphoto2Executable + " --delete-file=1 --folder=/store_00010001")
  if 'There are no files in folder' in stderr :
    ret, stdout, stderr = run(gphoto2Executable + " --delete-file=1 --folder=/store_00010001/DCIM/100NIKON")
    if 'There are no files in folder' in stderr :
      ret, stdout, stderr = run(gphoto2Executable + " --delete-file=1 --folder=/")
  
  return ret

def reset_settings() :
  log('reseting settings')
  run(gphoto2Executable + " --set-config /main/capturesettings/flashmode=1")
  run(gphoto2Executable + " --set-config /main/capturesettings/focusmode=0")

reset_settings()

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
    print "Waiting for the sun to come out"
    
  tCur = datetime.utcnow()
  
  tDelay = tCur - tInit
  if tDelay < shootInfo.delay:
    waitTime = shootInfo.delay - tDelay
    
    print 'Waiting ' + str(waitTime.seconds) + 's...'
    time.sleep(waitTime.seconds)
    
  # compute the desired time
  #print datetime.utcnow(), 'waiting ...'
  #while datetime.utcnow() < t + shootInfo.delay :
  #  time.sleep(1)

