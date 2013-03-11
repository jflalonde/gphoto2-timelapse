'''
Created on Mar 8, 2013

@author: jlalonde
'''

import xml.dom.minidom
import os.path
from datetime import datetime, timedelta

class Shoot(object):
  """ Stores information relative to a shoot. See the file config-example.txt for valid XML files. """

  def __init__(self, folder = '.', nbShots = float('inf'), delay = 1, 
               ignoreSun = True, exposures = []):
    """ Constructor """
    
    # shoot properties
    self.folder = folder;
    
    # number of exposure to take for each shot
    self.nbShots = nbShots;
    
    # delay (in minutes) to wait in between shots
    self.delay = timedelta(minutes = delay);
    
    # whether to ignore the sun or not
    self.ignoreSun = bool(ignoreSun);
    
    # list of exposures
    self.exposures = exposures;
    
  def fromXMLElement(self, xmlElement):
    # read attributes from the note (if available)
    
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
      self.ignoreSun = bool(ignoreSunAttributeNode.value)
      
    # read all the exposures
    exposureNodes = xmlElement.getElementsByTagName('exposure')
    for node in exposureNodes:
      exp = Exposure(config=[])
      exp.fromXMLElement(node)
      self.exposures.append(exp)
      
  def fromXMLFile(self, xmlFilename):
    """ Loads shoot information from an XML file """
    xmlDocument = xml.dom.minidom.parse(xmlFilename)
    
    shootElements = xmlDocument.getElementsByTagName('shoot')
    if len(shootElements) != 1:
      raise RuntimeError('Need exactly one shoot element in the XML file')
    
    self.fromXMLElement(shootElements[0])
    xmlDocument.unlink()
  
  def toGphoto2Call(self, gphoto2Executable):
    """ Generates a gphoto2 call for the current shoot """
    call = gphoto2Executable + " "
    
    for exposure in self.exposures:
      # set the configuration(s)
      for config in exposure.config:
        if config.name != None:
          call = call + "--set-config " + config.name + "=" + config.value + " "
            
      # capture the image
      call = call + "--capture-image-and-download --force-overwrite "
      
    # set the filename
    filename = os.path.join(self.folder, self.getFilename())
    call = call + "--filename " + filename + "_%03n.cr2"
      
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
  
      
    

    
    

