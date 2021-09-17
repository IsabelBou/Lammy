import asyncio
import traceback
from contextlib import suppress
from pickle import dump, load

from discord import guild

from config.config import Emojis
from config.dataclasses import User
from Lammy import Lammy, GuildData


class ConfigurationSaver:
    def __init__(self, target_file: str, bot: Lammy, interval=5):
        self.target_file = target_file
        self._interval = interval
        self._task = None
        self._running_bot = bot

    async def _run(self):
        while True:
            await asyncio.sleep(self._interval)
            with open(self.target_file, "wb") as fd:
                try:
                    dump(self._conf_data, fd)
                except TypeError as e:
                    print(repr(e))
                    print(self._conf_data)
                except Exception as e:
                    print(traceback.format_exception(type(e), e, e.__traceback__))

    async def _start(self):
        try:
            await self._load_conf_data()
            await self._run()
        except Exception as e:
            print(traceback.format_exception(type(e), e, e.__traceback__))

    def start(self):
        loop = asyncio.get_event_loop()
        self._task = loop.create_task(self._start())

    def stop(self):
        self._task.cancel()

    async def _load_conf_data(self):
        with suppress(FileNotFoundError, EOFError):
            with open(self.target_file, 'rb') as fd:
                conf = load(fd)
                await self._running_bot.bot.wait_until_ready()
                self._running_bot.guilds_data = {
                    guild_id: GuildData.from_json(self._running_bot.bot, guild_conf)
                    for guild_id, guild_conf in conf.items()
                }
                for guild_data, guild_conf in zip(self._running_bot.guilds_data.values(), conf.values()):
                    if guild_conf.get("is_colo_task"):
                        self._running_bot.start_colo_task(guild_data)
                    if guild_conf.get("is_demon_task"):
                        self._running_bot.start_demon_task(guild_data)
                    if guild_conf["is_started_conquest"]:
                        self._running_bot.start_bot_conquest_pings(guild_data)

    @property
    def _conf_data(self):
        return {
            guild_id: guild_data.to_json() for guild_id, guild_data in self._running_bot.guilds_data.items()
        }
