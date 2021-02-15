import asyncio
from contextlib import suppress
from pickle import dump, load

from Lammy import Lammy


class ConfigurationSaver:
    def __init__(self, target_file: str, bot: Lammy, interval=5):
        self.target_file = target_file
        self._interval = interval
        self._task = None
        self._running_bot = bot

    async def _run(self):
        await asyncio.sleep(self._interval)
        with open(self.target_file, "wb") as fd:
            dump(self._conf_data, fd)
        await self._run()

    async def _start(self):
        await self._load_conf_data()
        await self._run()

    def start(self):
        loop = asyncio.get_event_loop()
        self._task = loop.create_task(self._start())

    def stop(self):
        self._task.cancel()

    async def _load_conf_data(self):
        with suppress(FileNotFoundError, EOFError):
            with open(self.target_file, 'rb') as fd:
                conf = load(fd)
                self._running_bot.assignments = conf["assignments"]
                self._running_bot.equipped_nms = conf["equipped_nms"]
                self._running_bot.admin_roles = conf["admin_roles"]
                self._running_bot.member_roles = conf["member_roles"]
                self._running_bot.afks = conf["afks"]
                self._running_bot.colo_time = conf["colo_time"]
                self._running_bot.demon1 = conf["demons"][0]
                self._running_bot.demon2 = conf["demons"][1]
                self._running_bot.channel_data = conf["channel_data"]
                if conf["is_started"]:
                    asyncio.ensure_future(self._running_bot.start_bot_waiting(None))

    @property
    def _conf_data(self):
        bot = self._running_bot
        return dict(
            assignments=bot.assignments,
            equipped_nms=bot.equipped_nms,
            admin_roles=bot.admin_roles,
            member_roles=bot.member_roles,
            afks=bot.afks,
            colo_time=bot.colo_time,
            demons=(bot.demon1, bot.demon2),
            channel_data=bot.channel_data,
            is_started=bot.colo_task is not None and bot.demon_task is not None
        )