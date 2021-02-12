from ConfigurationSaver import ConfigurationSaver
from Lammy import Lammy

if __name__ == "__main__":
    bot = Lammy()
    conf_saver = ConfigurationSaver("configuration.p", bot)
    conf_saver.start()
    bot.run()
    conf_saver.stop()
