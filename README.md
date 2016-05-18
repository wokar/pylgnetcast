# PyLgNetcast

A Python 3 library to control LG Smart TV running NetCast 3.0 (LG Smart TV models released in 2012) and NetCast 4.0 (LG Smart TV models released in 2013) via TCP/IP.

## Dependencies

pylgnetcast requires Python 3 and the [requests](https://pypi.python.org/pypi/requests) package.

## Usage

```python
from xml.etree import ElementTree
from pylgnetcast.pylgnetcast import (
    LgNetCastClient, LG_CMD_MUTE_TOGGLE, LG_QUERY_VOLUME_INFO)

client = LgNetCastClient('192.168.1.5', '889955')
client.send_command(LG_CMD_MUTE_TOGGLE)
data = client.query_data(LG_QUERY_VOLUME_INFO)
if data:
    print(ElementTree.tostring(data[0], encoding='unicode'))
```
