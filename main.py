from ConfigurationSaver import ConfigurationSaver
from keep_alive import run_keep_alive
from Lammy import Lammy

if __name__ == "__main__":
    bot = Lammy()
    conf_saver = ConfigurationSaver("configuration.p", bot)
    conf_saver.start()
    run_keep_alive()
    bot.run()
    conf_saver.stop()
