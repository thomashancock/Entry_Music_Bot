# EntryMusicBot.py
import json
import random

# Setup logging
import logging
logger = logging.getLogger(__file__)
import LoggerSettings

import discord


class EntryMusicBot(discord.Client):

    def __init__(self, settings_file):
        '''
        Initialise the class from the config file
        '''
        logger.info("Creating client")

        data = self._read_json(settings_file)

        self.primary_text_channel = None
        self.primary_voice_channel = None

        self.token = data["token"]
        self.guild_name = data["guild"]
        self.tracks_file = data["track_list"]

        self.random_tracks = None
        self.track_map = None
        self.load_tracks()
        if len(self.random_tracks) == 0:
            logger.warning("No random tracks specified")
        if len(self.track_map) == 0:
            logger.warning("No user tracks specified")

        # Initialise discord client
        discord.Client.__init__(self)


    def get_token(self):
        '''
        Return token from config
        TODO: Find a more elegant way to read & pass the token to the client
        '''
        return self.token


    def _read_json(self, file):
        '''
        Generic read json file
        '''
        with open(file, "r") as read_file:
            return json.load(read_file)


    def load_tracks(self):
        '''
        Load track information from specified file
        '''
        logger.info("Loading Track List:")
        data = self._read_json(self.tracks_file)
        self.track_map = data["tracks"]
        self.random_tracks = data["random"]
        self.print_tracks()


    def print_tracks(self):
        '''
        Print linked tracks to console
        '''
        for user, track in self.track_map.items():
            print(f"\t{user:16}- {track}")
        print("\n\tRandom Tracks:")
        for track in self.random_tracks:
            print(f"\t{' '*16}- {track}")


    async def on_ready(self):
        '''
        Setup connection to server
        '''
        logger.info("Running on_ready")

        # Check indended guild has been joined
        for guild in self.guilds:
            if guild.name == self.guild_name:
                self.guild = guild
                break

        print(
            f'{self.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )

        # Save pointers to useful channels
        for channel in guild.channels:
            if channel.name == "General":
                self.primary_voice_channel = await channel.connect()
            if channel.name == "bot-testing":
                self.primary_text_channel = channel

        # Check channels succesfully connected
        if self.primary_voice_channel == None:
            logging.error("No voice channel has been joined.")
        if self.primary_text_channel == None:
            logging.error("No text channel has been joined.")


    async def on_message(self, message):
        '''
        Commands to do on message
        '''
        if message.author == self.user:
            return

        # Reload Track Information
        if message.content.startswith('!reload'):
            self.load_tracks()
            await message.channel.send('Reloaded track data')


    async def on_voice_state_update(self, member, before, after):
        '''
        Do stuff on voice state change
        '''
        if member == self.user:
            return

        if before.channel is None and after.channel is not None:
            logger.info(f"Detected {member.name} joining {after.channel.name}")

            if self.primary_voice_channel != None:
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
                    self.primary_voice_channel.play(discord.FFmpegPCMAudio(f"tracks/{track}"))
                    self.primary_voice_channel.source = discord.PCMVolumeTransformer(self.primary_voice_channel.source, volume=0.6)
                except discord.errors.ClientException:
                    logger.info(f"{member.name} joined but already playing audio.")
