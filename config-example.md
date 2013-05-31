Example configurations
======================

We can obtain different behaviors simply by changing the input XML configuration files.

Single photo
------------

The simplest kind of shoot is to take a single exposure with the current settings. 
This is achieved with the following XML configuration file, which takes a single shot and stores it in `/home/me`.

    <shoot nbShots="1" folder="/home/me">
      <exposure/>
    </shoot>
    
Saving images
-------------

We can tell the script to keep the images on the camera, or to download them each time one is captured.
If `downloadImages` is set to `1` (the default), images are downloaded at capture time. Otherwise, 
images are left on the camera. 

    <shoot downloadImages="1">
      <exposure/>
    </shoot>

Continuous time-lapse
---------------------

By setting `nbShots` to `Inf` and delay to a value (in minutes), we effectively implement a continuous time-lapse
capture setup.

    <shoot folder="/home/me" nbShots="Inf" delay="1">
      <exposure/>
    </shoot>

Continous day-time time-lapse
-----------------------------

We can also tell our script to stop capturing photos if the sun is down by setting the `ignoreSun` flag to `false`
(defaults to `true`):

    <shoot folder="/home/me" nbShots="Inf" delay="1" ignoreSun="0">
      <exposure/>
    </shoot>


Configuration
-------------

We can specify (one or many) configuration settings to be used for the photo by adding a list of `config` tags
to the photo. Each config tag's name and value correspond to the `--set-config` name/value in `gphoto2`. 
For example, here we set the aperture to f/8 and the shutter speed to 1/1000:

    <shoot folder="/home/me" nbShots="Inf" delay="1" ignoreSun="0">
      <exposure>
        <config name="/main/capturesettings/aperture" value="8" />
        <config name="/main/capturesettings/shutterspeed" value="1/1000" />
      </exposure>
    </shoot>
    
Initialization
--------------

We can tell our script to launch a series of configuration commands once, at initialization. This can be used, 
for example, to tell our camera that we want to shoot in RAW:

    <shoot folder="/home/me" nbShots="Inf" delay="1" ignoreSun="0">
      <init>
         <config name="/main/imgsettings/imageformat" value="20" /> <!-- Capture RAW files -->
      </init>
    </shoot>


Multiple exposures 
------------------

We can ask our script to take multiple exposures (with possibly different configurations) at each 
time instant in our time-lapse capture.

    <shoot folder="/home/me" nbShots="Inf" delay="1" ignoreSun="0">
      <exposure>
        <config name="/main/capturesettings/aperture" value="8" />
        <config name="/main/capturesettings/shutterspeed" value="1/1000" />
      </exposure>
      <exposure>
        <config name="/main/capturesettings/aperture" value="10" />
        <config name="/main/capturesettings/shutterspeed" value="1/500" />
      </exposure>
    </shoot>


