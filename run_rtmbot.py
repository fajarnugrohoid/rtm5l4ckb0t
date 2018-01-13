#!/usr/bin/env python
from argparse import ArgumentParser
import sys
import os
import yaml
import datetime

from core import RtmBot

sys.path.append(os.getcwd())

def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        '-c',
        '--config',
        help='Full path to config file.',
        metavar='path'
    )
    return parser.parse_args()


def main(args=None):
    # load args with config path if not specified
    if not args:
        args = parse_args()
    config = yaml.load(open(args.config or 'rtmbot.conf', 'r'))
    bot = RtmBot(config)
    try:
        bot.start()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    updated_at = "2018-01-07 17:59:10.649000"
    #var_update_at=datetime.datetime.strptime(updated_at, '%H:%M')
    today = datetime.datetime.today()
    myTime = datetime.datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S.%f")
    myFormat = "%Y-%m-%d"
    xxx = myTime.strftime(myFormat)
    xxy = datetime.datetime.strptime(xxx, "%Y-%m-%d")
    diff = today - xxy
    diffdays=diff.days

    print("New:", str(diffdays))

    main()