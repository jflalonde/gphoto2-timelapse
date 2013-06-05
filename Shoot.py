'''
Created on Mar 8, 2013

@author: jlalonde
'''

import xml.dom.minidom
import os.path
from datetime import datetime, timedelta

class Shoot(object):
  """ Stores information relative to a shoot. See the file config-example.txt for valid XML files. """

  def __init__(self, folder = '/', filename = '', nbShots = float('inf'), delay = 1, 
               ignoreSun = True, exposures = [], initConfig = [], 
               downloadImages = True, camera = ''):
    """ Constructor """
    
    # shoot properties
    self.filename = filename
    self.folder = folder
    
    # number of exposure to take for each shot
    self.nbShots = nbShots
    
    # delay (in minutes) to wait in between shots
    self.delay = timedelta(minutes = delay)
    
    # whether to ignore the sun or not
    self.ignoreSun = bool(ignoreSun)
    
    # list of exposures
    self.exposures = exposures
    
    # list of initialization configuration
    self.initConfig = initConfig
    
    # whether or not to download images
    self.downloadImages = downloadImages
    
    # camera model
    self.camera = camera
    
  def fromXMLElement(self, xmlElement):
    # read attributes from the note (if available)
    
    filenameAttributeNode = xmlElement.getAttributeNode('filename')
    if filenameAttributeNode != None:
      self.filename = filenameAttributeNode.value

    folderAttributeNode = xmlElement.getAttributeNode('folder')
    if folderAttributeNode != None:
      self.folder = folderAttributeNode.value
    
    nbShotsAttributeNode = xmlElement.getAttributeNode('nbShots') 
    if nbShotsAttributeNode != None:
      self.nbShots = float(nbShotsAttributeNode.value)
      
    delayAttributeNode = xmlElement.getAttributeNode('delay')
    if delayAttributeNode != None:
      self.delay = timedelta(minutes = int(delayAttributeNode.value));
      
    ignoreSunAttributeNode = xmlElement.getAttributeNode('ignoreSun')
    if ignoreSunAttributeNode != None:
      self.ignoreSun = bool(int(ignoreSunAttributeNode.value))
      
    downloadImagesAttributeNode = xmlElement.getAttributeNode('downloadImages')
    if downloadImagesAttributeNode != None:
      self.downloadImages = bool(int(downloadImagesAttributeNode.value))
      
    cameraAttributeNode = xmlElement.getAttributeNode('camera')
    if cameraAttributeNode != None:
      self.camera = cameraAttributeNode.value
    
    # read all the exposures
    exposureNodes = xmlElement.getElementsByTagName('exposure')
    for node in exposureNodes:
      exp = Exposure(config=[])
      exp.fromXMLElement(node)
      self.exposures.append(exp)
      
    # read all the initialization configuration settings
    initNodes = xmlElement.getElementsByTagName('init')
    if len(initNodes) > 1:
      raise RuntimeError('Must have one (or zero) init node in the XML file. Found %d', len(initNodes))
    
    if len(initNodes) > 0:
      initConfigNodes = initNodes[0].getElementsByTagName('config')
      for node in initConfigNodes:
        config = Configuration()
        config.fromXMLElement(node)
        self.initConfig.append(config)
      
  def fromXMLFile(self, xmlFilename):
    """ Loads shoot information from an XML file """
    xmlDocument = xml.dom.minidom.parse(xmlFilename)
    
    shootElements = xmlDocument.getElementsByTagName('shoot')
    if len(shootElements) != 1:
      raise RuntimeError('Need exactly one shoot element in the XML file')
    
    self.fromXMLElement(shootElements[0])
    xmlDocument.unlink()
  
  def toGphotoCaptureCall(self, gphoto2Executable):
    """ Generates a gphoto2 call for the current shoot """
    call = gphoto2Executable + " "
    
    if self.camera != '':
      call = call + "--camera=\"" + self.camera + "\" "
    
    filenames = list()
    
    for exposureId in range(0, len(self.exposures)):
      # set the configuration(s)
      for config in self.exposures[exposureId].config:
        if config.name != None:
          call = call + "--set-config " + config.name + "=" + config.value + " "
            
      # capture the image
      if self.downloadImages:
        call = call + "--capture-image-and-download "
        
        # set the filename
        filename = os.path.join(self.filename, self.getFilename())
        filename = filename + "_%03n.cr2"
        call = call + "--filename " + filename + " "
        
        # we'll store the _actual_ filename (replacing the %03n by the actual value)
        filename = filename.replace("%03n", ("%03d" % (exposureId+1)))
        filenames.append(filename)

      else:
        call = call + "--folder=" + self.folder + " --capture-image "
            
    return (call, filenames)
  
  def toGphotoInitCall(self, gphoto2Executable):
    """ Generates a gphoto2 call to initialize """
    call = ''
    
    if len(self.initConfig) > 0:
      call = gphoto2Executable + " "
      
      if self.camera != '':
        call = call + "--camera=\"" + self.camera + "\" "
      
      for config in self.initConfig:
        if config.name != None:
          call = call + "--set-config " + config.name + "=" + config.value + " "
          
    return call
  
  def getFilename(self):
    """ Generates a unique filename (based on current time) """
    filename = datetime.now().strftime("%Y%m%d-%H%M%S")
    return filename
    
class Exposure(object):
  """ Stores information for a particular exposure (a list of configurations) """
  
  def __init__(self, config = []):
    # stores a list of configuration
    self.config = config;
    
  def fromXMLElement(self, xmlElement):
    # read the configuration objects (if any)
    configNodes = xmlElement.getElementsByTagName('config')
    
    # loop over all config children
    for node in configNodes:
      config = Configuration();
      config.fromXMLElement(node)
      self.config.append(config)
      
    
class Configuration(object):
  """ Stores configuration information (name and value) """
  
  def __init(self, name = None, value = None):
    """ Constructor """ 
    # configuration name (must be compatible with gphoto2 --list-config), but we're not going to check this.
    self.name = name;
    
    # configuration value (again, must be compatible with the camera)
    self.value = value;
    
    
  def fromXMLElement(self, xmlElement):
    """ Create a Configuration object from an XML element"""
    nameAttributeNode = xmlElement.getAttributeNode('name')
    valueAttributeNode = xmlElement.getAttributeNode('value')
    
    if nameAttributeNode != None:
      if not valueAttributeNode != None:
        raise RuntimeError('Configuration name specified (' + nameAttributeNode.value + 
                           '), but no accompanying value.')
      
      self.name = nameAttributeNode.value
      self.value = valueAttributeNode.value
  
      
    

    
    

