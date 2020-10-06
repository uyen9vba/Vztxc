import configparser
import argparse
import os
import sys

from bot import Bot
from utilities.logger import *
from managers.http import HTTPManager
from managers.scheduler import Scheduler, BackgroundScheduler
from managers.irc_ import IRCManager


def run(args):
    config = configparser.ConfigParser()

    if not config.read("C:/Users/Niklas/Projects/Oesbot/source/config.ini", encoding="utf-8"):
        logger.error("Config path missing")
        sys.exit(0)

    HTTPManager.init()
    Scheduler.init()
    BackgroundScheduler.init()

    bot = Bot(config, args)

    bot.start()


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--config", "-c", default="config.ini", help="Choose config (default: config.ini)")
    args = args_parser.parse_args()

    debug()

    run(args)