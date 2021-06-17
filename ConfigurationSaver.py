import asyncio
import traceback
from contextlib import suppress
from pickle import dump, load

from config.config import Emojis
from config.dataclasses import User
from Lammy import Lammy


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
                self._running_bot.assignments = conf["assignments"]
                self._running_bot.equipped_nms = conf["equipped_nms"]
                self._running_bot.colo_channel_data = conf["channel_data"]

                guild = self._running_bot.bot.get_guild(self._running_bot.colo_channel_data[1])
                if guild:
                    self._running_bot.admin_roles = set(ConfigurationSaver.role_from_id(guild, role)
                                                        for role in conf["admin_roles"]) - {None}
                    self._running_bot.member_roles = set(ConfigurationSaver.role_from_id(guild, role)
                                                         for role in conf["member_roles"]) - {None}

                self._running_bot.afks = conf["afks"]
                self._running_bot.colo_time = conf["colo_time"]
                self._running_bot.demon1 = conf["demons"][0]
                self._running_bot.demon2 = conf["demons"][1]
                self._running_bot.sp_colo_nm_order = conf["sporder"]
                self._running_bot.nm_order = conf["order"]
                self._running_bot.conquest_channel_data = conf["conquest_channel_data"]
                
                if isinstance(list(conf["conquest_user_data"].values())[0], list):
                    self._running_bot.conquest_user_data = conf["conquest_user_data"]
                if conf.get("is_colo_task"):
                    await asyncio.ensure_future(self._running_bot.start_colo_task(None))
                if conf.get("is_demon_task"):
                    await asyncio.ensure_future(self._running_bot.start_demon_task(None))
                if conf["is_started_conquest"]:
                    await asyncio.ensure_future(self._running_bot.start_bot_conquest_pings(None))

    @staticmethod
    def role_from_id(guild, search_role):
        for role in guild.roles:
            if role.mention == search_role:
                return role
        return None if isinstance(search_role, str) else search_role

    @property
    def _conf_data(self):
        bot = self._running_bot
        return dict(
            assignments=bot.assignments,
            equipped_nms=bot.equipped_nms,
            admin_roles=set(role if isinstance(role, User) else role.mention for role in bot.admin_roles),
            member_roles=set(role if isinstance(role, User) else role.mention for role in bot.member_roles),
            afks=bot.afks,
            colo_time=bot.colo_time,
            demons=(bot.demon1, bot.demon2),
            channel_data=bot.colo_channel_data,
            is_colo_task=bot.colo_task is not None,
            is_demon_task=bot.demon_task is not None,
            order=bot._nm_order,
            sporder=bot._sp_colo_nm_order,
            conquest_channel_data=bot.conquest_channel_data,
            conquest_user_data=bot.conquest_user_data,
            is_started_conquest=bot.conquest_task is not None
        )
