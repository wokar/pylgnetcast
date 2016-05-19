# PyLgNetcast

A Python 3 library and command line tool to control LG Smart TV running NetCast 3.0 (LG Smart TV models released in 2012) and NetCast 4.0 (LG Smart TV models released in 2013) via TCP/IP.

## Dependencies

pylgnetcast requires:
 * Python 3
 * [requests](https://pypi.python.org/pypi/requests) package.

## API Usage

```python
from xml.etree import ElementTree
from pylgnetcast import LgNetCastClient, LG_COMMAND, LG_QUERY

with LgNetCastClient('192.168.1.5', '889955') as client:
    client.send_command(LG_COMMAND.MUTE_TOGGLE)
    data = client.query_data(LG_QUERY.VOLUME_INFO)
    if data:
        print(ElementTree.tostring(data[0], encoding='unicode'))
```

## Command Line Tool
PyLgNetCast also provides a simple command line tool to remote control a TV.

The tool needs a pairing key to be allowed to send commands to your TV.
To get the pairing key just start the tool while your TV is on:
```sh
python -m pylgnetcast --host <IP of your TV>
```
This will display the pairing key on your TV.

To retrieve status information from your TV start the tool like:
```sh
python -m pylgnetcast --host <IP of your TV>  --pairing_key <pairing key of your TV>
```
This will display information about the current channel, volume, 3D mode, etc. retrieved from your TV.

If you want to send a command to your TV, for instance to turn the volume up, check the list of available commands in the pylgnetcast.py file.
The class LG_COMMAND defines all supported commands and volume up would be defined as 24.
```sh
python -m pylgnetcast --host <IP of your TV>  --pairing_key <pairing key of your TV> --command 24
```


