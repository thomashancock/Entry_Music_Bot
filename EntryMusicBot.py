# bot.py
import os
import sys
import json
import random

# Setup logging
import logging
logger = logging.getLogger(__file__)
import LoggerSettings

import discord

settings_file = sys.argv[1]
print(f"Using settings file: {settings_file}")

def proc_settings(file):
    with open(file, "r") as read_file:
        return json.load(read_file)

data = proc_settings(settings_file)

TOKEN = data["token"]
GUILD = data["guild"]
TRACK_MAP = data["tracks"]
RANDOM = data["random"]

class MyClient(discord.Client):

    def load_tracks(self, settings_file):
        logger.info("Loading Track List:")
        data = proc_settings(settings_file)
        self.track_map = data["tracks"]
        self.random_tracks = data["random"]
        self.print_tracks()

    def print_tracks(self):
        for user, track in self.track_map.items():
            print(f"\t{user:16}- {track}")
        print("\n\tRandom Tracks:")
        for track in self.random_tracks:
            print(f"\t{' '*16}- {track}")

    async def on_ready(self):
        '''
        Setup
        '''
        logger.info("Running on_ready")
        for guild in client.guilds:
            if guild.name == GUILD:
                self.guild = guild
                break

        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )

        # Save pointers to useful channels
        self.vc = None
        self.general_text_channel = None
        for channel in guild.channels:
            if channel.name == "General":
                self.vc = await channel.connect()
            if channel.name == "bot-testing":
                self.general_text_channel = channel


    async def on_message(self, message):
        '''
        Commands to do on message
        '''
        if message.author == self.user:
            return

        # Reload Track Information
        if message.content.startswith('!reload'):
            self.load_tracks(settings_file)
            await message.channel.send('Reloaded track data')


    async def on_voice_state_update(self, member, before, after):
        '''
        Do stuff on voice state change
        '''
        if member == self.user:
            return

        if before.channel is None and after.channel is not None:
            logger.info(f"Detected {member.name} joining {after.channel.name}")
            # if self.general_text_channel != None:
                # await self.general_text_channel.send(f"{member} joined voice chat!")

            if self.vc != None:
                if member.name in self.track_map:
                    track = self.track_map[member.name]
                else:
                    track_no = random.randrange(0, len(self.random_tracks))
                    if track_no > len(self.random_tracks):
                        logger.error("Track index out of range. Default to 0.")
                        track_no = 0
                    track = self.random_tracks[track_no]

                try:
                    logger.info(f"Playing {track}")
                    self.vc.play(discord.FFmpegPCMAudio(f"tracks/{track}"))
                    self.vc.source = discord.PCMVolumeTransformer(self.vc.source, volume=0.3)
                except discord.errors.ClientException:
                    logger.info(f"{member.name} joined but already playing audio.")

logger.info("Declaring client")
client = MyClient()
client.load_tracks(settings_file)
logger.info("Running client")
client.run(TOKEN)
