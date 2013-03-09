'''
Created on Mar 8, 2013

@author: jlalonde
'''

import xml.dom.minidom
from datetime import timedelta

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
      self.nbShots = nbShotsAttributeNode.value
      
    delayAttributeNode = xmlElement.getAttributeNode('delay')
    if delayAttributeNode != None:
      self.delay = timedelta(minutes = int(delayAttributeNode.value));
      
    ignoreSunAttributeNode = xmlElement.getAttributeNode('ignoreSun')
    if ignoreSunAttributeNode != None:
      self.ignoreSun = bool(ignoreSunAttributeNode.value)
      
    # read all the exposures
    exposureNodes = xmlElement.getElementsByTagName('exposure')
    for node in exposureNodes:
      exposure = Exposure();
      exposure.fromXMLElement(node);
      self.exposures.append(exposure);
      
  def fromXMLFile(self, xmlFilename):
    """ Loads shoot information from an XML file """
    xmlDocument = xml.dom.minidom.parse(xmlFilename)
    
    shootElements = xmlDocument.getElementsByTagName('shoot')
    if len(shootElements) != 1:
      raise RuntimeError('Need exactly one shoot element in the XML file')
    
    self.fromXMLElement(shootElements[0])
    xmlDocument.unlink()
      
    
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
  
  def __init(self, name = '', value = ''):
    
    # configuration name (must be compatible with gphoto2 --list-config), but we're not going to check this.
    self.name = name;
    
    # configuration value (again, must be compatible with the camera)
    self.value = value;
    
    
  def fromXMLElement(self, xmlElement):
    nameAttributeNode = xmlElement.getAttributeNode('name')
    valueAttributeNode = xmlElement.getAttributeNode('value')
    
    if nameAttributeNode != None:
      if not valueAttributeNode != None:
        raise RuntimeError('Configuration name specified (' + nameAttributeNode.value + 
                           '), but no accompanying value.')
      
      self.name = nameAttributeNode.value
  
      
    

    
    

