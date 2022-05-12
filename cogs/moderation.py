import discord
from discord.ext import commands


# This is automod rules. All of them.
def checkIfRuleBroke(self, message):
    if 'shit' in message.content.lower():
        return 1
    else:
        return 0


muteRoleID = 828379552224509973


class moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    # @commands.command() Instead of @client.command()
    # @commands.Cog.listener() Instead of @client.event

    # Punishments are: note, blacklist, watch, warn, mute, kick, ban

    # Noted, Un-Noted, Blacklisted, Un-Blacklisted, Watched, Un-Watched, Warned, Un-Warned, Muted, Un-Muted, Kicked, Un-Kicked, Banned, Un-Banned

    # Moderator may be none if the moderator wishes to stay anonymous.
    # Time may be none if punishment doesn't expire
    # Message will be none unless it is automod
    # Member, punishment, and reason are all required

    async def buildPunishEmbed(self, member, punishment, reason, moderator, time, message):
        if member is None or punishment is None or reason is None:
            print("Missing Args")
            return
        iconURL = ""
        if punishment == 'Noted' or punishment == "Un-Noted":
            iconURL = "https://cdn.icon-icons.com/icons2/39/PNG/128/editnote_pencil_edi_6175.png"
        elif punishment == 'Blacklisted' or punishment == "Un-Blacklisted":
            iconURL = "https://cdn.icon-icons.com/icons2/569/PNG/512/list-document-black-interface-symbol_cdn.icon-icons.com_54502.png"
        elif punishment == 'Watched' or punishment == "Un-Watched":
            iconURL = "https://cdn.icon-icons.com/icons2/1465/PNG/512/396eyes_100600.png"
        elif punishment == 'Warned' or punishment == "Un-Warned":
            iconURL = "https://cdn.icon-icons.com/icons2/81/PNG/256/exclamation_warning_15590.png"
        elif punishment == 'Muted' or punishment == "Un-Muted":
            iconURL = "https://cdn.icon-icons.com/icons2/1933/PNG/512/iconfinder-volume-mute-sound-speaker-audio-4593175_122269.png"
        elif punishment == 'Kicked' or punishment == "Un-Kicked":
            iconURL = "https://cdn.icon-icons.com/icons2/564/PNG/512/Action_2_icon-icons.com_54220.png"
        elif punishment == 'Banned' or punishment == "Un-Banned":
            iconURL = "https://cdn.icon-icons.com/icons2/2621/PNG/512/tools_hammer_icon_156946.png"
        else:
            print("Invalid punishment")
            return

        embedVar = discord.Embed(title=f'You have been {punishment}', color=16714507)
        embedVar.set_author(name=f'{punishment}', icon_url=f'{iconURL}')
        embedVar.add_field(name="Reason:", value=f'{reason}', inline=False)
        if moderator is not None:
            embedVar.add_field(name="Moderator:", value=f'{moderator.name}', inline=False)
        if time is not None:
            embedVar.add_field(name="Expires at:", value=f'{time}')
        else:
            embedVar.add_field(name="Expires at:", value=f'Never')
        if message is not None:
            try:
                embedVar.add_field(name="Offending message:", value=f'{message.content}')
            except:
                pass

        embedVar.set_footer(text=f'Do NOT message any staff on the server to get this punishment appealed.This will result in a permanent ban\nYou may email ops@hackucf.org to appeal this punishment')
        await member.send(embed=embedVar)

    # Only should run if channel doesn't have mute override already
    async def setupMute(self, guild):
        allChannels = guild.channels
        muteRole = guild.get_role(muteRoleID)
        for channel in allChannels:
            await channel.set_permissions(muteRole, add_reactions=False,
                                          send_messages=False,
                                          speak=False,
                                          stream=False,
                                          request_to_speak=False,
                                          use_slash_commands=False,
                                          create_instant_invite=False,
                                          change_nickname=False,
                                          use_voice_activation=False)

    @commands.command(aliases=['purge'])
    @commands.has_any_role(558818974230511672, 558818939082375199)
    async def clear(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount)
        await ctx.send(f'{amount} messages purged')

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f'{member} kicked')

    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f'{member} banned')

    @commands.command()
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        muteRole = member.guild.get_role(muteRoleID)
        roles = [10]
        roles[0] = muteRoleID
        print(muteRole.id)
        await self.setupMute(member.guild)
        print("Passed A")
        await self.buildPunishEmbed(member, "Muted", reason, ctx.message.author, None, None)
        print("Passed B")
        await member.add_roles(muteRole, reason=reason, atomic=True)
        print("Passed C")

    @commands.command()
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'{user.mention} unbanned')
                return
        await ctx.send(f'Specified user wasn\'t found to be banned')

    # automod
    # Noted, Un-Noted, Blacklisted, Un-Blacklisted, Watched, Un-Watched, Warned, Un-Warned, Muted, Un-Muted, Kicked, Un-Kicked, Banned, Un-Banned
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            if checkIfRuleBroke(self, message) == 1:
                await message.delete()
                await message.channel.send("You Broke Rule")
                await message.author.send("Y U Break Rules?")
                await self.buildPunishEmbed(message.author, "Muted", "Automod: No saying \"shit\"", None, None, message)

    # For punish role enformcement.
    # Needs to check if member is currently punished first
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            beforeHasMute = 0
            for role in before.roles:
                if role.id == muteRoleID:
                    beforeHasMute = 1
                    break
            if beforeHasMute == 1:
                await after.add_roles(after.guild.get_role(muteRoleID), reason="Mute Evasion", atomic=True)

def setup(client):
    client.add_cog(moderation(client))
