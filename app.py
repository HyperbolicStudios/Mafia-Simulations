import discord
import asyncio
import math
from discord.ext import tasks, commands
import datetime
import traceback
from replit import db
from keep_alive import keep_alive
#OS/Directory
import os

import random
TOKEN = "TOKEN GOES HERE"

helpPage = ""
#keep_alive()
client = discord.Client()

async def updateStatus(status):
    game = discord.Game(status)
    await client.change_presence(status=discord.Status.online, activity=game)

async def sendHelpMessage(message):
    embed = discord.Embed()
    embed.color = 0x46848c
    channel_id = "#votecounts"
    for channel in message.guild.channels:
      if(channel.name == "server-functionality"):
        channel_id = str(channel.id)
    embed.description = helpPage.format(channel_id = channel_id)
    await message.channel.send("**Comms Bot Help:**")
    await message.channel.send(embed=embed)

async def embed_text(channel,text):
  embed = discord.Embed()
  embed.color = 0x46848c
  embed.description = text
  await channel.send(embed=embed)

async def checkForData():
    await client.wait_until_ready()
    while not client.is_closed():
        await asyncio.sleep(2)

def getChannelByName(guilds,name):
  for guild in guilds:
    for channel in guild.channels:
        if(channel.name) == name:
            return channel

def getRoleByName(guild,name):
  for role in guild.roles:
    if(role.name == name):
      return(role)
  return(0)

def senderNotMod(message):
    roles = message.author.roles
    for role in roles:
        if role.name == "Mod":
            return(False)
    return(True)

@client.event
async def on_ready():
    keep_alive()
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)

    # LIST_OF_CHANNELS = []
    global guilds
    guilds = client.guilds
    global verify_channel
    global server_management_channel
    global medium_channel
    global dead_channel
    global chess_champion_channel
    global chess_challenger_channel
    global jailor_channel
    global cell_channel

    verify_channel = getChannelByName(guilds,"verify")
    medium_channel = getChannelByName(guilds,"medium")
    dead_channel = getChannelByName(guilds,"dead-chat-unspoiled")

    chess_champion_channel = getChannelByName(guilds,"champion")
    chess_challenger_channel = getChannelByName(guilds,"challenger")

    jailor_channel = getChannelByName(guilds, "jailor")
    cell_channel= getChannelByName(guilds, "cell")

    server_management_channel = getChannelByName(guilds, "server-functionality")
    await updateStatus("$commsbot help")
    await client.change_presence(status=discord.Status.online)


@client.event
async def on_message(message):
    if(message.author.id != client.user.id):
#COMMUNICATION MANAGEMENT - MOD MESSAGES IGNORED:
        #if(senderNotMod(message)):
            #Medium communication
            if(message.channel.id == medium_channel.id):
                await dead_channel.send("**Medium:** " + message.content)
            if(message.channel.id == dead_channel.id):
                await medium_channel.send("**Spirits: **" + message.content)

            #Chess player communication
            if(message.channel.id == chess_champion_channel.id):
                await chess_challenger_channel.send("**Champion: **" + message.content)
            if(message.channel.id == chess_challenger_channel.id):
                await chess_champion_channel.send("**Challenger: **" + message.content)

            #Cell-Jailor Communication
            if(message.channel.id == jailor_channel.id):
                await cell_channel.send("**Jailor: **" + message.content)
            if(message.channel.id == cell_channel.id):
                await jailor_channel.send("**{}: **{}".format(message.author.name,message.content))
    #MOD ONLY commands
    if(senderNotMod(message) == False):
        if message.content == "$clear channel":
            await message.channel.purge()
            await message.channel.send("Wiped messages!")

      #VERIFICATION

        #generate codes
        if message.content == "$generate codes" and message.channel.id == server_management_channel.id:
          codes = {}
          for role in message.channel.guild.roles:
            codes.update({random.randint(1000,9000):role.name})
          db["codes"] = codes
          text = "**Verification Codes:\n"
          for role in codes.keys():
            text = text+"`{}`: {}\n".format(role,codes[role])
          await embed_text(message.channel,text)

        #print codes
        if message.content == "$print codes" and message.channel.id == server_management_channel.id:
          codes = db["codes"]
          text = "**Verification Codes:\n"
          for role in codes.keys():
            text = text+"`{}`: {}\n".format(role,codes[role])
          await embed_text(message.channel,text)

    #VERIFICATION CHANNEL - OPEN TO USERS
    if message.content.find("$verify ") == 0 and message.channel.name =="verify":
    #  try:
        code = message.content[7:].strip()
        role_name = db["codes"][code]
        print(role_name)

        await message.author.add_roles(getRoleByName(message.channel.guild,role_name))
        await message.author.add_roles(getRoleByName(message.channel.guild,"Verified"))
        await message.channel.purge()
        await server_management_channel.send("<@&{}> Notification: Added user **{}** to role **{}**.".format(getRoleByName(message.channel.guild,"Mod").id,message.author,role_name))

      #except:
       # await message.channel.send("Could not find role with code '{}'.".format(code))

#ANONYMOUS MASON CHAT
    mason_channels = {"A":["p1","p2","p3"],"B":["p4","p5","p6"]}
    if message.content[:2] == "-m":
        print("msg received")
        channel = message.channel.name
        for category in mason_channels.keys():
          if channel in mason_channels[category]:
              for other_channel in mason_channels[category]:
                  if other_channel != channel:
                      await getChannelByName(guilds,other_channel).send(message.content[2:])


client.loop.create_task(checkForData())
client.run(TOKEN)
