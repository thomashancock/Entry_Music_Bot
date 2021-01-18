# bot.py
import os
import logging

import discord

from Settings import DISCORD_TOKEN, DISCORD_GUILD, TRACK_MAP
TOKEN = DISCORD_TOKEN
GUILD = DISCORD_GUILD


class MyClient(discord.Client):

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
        if message.content.startswith('!iron'):
            await message.channel.send(file=discord.File('Ironing.gif'))


    async def on_voice_state_update(self, member, before, after):
        '''
        Do stuff on voice state change
        '''
        if member == self.user:
            return

        if before.channel is None and after.channel is not None:
            # if self.general_text_channel != None:
                # await self.general_text_channel.send(f"{member} joined voice chat!")

            if self.vc != None:
                try:
                    if member.name in TRACK_MAP:
                        self.vc.play(discord.FFmpegPCMAudio(TRACK_MAP[member.name]))
                    else:
                        self.vc.play(discord.FFmpegPCMAudio('tracks/Zelda_Chest_Open.mp3'))
                        if self.general_text_channel != None:
                            await self.general_text_channel.send(f"{self.name} noticed {member} doesn't have personalised entry music. Suggest something!")
                    self.vc.source = discord.PCMVolumeTransformer(self.vc.source, volume=0.3)
                except discord.errors.ClientException:
                    print("User joined but already playing audio.")


client = MyClient()
client.run(TOKEN)

# @atexit.register
# def goodbye():
#     print("Script quit. Disconnecting client...", end="")
#     client.disconnect()
#     print("Done")
