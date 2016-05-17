"""
Client library for the LG Smart TV running NetCast 3 or 4.

LG Smart TV models released in 2012 (NetCast 3.0) and LG Smart TV models
released in 2013 (NetCast 4.0) are supported.

The client is inspired by the work of
https://github.com/ubaransel/lgcommander
"""
from http.client import HTTPConnection
import logging
from xml.etree import ElementTree

_LOGGER = logging.getLogger(__name__)

# LG TV remote control commands
LG_CMD_POWER = 1
LG_CMD_NUMBER_0 = 2
LG_CMD_NUMBER_1 = 3
LG_CMD_NUMBER_2 = 4
LG_CMD_NUMBER_3 = 5
LG_CMD_NUMBER_4 = 6
LG_CMD_NUMBER_5 = 7
LG_CMD_NUMBER_6 = 8
LG_CMD_NUMBER_7 = 9
LG_CMD_NUMBER_8 = 10
LG_CMD_NUMBER_9 = 11
LG_CMD_UP = 12
LG_CMD_DOWN = 13
LG_CMD_LEFT = 14
LG_CMD_RIGHT = 15
LG_CMD_OK = 20
LG_CMD_HOME_MENU = 21
LG_CMD_BACK = 23
LG_CMD_VOLUME_UP = 24
LG_CMD_VOLUME_DOWN = 25
LG_CMD_MUTE_TOGGLE = 26
LG_CMD_CHANNEL_UP = 27
LG_CMD_CHANNEL_DOWN = 28
LG_CMD_BLUE = 29
LG_CMD_GREEN = 30
LG_CMD_RED = 31
LG_CMD_YELLOW = 32
LG_CMD_PLAY = 33
LG_CMD_PAUSE = 34
LG_CMD_STOP = 35
LG_CMD_FAST_FORWARD = 36
LG_CMD_REWIND = 37
LG_CMD_SKIP_FORWARD = 38
LG_CMD_SKIP_BACKWARD = 39
LG_CMD_RECORD = 40
LG_CMD_RECORDING_LIST = 41
LG_CMD_REPEAT = 42
LG_CMD_LIVE_TV = 43
LG_CMD_EPG = 44
LG_CMD_PROGRAM_INFORMATION = 45
LG_CMD_ASPECT_RATIO = 46
LG_CMD_EXTERNAL_INPUT = 47
LG_CMD_PIP_SECONDARY_VIDEO = 48
LG_CMD_SHOW_SUBTITLE = 49
LG_CMD_PROGRAM_LIST = 50
LG_CMD_TELE_TEXT = 51
LG_CMD_MARK = 52
LG_CMD_3D_VIDEO = 400
LG_CMD_3D_LR = 401
LG_CMD_DASH = 402
LG_CMD_PREVIOUS_CHANNEL = 403
LG_CMD_FAVORITE_CHANNEL = 404
LG_CMD_QUICK_MENU = 405
LG_CMD_TEXT_OPTION = 406
LG_CMD_AUDIO_DESCRIPTION = 407
LG_CMD_ENERGY_SAVING = 409
LG_CMD_AV_MODE = 410
LG_CMD_SIMPLINK = 411
LG_CMD_EXIT = 412
LG_CMD_RESERVATION_PROGRAM_LIST = 413
LG_CMD_PIP_CHANNEL_UP = 414
LG_CMD_PIP_CHANNEL_DOWN = 415
LG_CMD_SWITCH_VIDEO = 416
LG_CMD_APPS = 417
# LG TV handler
LG_HANDLE_KEY_INPUT = 'HandleKeyInput'
LG_HANDLE_MOUSE_MOVE = 'HandleTouchMove'
LG_HANDLE_MOUSE_CLICK = 'HandleTouchClick'
LG_HANDLE_TOUCH_WHEEL = 'HandleTouchWheel'
LG_HANDLE_CHANNEL_CHANGE = 'HandleChannelChange'
# LG TV scroll commands
LG_CMD_SCROLL_UP = 'up'
LG_CMD_SCROLL_DOWN = 'down'
# LG TV data queries
LG_QUERY_CUR_CHANNEL = 'cur_channel'
LG_QUERY_CHANNEL_LIST = 'channel_list'
LG_QUERY_CONTEXT_UI = 'context_ui'
LG_QUERY_VOLUME_INFO = 'volume_info'
LG_QUERY_SCREEN_IMAGE = 'screen_image'
LG_QUERY_3D = 'is_3d'

DEFAULT_PORT = 8080
DEFAULT_TIMEOUT = 3


class LgNetCastClient(object):
    """LG NetCast TV client using the ROAP protocol."""

    HEADER = {'Content-Type': 'application/atom+xml'}
    XML = '<?xml version=\"1.0\" encoding=\"utf-8\"?>'
    KEY = XML + '<auth><type>AuthKeyReq</type></auth>'
    AUTH = XML + '<auth><type>%s</type><value>%s</value></auth>'
    COMMAND = XML + '<command><session>%s</session><type>%s</type>%s</command>'

    def __init__(self, host, access_token):
        """Initialize the LG TV client."""
        self.host = host
        self.access_token = access_token
        self.session = None

    def send_command(self, command):
        """Send remote control commands to the TV."""
        if not self.session:
            self.session = self._get_session_id()
        if self.session:
            message = self.COMMAND % (self.session, LG_HANDLE_KEY_INPUT,
                                      '<value>%s</value>' % command)
            self._send_to_tv(message, 'command')

    def change_channel(self, channel):
        """Send change channel command to the TV."""
        if not self.session:
            self.session = self._get_session_id()
        if self.session:
            message = self.COMMAND % (self.session, LG_HANDLE_CHANNEL_CHANGE,
                                      ElementTree.tostring(channel,
                                                           encoding='unicode'))
            self._send_to_tv(message, 'command')

    def query_data(self, query):
        """Query status information from the TV."""
        if not self.session:
            self.session = self._get_session_id()
        if self.session:
            http_response = self._send_to_tv(None, 'data?target=%s' % query)
            if http_response and http_response.reason == 'OK':
                data = http_response.read()
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
            return
        message = self.AUTH % ('AuthReq', self.access_token)
        http_response = self._send_to_tv(message, 'auth')
        if http_response and http_response.reason != 'OK':
            return
        data = http_response.read()
        tree = ElementTree.XML(data)
        session = tree.find('session').text
        if len(session) >= 8:
            return session

    def _display_pair_key(self):
        """Send message to display the pair key on TV screen."""
        self._send_to_tv(self.KEY, 'auth')

    def _send_to_tv(self, message, message_type):
        """Send message of given type to the tv."""
        conn = HTTPConnection(self.host, port=DEFAULT_PORT,
                              timeout=DEFAULT_TIMEOUT)
        if message:
            _LOGGER.debug('POST message: %s' % message)
            conn.request('POST', '/roap/api/%s' % message_type, message,
                         headers=self.HEADER)
        else:
            _LOGGER.debug('POST message: %s' % message)
            conn.request('GET', '/roap/api/%s' % message_type,
                         headers=self.HEADER)
        return conn.getresponse()
