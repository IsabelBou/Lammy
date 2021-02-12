from pickle import dump, load
from threading import Timer

from Lammy import Lammy


class ConfigurationSaver:
    def __init__(self, target_file: str, bot: Lammy, interval=5):
        self.target_file = target_file
        self._interval = interval
        self._timer = None
        self._running_bot = bot

    def _run(self):
        self._timer = Timer(self._interval, self._run)
        self._timer.start()
        with open(self.target_file, "wb") as fd:
            dump(self._conf_data, fd)

    def start(self):
        try:
            self._load_conf_data()
        except FileNotFoundError as e:
            pass
        self._run()

    def stop(self):
        self._timer.cancel()

    def _load_conf_data(self):
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

    @property
    def _conf_data(self):
        return dict(
            assignments=self._running_bot.assignments,
            equipped_nms=self._running_bot.equipped_nms,
            admin_roles=self._running_bot.admin_roles,
            member_roles=self._running_bot.member_roles,
            afks=self._running_bot.afks,
            colo_time=self._running_bot.colo_time,
            demons=(self._running_bot.demon1, self._running_bot.demon2)
        )
