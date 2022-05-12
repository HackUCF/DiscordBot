import discord
import random
from discord.ext import commands


class games(commands.Cog):

    def __init__(self, client):
        self.client = client

    # @commands.command() Instead of @client.command()
    # @commands.Cog.listener() Instead of @client.event

    @commands.command()
    async def ping(self, ctx):
       await ctx.send(f'Pong! {round(self.client.latency * 1000)}ms')


    @commands.command(aliases=['8ball'])
    async def _8ball(self, ctx, *, question):
       responses = ['No',
                    'Yes']
       await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

def setup(client):
    client.add_cog(games(client))
