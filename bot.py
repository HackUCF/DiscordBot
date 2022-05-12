import discord
import os
import json
from discord.ext import commands
from discord.ext import tasks
from itertools import cycle

intents = discord.Intents().all()

client = commands.Bot(command_prefix='.', intents=intents, max_messages=1000000)
status = cycle(['Check out the source code on GitHub', 'Meetings Fridays at 5:30PM', 'Come to ops meetings Tuesdays at 8:30PM', 'Have a great Day!'])

@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')


@client.event
async def on_command_error(ctx, error):
    await ctx.send(error)


@client.event
async def on_ready():
    change_status.start()
    print('Bot is ready.')


@tasks.loop(seconds=10)
async def change_status():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(next(status)))

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

json_file = open("auth.json")

variables = json.load(json_file)

json_file.close()

client.run(variables["client"])
