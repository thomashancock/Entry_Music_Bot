# bot.py
import sys

# Setup logging
import logging
logger = logging.getLogger(__file__)
import LoggerSettings

import EntryMusicBot


settings_file = sys.argv[1]
print(f"Using settings file: {settings_file}")


client = EntryMusicBot.EntryMusicBot(settings_file)
token = client.get_token()
client.run(token)
