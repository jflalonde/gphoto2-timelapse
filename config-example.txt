We use XML files to specify what kind of shoot to be taken. 

The simplest kind of shoot is to take a single exposure with the current settings. 
This is achieved with the following XML configuration file, which takes a single shot and stores it in /home/me.

<?xml version="1.0" encoding="UTF-8"?>
<shoot nbShots="1" folder="/home/me">
  <exposure/>
</shoot>


By setting 'nbShots' to Inf and delay to a value (in minutes), we effectively implement a continuous time-lapse
capture setup.

<?xml version="1.0" encoding="UTF-8"?>
<shoot folder="/home/me" nbShots="Inf" delay="1">
  <exposure/>
</shoot>


We can also tell our script to stop capturing photos if the sun is down by setting the 'ignoreSun' flag to false
(defaults to true):

<?xml version="1.0" encoding="UTF-8"?>
<shoot folder="/home/me" nbShots="Inf" delay="1" ignoreSun="false">
  <exposure/>
</shoot>


We can specify (one or many) configuration settings to be used for the photo by adding a list of <config> tags
to the photo. Each config tag's name and value correspond to the --set-config name/value in gphoto2. 
For example, here we set the aperture to f/8 and the shutter speed to 1/1000:

<?xml version="1.0" encoding="UTF-8"?>
<shoot folder="/home/me" nbShots="Inf" delay="1" ignoreSun="false">
  <exposure>
    <config name="/main/capturesettings/aperture" value="8" />
    <config name="/main/capturesettings/shutterspeed" value="1000" />
  </exposure>
</shoot>


Finally, we can ask our script to take multiple exposures (with possibly different configurations) at each 
time instant in our time-lapse capture.

<?xml version="1.0" encoding="UTF-8"?>
<shoot folder="/home/me" nbShots="Inf" delay="1" ignoreSun="false">
  <exposure>
    <config name="/main/capturesettings/aperture" value="8" />
    <config name="/main/capturesettings/shutterspeed" value="1000" />
  </exposure>
  <exposure>
    <config name="/main/capturesettings/aperture" value="10" />
    <config name="/main/capturesettings/shutterspeed" value="500" />
  </exposure>
</shoot>


