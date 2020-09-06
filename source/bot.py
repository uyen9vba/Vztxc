import cgi
import datetime
import re
import sys
import urllib
import random
import abc

from managers.scheduler import Scheduler, BackgroundScheduler
from managers.database import DatabaseManager
from managers.irc_ import IRCManager
from managers.command import CommandManager
from managers.phrase import PhraseManager
from managers.access_token import UserAccessTokenManager
from managers.http import HTTPManager
from wrappers.helix import HelixWrapper
from wrappers.redis import RedisWrapper
from utilities.client_auth import ClientAuth
from utilities.logger import *
from utilities.tmi import *


class Bot:
    def __init__(self, config, args):
        self.args = args
        self.config = config["config"]
        self.phrases = config["phrases"]
        self.twitch = config["twitch"]
        self.api = config["api"]

        self.client_auth = ClientAuth(
            client_id=self.config.get("client_id"),
            client_secret=self.config.get("client_secret"),
            redirect_uri=self.config.get("redirect_uri")
        )

        if self.config.getboolean("verified", False):
            self.tmi_status = TMIStatus.verified
        elif self.config.getboolean("known", False):
            self.tmi_status = TMIStatus.known
        else:
            self.tmi_status = TMIStatus.moderator

        HTTPManager.init()
        Scheduler.init()
        BackgroundScheduler.init()

        self.database_manager = DatabaseManager(url=self.api.get("database"))
        self.background_scheduler = BackgroundScheduler()
        self.redis_wrapper = RedisWrapper()
        self.helix_wrapper = HelixWrapper(
            url=self.api.get("helix"),
            config=self.config,
            RedisWrapper=self.redis_wrapper,
            ClientAuth=self.client_auth
        )

        self.bot_userdata = self.helix_wrapper.get_userdata_by_login(self.config.get("name"))
        self.channel_userdata = self.helix_wrapper.get_userdata_by_login(self.config.get("channel"))

        self.token_manager = UserAccessTokenManager(
            RedisWrapper=self.redis_wrapper,
            username=self.config.get("name"),
            user_id=self.bot_userdata.get("id", None)
        )

        self.irc_manager = IRCManager(self)
        self.command_manager = CommandManager(self.database_manager)
        self.phrase_manager = PhraseManager(self.database_manager)

        if self.channel_userdata["id"] is None:
            raise ValueError("Config: channel name not found on https://api.twitch.tv/helix")
        
        if self.bot_userdata["id"] is None:
            raise ValueError("Config: bot name not found on https://api.twitch.tv/helix")

    def password(self):
        return f"oauth:{self.token_manager.access_token}"

    def execute_delayed(self, delay, method, *args, **kwargs):
        self.scheduler.execute_after

    def parse_message(self, message, source, event, tags={}, whisper=False):
        message = message.lower()

        #if not whisper and event.target == 
        #

    def quit(self, **options):
        self.commit()

        try:
            BackgroundScheduler.scheduler.print_jobs()
            BackgroundScheduler.scheduler.shutdown(wait=False)
        except a:
            logger.exception("Error while shutting down APScheduler")

        try:
            for a in self.phrases["quit"]:
                self.irc_manager.message(self.channel, a)
        except:
            logger.exception("Exception caught while trying to message quit phrase")
            
        sys.exit(0)

    def commit(self):
        for key, a in self.command_manager.commands:
            a.commit()

        for key, a in self.phrase_manager.phrases:
            a.commit()

    def start(self):
        self.irc_manager.start()
        self.irc_manager.reactor.process_forever()