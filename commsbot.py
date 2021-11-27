import discord
import asyncio
import math
from discord.ext import tasks, commands
import datetime
import traceback

#OS/Directory
import os

TOKEN = "ODc2OTgxMTg0MTEzMDQ5NjEx.YRr-Xw.H9j7jx6Xx57JiP5e9UysJfuluiw"

helpPage = ""

client = discord.Client()

async def updateStatus(status):
    game = discord.Game(status)
    await client.change_presence(status=discord.Status.online, activity=game)

async def sendHelpMessage(message):
    embed = discord.Embed()
    embed.color = 0x46848c
    channel_id = "#votecounts"
    for channel in message.guild.channels:
      if(channel.name == "votecount-game-"+getToken("name")[0].lower()):
        channel_id = str(channel.id)
    embed.description = helpPage.format(channel_id = channel_id)
    await message.channel.send("**Votecount Bot " + getToken("name") + " help:**")
    await message.channel.send(embed=embed)

async def checkForData():
    await client.wait_until_ready()
    while not client.is_closed():
        await asyncio.sleep(2)

def searchChannelByName(guilds,name):
    for guild in guilds:
        for channel in guild.channels:
            if(channel.name) == name:
                return channel

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)

    # LIST_OF_CHANNELS = []
    guilds = client.guilds
    global verify_channel
    global medium_channel
    global deadchatunspoiled_channel
    verify_channel = searchChannelByName(guilds,"verify")
    medium_channel = searchChannelByName(guilds,"medium")
    deadchatunspoiled_channel = searchChannelByName(guilds,"dead-chat-unspoiled")

    await updateStatus("$commbot help")
    await client.change_presence(status=discord.Status.online)


@client.event
async def on_message(message):
    if(message.author.id != client.user.id):
        #Medium communication
        if(message.channel.id == medium_channel.id):
            await deadchatunspoiled_channel.send("**Medium:** " + message.content)
        if(message.channel.id == deadchatunspoiled_channel.id):
            await medium_channel.send("**Spirits: **" + message.content)

client.loop.create_task(checkForData())
client.run(TOKEN)
