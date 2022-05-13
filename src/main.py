import dotenv
import math
import sys
import datetime
import time
from time import sleep
import re
import yaml
import pathlib
import json
import asyncio
import yaml
import random
import traceback

import atexit

from nextcord.types import activity
import nextcord.client
import nextcord.abc
import nextcord.types.activity
import nextcord.ext.commands
from nextcord.abc import Snowflake
from nextcord.ext import commands
import nextcord.abc

from colorama import Fore, Back, Style

from version import *

from utils import *

from exception import AuthenticationException

save = {}

async def addCoins(member, amount):
    if not 'users' in save:
        save['users'] = {}
    if not member.id in save['users']:
        save['users'][member.id] = {}
    if not 'coins' in save['users'][member.id]:
        save['users'][member.id]['coins'] = 0
    save['users'][member.id]["coins"] += amount

    # Save it
    with open('save.yaml', 'w') as outfile:
        yaml.dump(save, outfile)    

def saveData():
    with open('save.yaml', 'w') as outfile:
        yaml.dump(save, outfile)

def loadData():
    global save
    with open('save.yaml', 'r') as infile:
        save = yaml.load(infile, Loader=yaml.FullLoader)

# Open file save.yaml and load it into the save variable
try:
    with open('save.yaml', 'r') as f:
        save = yaml.load(f, Loader=yaml.FullLoader)
except FileNotFoundError:
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Could not find save.yaml. Creating it now.")
    with open('save.yaml', 'w') as f:
        yaml.dump(save, f)
intents = nextcord.Intents.all()

LOG = False
coinName = "Karpcoins"

autoResponses = {}

version = Version(major=1, minor=2, patch=0)

bot = commands.Bot(command_prefix=["!", "\\!", "$", "\\$"], intents=intents, owner_ids=[941433256010727484])


@bot.command(
    aliases=["getping"],help="""
Tells you the ping of the bot
Usage:
 - `ping`
""" 
)
async def ping(ctx: commands.context.Context):
    await ctx.send("Pong!\nLatency is " + str(math.floor(bot.latency * 1000) / 1000) + " seconds")

@bot.command(aliases=["version"], help="""
Gets the bots about page
Usage:
 - `about`
""" )
async def about(ctx: commands.context.Context):
    embed = nextcord.Embed(title = f"About KarpeBot", description = f"""
**KarpeBot version {version}**
Running on {getOSVersion()}
Python {getPythonVersion()}
Nextcord {getNextcordVersion()}
    """,
    color = nextcord.Colour(0x0088FF)
    )
    embed.set_footer(text = "Requested by " + ctx.author.name, icon_url = ctx.author.avatar.url)
    
    #embed.set_image(url=f"{bot.user.display_avatar.url}?size=64")
    
    await ctx.send( embed=embed )

@bot.command(aliases=["codeformat"], help="""
Tells you how to format code
Usage:
 - `format`
""",
 )
async def format(ctx: commands.context.Context):
    embed = nextcord.Embed(title = f"How to format code", description = """
Use
\\`\\`\\`<language>

\\`\\`\\`
this will result in
```
print("Hello world!")
```
add syntax highlighting by replacing <language> with for example, for python:
`python`
```python
print("Hello world!")
```
this was achieved by typing
\\`\\`\\`python
print("Hello world!")
\\`\\`\\`
    """
    ,
    color = nextcord.Colour(0x0088FF)
    )

    embed.set_footer(text = "Requested by " + ctx.author.name, icon_url = ctx.author.avatar.url)
    
    await ctx.send( embed=embed )

@bot.command(aliases=[], help="""
Gets the bots prefix
Usage:
 - `about`
""" )
async def prefix(ctx: commands.context.Context):
    prefixarr = [] + bot.command_prefix
    try:
        prefixarr.pop(prefixarr.index(bot.user.mention.replace('@', '@!')))
    except:
        prefixarr
    try:
        prefixarr.pop(prefixarr.index(bot.user.mention.replace('@', '@!') + " "))
    except:
        prefixarr
    embed = nextcord.Embed(title = f"{bot.user.name}'s prefixes", description = """
```
{0}
```
    """.format (
        "\n".join(prefixarr)
    ),
    color = nextcord.Colour(0x0088FF)
    )

    if len(bot.command_prefix) == 1:
        embed.title = f"{bot.user.name}'s prefix"
    
    #embed.set_image(url=f"{bot.user.display_avatar.url}?size=64")
    
    await ctx.send( embed=embed )

# create a kick command that kicks the specified user
@bot.command( aliases=[], help="""
Kicks the specified user
Usage:
    - `kick @user <reason>`
""")
async def kick(ctx: commands.context.Context, member: commands.MemberConverter, *, reason: str = "No reason specified"):
    #if member is invalid, return and give an error
    if not member:
        await ctx.send("Invalid user")
        return
    if member.guild != ctx.guild:
        return
    if ctx.author.top_role.position <= member.top_role.position:
        await ctx.send("You cannot kick this user")
        return

    #prevent the bot from kicking itself
    if member.id == bot.user.id:
        await ctx.send("I cannot kick myself")
        return

    if not ctx.author.guild_permissions.kick_members:
        return

    if not member.bot:
        embed = nextcord.Embed(title = f"You have been kicked from {ctx.guild.name}", description = "Reason:```\n{reason}```", color = nextcord.Colour(0x0088FF))
        await member.send(embed=embed)

    await member.kick(reason=reason)

    embed = nextcord.Embed(title = f"{member.name} has been kicked", description = """
User {0} has been kicked
Reason:
```
{1}
```
""".format(
    member.mention,
    reason
    ), color=nextcord.Colour(0x0088FF))
    await ctx.send(embed=embed)

@bot.command( aliases=[], help="""
Bans the specified user
Usage:
    - `ban @user <reason>`
    - `ban <user id> <reason>`
""")
async def ban(ctx: commands.context.Context, member: commands.MemberConverter = None, *, reason: str = "No reason specified"):
    member: nextcord.member = member
    #if member is invalid, return and give an error
    if not member:
        embed = nextcord.Embed(title = f"Invalid user", description = "Please specify a valid user", color = nextcord.Colour(0xFF0000))
        await ctx.send(embed=embed)
        return
    if member.guild != ctx.guild:
        return
    
    # If user is not a mod or higher, return
    if not ctx.author.guild_permissions.ban_members:
        embed = nextcord.Embed(title = f"You do not have permission to ban this user", description = "You must be a mod or higher to ban this user\nOr have the permission to ban members", color = nextcord.Colour(0xFF0000))
        await ctx.send(embed=embed)
        return

    # do we have a higher role than the user?
    if ctx.author.top_role.position <= member.top_role.position:
        embed = nextcord.Embed(title = f"You do not have permission to ban this user", description = "You need to have a higher role than the user to ban them", color = nextcord.Colour(0xFF0000))
        await ctx.send(embed=embed)
        return

    #prevent the bot from banning itself
    if member.id == bot.user.id:
        await ctx.send("I cannot ban myself")
        return

    if not member.bot:
        embed = nextcord.Embed(title = f"You have been banned from {ctx.guild.name}", description = "Reason:```\n{reason}```", color = nextcord.Colour(0x0088FF))
        await member.send(embed=embed)

    await member.ban(reason=reason)
    
    embed = nextcord.Embed(title = f"{member.name} has been banned", description = """
User {0} has been banned
Reason:
```
{1}
```
""".format(
    member.mention,
    reason
    ), color=nextcord.Colour(0x0088FF))
    await ctx.send(embed=embed)

# Klck command (fake kick)

@bot.command( aliases=['k¡ck'], help="""
Kicks the specified user
Usage:
    - `klck @user <reason>`
""")
async def klck(ctx: commands.context.Context, member: commands.MemberConverter, *, reason: str = "No reason specified"):
    #if member is invalid, return and give an error
    if not member:
        await ctx.send("Invalid user")
        return
    if member.guild != ctx.guild:
        return
    if ctx.author.top_role.position <= member.top_role.position:
        await ctx.send("You cannot kick this user")
        return

    #prevent the bot from kicking itself
    if member.id == bot.user.id:
        await ctx.send("I cannot kick myself")
        return

    if not ctx.author.guild_permissions.kick_members:
        return

    if not member.bot:
        embed = nextcord.Embed(title = f"You have been kicked from {ctx.guild.name}", description = "Reason:```\n{reason}```", color = nextcord.Colour(0x0088FF))
        await member.send(embed=embed)

    embed = nextcord.Embed(title = f"{member.name} has been kicked", description = """
User {0} has been kicked
Reason:
```
{1}
```
""".format(
    member.mention,
    reason
    ), color=nextcord.Colour(0x0088FF))
    await ctx.send(embed=embed)

@bot.command( aliases=[], help="""
Bans the specified user
Usage:
    - `bon @user <reason>`
    - `bon <user id> <reason>`
""")
async def bon(ctx: commands.context.Context, member: commands.MemberConverter = None, *, reason: str = "No reason specified"):
    member: nextcord.member = member
    #if member is invalid, return and give an error
    if not member:
        embed = nextcord.Embed(title = f"Invalid user", description = "Please specify a valid user", color = nextcord.Colour(0xFF0000))
        await ctx.send(embed=embed)
        return
    if member.guild != ctx.guild:
        return
    
    # If user is not a mod or higher, return
    if not ctx.author.guild_permissions.ban_members:
        embed = nextcord.Embed(title = f"You do not have permission to ban this user", description = "You must be a mod or higher to ban this user\nOr have the permission to ban members", color = nextcord.Colour(0xFF0000))
        await ctx.send(embed=embed)
        return

    # do we have a higher role than the user?
    if ctx.author.top_role.position <= member.top_role.position:
        embed = nextcord.Embed(title = f"You do not have permission to ban this user", description = "You need to have a higher role than the user to ban them", color = nextcord.Colour(0xFF0000))
        await ctx.send(embed=embed)
        return

    #prevent the bot from banning itself
    if member.id == bot.user.id:
        await ctx.send("I cannot ban myself")
        return

    if not member.bot:
        embed = nextcord.Embed(title = f"You have been banned from {ctx.guild.name}", description = "Reason:```\n{reason}```", color = nextcord.Colour(0x0088FF))
        await member.send(embed=embed)
    
    embed = nextcord.Embed(title = f"{member.name} has been banned", description = """
User {0} has been banned
Reason:
```
{1}
```
""".format(
        member.mention,
        reason
    ), color=nextcord.Colour(0x0088FF))
    await ctx.send(embed=embed)

@bot.command( aliases=[], help="""
Bans the specified user
Usage:
    - `unban @user`
    - `unban <user id>`
""")
async def unban(ctx: commands.context.Context, member: commands.MemberConverter, *, reason: str = "No reason specified"):
    #if member is invalid, return and give an error
    if not member:
        await ctx.send("Invalid user")
        return
    if member.guild != ctx.guild:
        return
    # do we have a higher role than the user?
    if ctx.author.top_role.position <= member.top_role.position:
        await ctx.send("You cannot ban this user")
        return

    #prevent the bot from banning itself
    if member.id == bot.user.id:
        await ctx.send("I cannot ban myself")
        return

    if not ctx.author.guild_permissions.ban_members:
        return

    await member.unban(reason=reason)
    
    embed = nextcord.Embed(title = f"{member.name} has been unbanned", description = """
User {0} has been banned
Reason:
```
{1}
```
""".format(
    member.mention,
    reason
    ), color=nextcord.Colour(0x0088FF))
    await ctx.send(embed=embed)

#Command that deletes all messages in the specified channel
@bot.command(aliases=[], help="""
Deletes all messages in the specified channel
Usage:
    - `purge <amount>`
    - `purge <amount> <channel>`
    - `purge <amount> <channel> <user>`
""")
async def purge(ctx: commands.context.Context, amount: int, channel: nextcord.TextChannel = None, user: commands.MemberConverter = None):
    if not channel:
        channel = ctx.channel
    
    if amount > 1000:
        await ctx.send("You cannot delete more than 100 messages")
        return
    if amount < 1:
        await ctx.send("You cannot delete less than 1 message")
        return
    if not ctx.author.guild_permissions.manage_messages:
        return

    deleted = 0
    if user == None:
        await ctx.channel.purge(limit=amount, oldest_first=False)
        deleted = amount
    else:
        async for message in channel.history(limit=amount):
            if message.author == user:
                await message.delete()
                deleted += 1
    await ctx.send(f"Deleted {deleted} messages", delete_after=5)

# Command to get the bot's uptime
@bot.command(aliases=[], help="""
Gets the bots uptime
Usage:
    - `uptime`
""")
async def uptime(ctx: commands.context.Context):
    currentTime = time.time()
    difference = currentTime - startTime

    # Change differences precision to seconds
    difference = round(difference, 0)

    # Format difference to a readable string in python 3
    difference = str(datetime.timedelta(seconds=difference))

    await ctx.send(f"Uptime: {difference}")

# Command to get server rules
@bot.command(aliases=[], help="""
Gets the server's rules
Usage:
    - `rules`
""")
async def rules(ctx: commands.context.Context):
    ruleschannel = ctx.guild.rules_channel
    # Get oldest message in rules channel
    message = await ruleschannel.history(limit=1, oldest_first=True).flatten()
    rules = message[0].content.replace("@everyone", "")
    # Create a new embed with the rules
    embed = nextcord.Embed(title = f"{ctx.guild.name}'s rules", description = rules, color = nextcord.Colour(0x0088FF))
    await ctx.send(embed=embed)

# Thanks command
@bot.command(aliases=[], help="""
Thanks the specified user
Usage:
    - `thanks @user`
    - `thanks <user id>`
""")
async def thanks(ctx: commands.context.Context, member: commands.MemberConverter):
    if not member:
        await ctx.send("Invalid user")
        return
    if member.guild != ctx.guild:
        return
    if member.id == bot.user.id:
        await ctx.send("I cannot thank myself")
        return
    if member.id == ctx.author.id:
        await ctx.send("You cannot thank yourself")
        return
    #if ctx.author.top_role.position <= member.top_role.position:
    #    await ctx.send("You cannot thank this user")
    #    return
    if not ctx.author.guild_permissions.manage_messages:
        return
    embed = nextcord.Embed(title = f"{ctx.author.name} has thanked {member.name}", description = "", color = nextcord.Colour(0x0088FF))
    await ctx.send(embed=embed)

@bot.command(aliases=[], help="""
Sends a message to all members of the server that it was sent in
Usage:
    - `botsend <message>`
""")
async def botsend(ctx: commands.context.Context, *, message: str):
    # check if the user is the owner of the bot, if it isn't, return
    if not ctx.author.id in bot.owner_ids:
        return
    embed = nextcord.Embed(title = f"Message from {ctx.guild.name}", description = message, color = nextcord.Colour(0x0088FF))
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed.set_footer(text=f"If this is being spammed, please leave the server this message originated from or contact the bot owner (<@{bot.owner_ids[0]}>)")
    for member in ctx.guild.members:
        try:
            await member.send(embed=embed)
        except:
            pass

# Karpe command
@bot.command(aliases=[], help="""
Karpe the specified user
Usage:
    - `karpe @user`
    - `karpe <user id>`
""")
async def karpe(ctx: commands.context.Context, member: commands.MemberConverter):
    if not member:
        await ctx.send("Invalid user")
        return
    if member.guild != ctx.guild:
        return
    if member.id == bot.user.id:
        await ctx.send("I cannot karpe myself")
        return
    name = member.name
    if member.nick:
        name = member.nick

    name = re.escape(name)
    name = name.replace("\\ ", " ")
    name = name.replace("_", r"\_")
    await ctx.send(f"{name} has been karpe")

@bot.command(aliases=['addcash', 'addmoney'], help="""
Adds coins to the specified user
Usage:
    - `addcoins @user <amount>`
    - `addcoins <user id> <amount>`
""")
async def addcoins(ctx: commands.context.Context, member: commands.MemberConverter, amount: int):
    if not member:
        await ctx.send("Invalid user")
        return
    if member.guild != ctx.guild:
        return
    if not member.id:
        await ctx.send("Invalid user")
        return
    if member.id == bot.user.id:
        await ctx.send("I cannot add coins to myself")
        return
    if not ctx.author.guild_permissions.administrator:
        return

    await addCoins(member, amount)
    await ctx.send(f"Added {amount} {coinName} to {member.name}\nThey now have {save['users'][member.id]['coins']} {coinName}")

# Command to remove coins from a user
@bot.command(aliases=['removecash', 'removemoney'], help="""
Removes coins from the specified user
Usage:
    - `removecoins @user <amount>`
    - `removecoins <user id> <amount>`
""")
async def removecoins(ctx: commands.context.Context, member: commands.MemberConverter, amount: int):
    if not member:
        await ctx.send("Invalid user")
        return
    if member.guild != ctx.guild:
        return
    if not member.id:
        await ctx.send("Invalid user")
        return
    if member.id == bot.user.id:
        await ctx.send("I cannot remove coins from myself")
        return
    # Only bot.owners can change coins
    if ctx.author.id in bot.owner_ids:
        pass
    else:
        await ctx.send("You do not have the permission `BOT.OWNER`")
        return

    await addCoins(member, -amount)
    await ctx.send(f"Removed {amount} {coinName} from {member.name}\nThey now have {save['users'][member.id]['coins']} {coinName}")

# Command to set the amount of coins a user has
@bot.command(aliases=['setcash', 'setmoney'], help="""
Sets the amount of coins a user has
Usage:
    - `setcoins @user <amount>`
    - `setcoins <user id> <amount>`
""")
async def setcoins(ctx: commands.context.Context, member: commands.MemberConverter, amount: int):
    if not member:
        await ctx.send("Invalid user")
        return
    if member.guild != ctx.guild:
        return
    if not member.id:
        await ctx.send("Invalid user")
        return
    if member.id == bot.user.id:
        await ctx.send("I cannot set coins for myself")
        return
    # Only bot.owners can change coins
    if ctx.author.id in bot.owner_ids:
        pass
    else:
        await ctx.send("You do not have the permission `BOT.OWNER`")
        return
    
    save['users'][member.id]['coins'] = amount
    await addCoins(member, 0)
    await ctx.send(f"Set {member.name}'s coins to {amount}")

# Balance command
@bot.command(aliases=['bal'], help="""
Gets the balance of the specified user
Usage:
    - `balance @user`
    - `balance <user id>`
""")
async def balance(ctx: commands.context.Context, member: commands.MemberConverter = None):
    if not member:
        member = ctx.author
    if not member.id:
        await ctx.send("Invalid user")
        return
    if member.guild != ctx.guild:
        return
    if member.id == bot.user.id:
        await ctx.send("I cannot get the balance of myself")
        return

    # Check if the user data exists
    if not member.id in save['users']:
        save['users'][member.id] = {}
        save['users'][member.id]['coins'] = 0
    
    if not 'coins' in save['users'][member.id]:
        save['users'][member.id]['coins'] = 0
    coins = save['users'][member.id]['coins']
    await ctx.send(f"{member.name} has {coins} {coinName}")

# Daily command
@bot.command(aliases=[], help="""
Gives you your daily coins
Usage:
    - `daily`
""")
async def daily(ctx: commands.context.Context):
    daily_coins = random.randint(50, 100)
    if not ctx.author.id in save['users']:
        save['users'][ctx.author.id] = {}
        save['users'][ctx.author.id]['coins'] = 0
    if not 'daily' in save['users'][ctx.author.id]:
        save['users'][ctx.author.id]['daily'] = 0
    # Check if the user hasn't claimed their daily coins in the last 24 hours
    if save['users'][ctx.author.id]['daily'] <= (time.time() - 86400):
        await addCoins(ctx.author, daily_coins)
        embed = nextcord.Embed(title = f"Daily coins", description = f"You have received {daily_coins} {coinName}", color = nextcord.Colour(0x0088FF))
        embed.set_footer(text=f"You can claim your daily coins again in 24 hours")
        await ctx.send(embed=embed)
        save['users'][ctx.author.id]['daily'] = time.time()
    else:
        embed = nextcord.Embed(title = f"Daily coins", description = f"You have already claimed your daily coins today", color = nextcord.Colour(0x0088FF))
        # Format the time left
        time_left = 86400 - (time.time() - save['users'][ctx.author.id]['daily'])
        hours = int(time_left / 3600)
        minutes = int((time_left % 3600) / 60)
        seconds = int(time_left % 60)
        embed.set_footer(text=f"You can claim your daily coins again in {hours}:{minutes}:{seconds}")
        await ctx.send(embed=embed)
    saveData()

# Leaderboard command
@bot.command(aliases=['baltop', 'top'], help="""
Gets the top 10 users with the most coins
Usage:
    - `leaderboard`
""")
async def leaderboard(ctx: commands.context.Context):
    loadingEmbed = nextcord.Embed(title = "Loading...", color = nextcord.Colour(0x0088FF), description = "Please wait whilst the leaderboard is being loaded")
    loadingMessage = await ctx.send(embed=loadingEmbed)
    # Get the top 10 users
    users = save['users']
    # Turn the users object into a list
    users = list(users.items())
    # Sort the list by the coins
    users.sort(key=lambda x: x[1]["coins"], reverse=True)

    # Create the embed
    embed = nextcord.Embed(title = f"Leaderboard (Top {min(10, users.__len__())} / {users.__len__()})", color = nextcord.Colour(0x0088FF))
    # Add the top 10 users
    for i, user in enumerate(users):
        # Make the memberName variable
        # Try getting the member name from every guild the bot is in
        memberName = None
        gotName = False
        for guild in bot.guilds:
            try:
                memberName = guild.get_member(user[0]).name + "#" + guild.get_member(user[0]).discriminator
                if user[0] in bot.owner_ids:
                    memberName = "`[Bot Owner]` " + memberName
            except:
                pass
        memberNameGuild = ctx.guild.get_member(user[0])
        if memberNameGuild:
            if user[0] == ctx.guild.owner_id:
                memberName = "`[Server Owner]` " + memberNameGuild.name + "#" + memberNameGuild.discriminator
            else:
                memberName = "`[Server]` " + memberNameGuild.name + "#" + memberNameGuild.discriminator
            if memberNameGuild.nick:
                memberName += " (" + memberName + ")"
            if user[0] in bot.owner_ids:
                memberName = "`[Bot Owner]` " + memberName
        if not memberName:
            memberName = user[0]
        if memberName == None:
            memberName = "Unknown"
        memberName = memberName.__str__().replace('_', '\\_')
        embed.add_field(name = f"{i + 1}. {memberName}", value=f"{user[1]['coins']} {coinName}", inline = False)
    await ctx.send(embed=embed)
    await loadingMessage.delete()

bot.remove_command("help") # Remove default help command

@bot.command( help="""
Gives help about commands,
Usage:
 - `help`
 - `help <commandname>`
""" )
async def help(ctx: commands.context.Context, commandname: str = ""):
    if commandname == "":
        helpstr = ""
        # Sort the commands alphabetically
        commands = sorted(bot.commands, key=lambda x: x.name)
        for command in commands:
            if command.name == "help":
                continue
            if len(command.aliases) != 0:
                helpstr += f" - **{command.name} ({' | '.join(command.aliases)})**\n"
            else:
                helpstr += f" - **{command.name}**\n"
        embed = nextcord.Embed(
            title = "Commands:",
            description = helpstr,
            color = nextcord.Colour(0x0088FF)
        )
        await ctx.send(embed=embed)
    else:
        helpcommand = None
        for command in bot.commands:
            if command.name == commandname:
                helpcommand = command
            else:
                for alias in command.aliases:
                    if alias == commandname:
                        helpcommand = command
        
        if helpcommand != None:
            embed = nextcord.Embed(
                title = f"Command {helpcommand.name}:",
                description = helpcommand.help,
                color = nextcord.Colour(0x0088FF)
            )

            embed._footer = helpcommand.parent

            print(helpcommand.module)
            #if embed.description == "None":
            #    embed.description = "This command has no help description"
            await ctx.send(embed=embed)
        else:
            embed = nextcord.Embed(
                title = f"Command not found",
                description = "This command doesn't exist, or you might have misspelled it",
                color = nextcord.Colour(0x0088FF)
            )
            await ctx.send(embed=embed)

startTime = time.time()

@bot.event
async def on_ready():
    print(Fore.CYAN + "Bot ready" + Fore.RESET)

    # Store the bot's uptime
    startTime = time.time()

    bot.command_prefix.append(bot.user.mention.replace('@', '@!') + " ")
    bot.command_prefix.append(bot.user.mention.replace('@', '@!'))

    presence = nextcord.Activity()
    presence.application_id = 945283628018057287
    presence.name = "Fish"
    presence.url = "https://example.org"
    presence.type = nextcord.ActivityType.watching
    presence.buttons = nextcord.types.activity.ActivityButton()

    await bot.change_presence(status=nextcord.Status.online, activity=presence)

    # Print that the bot is done initializing
    print(Fore.CYAN + "Bot initialized" + Fore.RESET)

    #await bot.get_guild(945283628018057287).get_channel(945283628018057290).send(embed=embed)

@bot.event
async def on_typing(channel: nextcord.abc.Messageable, user: nextcord.User, when: datetime):
    # print("User " + user.name + " started typing")
    return

# Variable for the last time someone sent a message
lastMessageTime = {}

@bot.event
async def on_message(message: nextcord.Message):
    if message.author.bot:
        return
    #   await message.channel.send(message.content[::-1])
    if message.author == bot.user:
        return
    
    # If they haven't chatted in the last 60 seconds, give them between 10 and 20 coins
    if message.author.id in lastMessageTime:
        if time.time() - lastMessageTime[message.author.id] >= 60 * 60 and random.randint(0, 100) <= 20:
            lastMessageTime[message.author.id] = time.time()
            coins = random.randint(1, 10)
            await addCoins(message.author, coins)
            nick = message.author.nick
            if nick == None:
                nick = message.author.name
            # await message.channel.send(f"{nick} has been given {coins} {coinName}")
    
    if LOG:
        print(f'{Fore.RED}#{message.channel.name} {Fore.YELLOW}"{message.guild.name}" {Fore.GREEN}{message.author.display_name}> {Fore.CYAN}{message.content}{Fore.RESET}'.replace("\n", "\\n"))
        if message.attachments.__len__() > 0:
            for attachment in message.attachments:
                print(f"{Fore.CYAN}{attachment.url}{Fore.RESET}", end=" ")
            print()

    
    for (key, value) in autoResponses.items():
        if key in message.content:
            await message.channel.send(value)
            break

    await bot.process_commands(message)

    return

# On message edit
@bot.event
async def on_message_edit(before: nextcord.Message, after: nextcord.Message):
    if before.author.bot:
        return
    if before.author == bot.user:
        return
    if before.content == after.content:
        return
    if LOG:
        print(f'{Fore.GREEN}EDIT Before: {Fore.RED}#{before.channel.name} {Fore.YELLOW}"{before.guild.name}" {Fore.GREEN}{before.author.display_name}> {Fore.CYAN}{before.content}{Fore.RESET}'.replace("\n", "\\n"))
        print(f'{Fore.GREEN}EDIT After: {Fore.RED}#{before.channel.name} {Fore.YELLOW}"{before.guild.name}" {Fore.GREEN}{before.author.display_name}> {Fore.CYAN}{after.content}{Fore.RESET}'.replace("\n", "\\n"))

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.errors.CommandNotFound):
        embed = nextcord.Embed(color=nextcord.Colour(0xFF0000), title="Command not found") #,  description=f"Command  not found")
        await ctx.send(embed=embed)
        return
    if isinstance(error, commands.errors.CommandInvokeError):
        if (isinstance(error.original, AuthenticationException)):
            embed = nextcord.Embed(color=nextcord.Colour(0xFF0000), title="Permission denied", description="You aren't allowed to do this") #,  description=f"Command  not found")
            await ctx.send(embed=embed)
            return
        else:
            embed = nextcord.Embed(color=nextcord.Colour(0xFF0000), title="An error occured", description=f"```py\n{str(error)}\n```")
            await ctx.send(embed=embed)
            return
    embed = nextcord.Embed(color=nextcord.Colour(0xFF0000), title="An error occured", description=f"```py\n{str(error)}\n```")
    await ctx.send(embed=embed)
    await ctx.message.add_reaction("⚠️")

@bot.event
async def on_webhooks_update(channel: nextcord.TextChannel):
    while(True):
        for item in bot.guilds:
            for item2 in (await item.webhooks()):
                await item2.delete(reason="Webhook prevention")
        time.sleep(5)
    return

# On close of application, close the bot
@atexit.register
async def close():
    print("Closing bot")
    await bot.close()

print(Fore.CYAN + "Bot starting" + Fore.RESET)

bot.run(dotenv.get_key(pathlib.Path(__file__).parent.joinpath("./.env"), "TOKEN"))
