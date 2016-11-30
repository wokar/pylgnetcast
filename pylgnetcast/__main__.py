"""
Simple command line tool to control a LG NetCast TV.
"""
import argparse
import logging
import sys
from xml.etree import ElementTree

from . pylgnetcast import LgNetCastClient, AccessTokenError, LG_QUERY

_LOGGER = logging.getLogger(__name__)


def main():
    """Process command line and send commands to TV."""
    parser = argparse.ArgumentParser(prog='pylgnetcast',
                        description='Remote control for a LG NetCast TV.')
    parser.add_argument('--host', metavar='host', type=str, required=True,
                        help='Address of the TV')
    parser.add_argument('--pairing_key', metavar='pairing_key', type=str,
                        help='Pairing key to access the TV')
    parser.add_argument('--protocol', metavar='protocol', type=str,
                        default='roap',
                        help='LG TV protocol hdcp or roap')
    parser.add_argument('--command', metavar='command', type=int,
                        help='Remote control command to send to the TV')
    parser.add_argument('--verbose', dest='verbose', action='store_const',
                        const=True, default=False,
                        help='debug output')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    try:
        with LgNetCastClient(args.host, args.pairing_key,
                             args.protocol) as client:
            if args.command:
                client.send_command(args.command)
                print('Sent command %s' % args.command)

            infos = {'Channel Info': LG_QUERY.CUR_CHANNEL,
                     'Volume Info': LG_QUERY.VOLUME_INFO,
                     'Context Info': LG_QUERY.CONTEXT_UI,
                     'Is 3D': LG_QUERY.IS_3D}
            for title, query in infos.items():
                try:
                    data = client.query_data(query)
                    if data:
                        print('%s: %s' %
                              (title, ElementTree.tostring(data[0],
                                                           encoding='unicode')))
                except Exception as error:
                    'Can not retrieve %s - error: %s' % (title.lower(), error)
    except AccessTokenError:
        print('Access token is displayed on TV - '
              'use it for the --pairing_key parameter to connect to your TV.')


if __name__ == '__main__':
    sys.exit(main())
