"""
Client library for the LG Smart TV running NetCast 3 or 4.

LG Smart TV models released in 2012 (NetCast 3.0) and LG Smart TV models
released in 2013 (NetCast 4.0) are supported.

The client is inspired by the work of
https://github.com/ubaransel/lgcommander
"""
import logging
import requests
from xml.etree import ElementTree

_LOGGER = logging.getLogger(__name__)

__all__ = ['LgNetCastClient', 'LG_COMMAND', 'LG_QUERY', 'LgNetCastError',
           'AccessTokenError', 'SessionIdError']


# LG TV handler
LG_HANDLE_KEY_INPUT = 'HandleKeyInput'
LG_HANDLE_MOUSE_MOVE = 'HandleTouchMove'
LG_HANDLE_MOUSE_CLICK = 'HandleTouchClick'
LG_HANDLE_TOUCH_WHEEL = 'HandleTouchWheel'
LG_HANDLE_CHANNEL_CHANGE = 'HandleChannelChange'

DEFAULT_PORT = 8080
DEFAULT_TIMEOUT = 3


class LG_COMMAND(object):
    """LG TV remote control commands."""
    POWER = 1
    NUMBER_0 = 2
    NUMBER_1 = 3
    NUMBER_2 = 4
    NUMBER_3 = 5
    NUMBER_4 = 6
    NUMBER_5 = 7
    NUMBER_6 = 8
    NUMBER_7 = 9
    NUMBER_8 = 10
    NUMBER_9 = 11
    UP = 12
    DOWN = 13
    LEFT = 14
    RIGHT = 15
    OK = 20
    HOME_MENU = 21
    BACK = 23
    VOLUME_UP = 24
    VOLUME_DOWN = 25
    MUTE_TOGGLE = 26
    CHANNEL_UP = 27
    CHANNEL_DOWN = 28
    BLUE = 29
    GREEN = 30
    RED = 31
    YELLOW = 32
    PLAY = 33
    PAUSE = 34
    STOP = 35
    FAST_FORWARD = 36
    REWIND = 37
    SKIP_FORWARD = 38
    SKIP_BACKWARD = 39
    RECORD = 40
    RECORDING_LIST = 41
    REPEAT = 42
    LIVE_TV = 43
    EPG = 44
    PROGRAM_INFORMATION = 45
    ASPECT_RATIO = 46
    EXTERNAL_INPUT = 47
    PIP_SECONDARY_VIDEO = 48
    SHOW_SUBTITLE = 49
    PROGRAM_LIST = 50
    TELE_TEXT = 51
    MARK = 52
    VIDEO_3D = 400
    LR_3D = 401
    DASH = 402
    PREVIOUS_CHANNEL = 403
    FAVORITE_CHANNEL = 404
    QUICK_MENU = 405
    TEXT_OPTION = 406
    AUDIO_DESCRIPTION = 407
    ENERGY_SAVING = 409
    AV_MODE = 410
    SIMPLINK = 411
    EXIT = 412
    RESERVATION_PROGRAM_LIST = 413
    PIP_CHANNEL_UP = 414
    PIP_CHANNEL_DOWN = 415
    SWITCH_VIDEO = 416
    APPS = 417


class LG_QUERY(object):
    """LG TV data queries."""
    CUR_CHANNEL = 'cur_channel'
    CHANNEL_LIST = 'channel_list'
    CONTEXT_UI = 'context_ui'
    VOLUME_INFO = 'volume_info'
    SCREEN_IMAGE = 'screen_image'
    IS_3D = 'is_3d'


class LgNetCastClient(object):
    """LG NetCast TV client using the ROAP protocol."""

    HEADER = {'Content-Type': 'application/atom+xml'}
    XML = '<?xml version=\"1.0\" encoding=\"utf-8\"?>'
    KEY = XML + '<auth><type>AuthKeyReq</type></auth>'
    AUTH = XML + '<auth><type>%s</type><value>%s</value></auth>'
    COMMAND = XML + '<command><session>%s</session><type>%s</type>%s</command>'

    def __init__(self, host, access_token):
        """Initialize the LG TV client."""
        self.url = 'http://%s:%s/roap/api/' % (host, DEFAULT_PORT)
        self.access_token = access_token
        self._session = None

    def __enter__(self):
        """Context manager method to support with statement."""
        self._session = self._get_session_id()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager method to support with statement."""
        self._session = None

    def send_command(self, command):
        """Send remote control commands to the TV."""
        message = self.COMMAND % (self._session, LG_HANDLE_KEY_INPUT,
                                  '<value>%s</value>' % command)
        self._send_to_tv('command', message)

    def change_channel(self, channel):
        """Send change channel command to the TV."""
        message = self.COMMAND % (self._session, LG_HANDLE_CHANNEL_CHANGE,
                                  ElementTree.tostring(channel,
                                                       encoding='unicode'))
        self._send_to_tv('command', message)

    def query_data(self, query):
        """Query status information from the TV."""
        response = self._send_to_tv('data', payload={'target': query})
        if response.status_code == requests.codes.ok:
            data = response.text
            tree = ElementTree.XML(data)
            data_list = []
            for data in tree.iter('data'):
                data_list.append(data)
            return data_list

    def _get_session_id(self):
        """Get the session key for the TV connection.

        If a pair key is defined the session id is requested otherwise display
        the pair key on TV.
        """
        if not self.access_token:
            self._display_pair_key()
            raise AccessTokenError('No access token specified to create session.')
        message = self.AUTH % ('AuthReq', self.access_token)
        response = self._send_to_tv('auth', message)
        if response.status_code != requests.codes.ok:
            raise SessionIdError('Can not get session id from TV.')
        data = response.text
        tree = ElementTree.XML(data)
        session = tree.find('session').text
        if len(session) >= 8:
            return session
        else:
            raise SessionIdError('Can not get session id from TV.')

    def _display_pair_key(self):
        """Send message to display the pair key on TV screen."""
        self._send_to_tv('auth', self.KEY)

    def _send_to_tv(self, message_type, message=None, payload=None):
        """Send message of given type to the tv."""
        url = '%s%s' % (self.url, message_type)
        if message:
            response = requests.post(url, data=message, headers=self.HEADER,
                                     timeout=DEFAULT_TIMEOUT)
        else:
            response = requests.get(url, params=payload, headers=self.HEADER,
                                    timeout=DEFAULT_TIMEOUT)
        return response


class LgNetCastError(Exception):
    """Base class for all exceptions in this module."""


class AccessTokenError(LgNetCastError):
    """No access token specified to create session."""


class SessionIdError(LgNetCastError):
    """No session id could be retrieved from TV."""
