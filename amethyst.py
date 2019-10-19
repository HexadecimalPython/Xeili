from discord import utils as dutils
from utils.database import PlyvelDict
import traceback
import argparse
import json
import discord
import asyncio
import aiohttp

with open("config.json") as f:
    config = json.load(f)

token = config.get('NOTUS_TOKEN')
prefixes = config.get('NOTUS_PREFIXES', [])


class Notus(discord.Client):
    def __init__(self, config, **options):
        super().__init__(**options)
        self.db = PlyvelDict('./.notus_db')
        self.owner = None
        self.config = config
        self.send_command_help = send_cmd_help

        if 'settings' not in self.db:
            self.db['settings'] = {}

        if 'blacklist' not in self.db['settings']:
            self.db['settings']['blacklist'] = []

    async def on_ready(self):
        self.session = aiohttp.ClientSession()

        app_info = await self.application_info()
        self.invite_url = dutils.oauth_url(app_info.id)
        self.owner = str(app_info.owner.id)

        print('Ready.')
        print(self.invite_url)
        print(self.user.name)

        self.load_extension('modules.core')

    async def on_command_error(self, exception, context):
        if isinstance(exception, commands_errors.MissingRequiredArgument):
            await self.send_command_help(context)
        elif isinstance(exception, commands_errors.CommandInvokeError):
            exception = exception.original
            _traceback = traceback.format_tb(exception.__traceback__)
            _traceback = ''.join(_traceback)
            error = ('`{0}` in command `{1}`: ```py\n'
                     'Traceback (most recent call last):\n{2}{0}: {3}\n```')\
                .format(type(exception).__name__,
                        context.command.qualified_name,
                        _traceback, exception)
            await context.send(error)
        elif isinstance(exception, commands_errors.CommandNotFound):
            pass

    async def close(self):
        await self.session.close()
        await super().close()

    async def on_message(self, message):
        if (not message.content or message.author.bot or
                (str(message.author.id) in self.db['settings']['blacklist'] and
                 str(message.author.id) not in self.owners)
        ):
            return


notus = Notus(config)
notus.run(token)
