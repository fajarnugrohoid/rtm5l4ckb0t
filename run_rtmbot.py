#!/usr/bin/env python
from argparse import ArgumentParser
import sys
import os
import yaml

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
    json = [{},{},{}]
    temp_arrjson = []
    final_arrjson = {}
    json[0]["stars"] = 0
    json[0]["last_star_ts"] = "1969-12-31T19:00:00-0500"
    json[0]["name"] = "fajar"
    final_arrjson["01"] = json[0]
    #print("temp_arrjson:", final_arrjson[0])
    json[1]["stars"] = 0
    json[1]["last_star_ts"] = "1969-12-31T19:00:00-0500"
    json[1]["name"] = "fajar"
    final_arrjson["02"] = json[1]
    print("temp_arrjson:", final_arrjson)
    main()