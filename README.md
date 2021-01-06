# u-blox GPS Configuration Scripts
A set of Python scripts to change the configuration settings of u-blox GPS modules. 

# IGNORE ALL DOCUMENTATION AFTER THIS SECTION!
This library is very much in flux as things are partially ported to a newer Python 3 compatible library without gobject and instead using PySerial.

## Tested working utils with an M8N module:
- getset-messagerate.py (CFG-MSG)
- set-baudrate.py (CFG-PRT)
- ask-position.py (NAV-STATUS, NAV-POSLLH)
- getset-gnssconfiguration.py (CFG-GNSS)
- get-pollconfiguration (CFG-INF)
- save-configuration (CFG-CFG)
- load-configuration (CFG-CFG)
- load-defaultconfiguration (CFG-CFG)

## Installation
### Mac OS X
brew install pygobject

## Execution
You will need to know the serial port device path. For the Inforce HSUART, this is /dev/ttyHSL2, which is the default path. For Mac OS X and the USB port, this is something like /dev/cu.usbmodem1234.

### configure
The configure script sets up a default set of messages for an M8U

```./configure -d <device path>```

Example: ```./configure -d /dev/cu.usbmodem1234```

### stream
The stream script displays the data stream. By default, this will call the configuration script to set up the receiver.

```./stream -d <device path>```

Example: ```./stream -d /dev/cu.usbmodem1234```

### capture
This saves the raw data stream to a file. The file name is ublox_YYYYMMDDTHHMMSS.ubx. A directory to save the file in may be optionally specified. By default, this will call the configuration script to set up the receiver.

```./stream -d <device path> <directory to save the file>```

Example: ```./stream -d /dev/cu.usbmodem1234```

### parseToPickle.py
This converts a UBX file to a pickle file, generating a dictionary keyed by message name, e.g. HNR-PVT, with each value a list of message dictionaries. The pickle file with have the same name as the UBX file, but with the .pickle extension.

```./parseToPickle.py <UBX file>```

### plotSvInfo.py
This plots many of the key data fields in a pickle file as time series plots

```./plotSvInfo.py <pickle file>```

### generateKmlFromPickle.py
This generates a KML track from a pickle file which can be opened in Google Earth. This requires mapper-kml, which is in the mapper-hw-pcbTools repo. By default, the KML file will have the same filename as the pickle file, but with the .kml extension.

```./generateKmlFromPickle.py <pickle file>```
    
