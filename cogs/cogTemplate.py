import discord
from discord.ext import commands


class cogTemplate(commands.Cog):

    def __init__(self, client):
        self.client = client

    # @commands.command() Instead of @client.command()
    # @commands.Cog.listener() Instead of @client.event

    @commands.command()
    async def test(self, ctx):
        print(f'{ctx.channel}')
        print(f'{ctx.channel.overwrites_for(ctx.message.author)}')

def setup(client):
    client.add_cog(cogTemplate(client))
