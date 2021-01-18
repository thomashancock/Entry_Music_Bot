# bot.py
import os
import sys
import json
import random

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
        print("Loading Track List:")
        data = proc_settings(settings_file)
        self.track_map = data["tracks"]
        for user, track in self.track_map.items():
            print(f"\t{user}:\t{track}")
        self.random_tracks = data["random"]
        print("\n\tRandom Tracks:")
        for track in self.random_tracks:
            print(f"\t\t{track}")

    async def on_ready(self):
        '''
        Setup
        '''
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

        # Reply to hello
        if message.content.startswith('!hello'):
            await message.channel.send('Hello!')

        # Send gif
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
            print(f"Detected {member.name} joining {after.channel.name}")
            # if self.general_text_channel != None:
                # await self.general_text_channel.send(f"{member} joined voice chat!")

            if self.vc != None:
                if member.name in self.track_map:
                    track = self.track_map[member.name]
                else:
                    track_no = random.randrange(0, len(self.random_tracks))
                    if track_no > len(self.random_tracks):
                        print("Error: Track index out of range. Default to 0.")
                        track_no = 0
                    track = self.random_tracks[track_no]

                try:
                    self.vc.play(discord.FFmpegPCMAudio(f"tracks/{track}"))
                    self.vc.source = discord.PCMVolumeTransformer(self.vc.source, volume=0.3)
                except discord.errors.ClientException:
                    print("User joined but already playing audio.")


client = MyClient()
client.load_tracks(settings_file)
client.run(TOKEN)
