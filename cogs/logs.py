import discord
from discord.ext import commands
from datetime import datetime
#from bot import checkIfRuleBroke
from cogs.moderation import checkIfRuleBroke

# Moderator Logs
modLogID = 827246800342745149
memberLogID = 827246948884283423
userLogID = 827246964453146665
userVoiceLogID = 827246989732610129
modVoiceLogID = 827247013472763914
assignedRoleLogID = 827247035949514802
messageLogID = 827247073656045639
sentMessageLogID = 827247088936157214
typingLogID = 827345082540621905
reactionLogID = 827247050470064181

# Administrator Logs
discordModerationLogID = 827246814616617006
channelLogID = 827247195790508062
modRoleLogID = 827247213829685259
restrictMessageLogID = 827247239088177212
restrictSentMessageLogID = 827247263607816212
restrictTypingLogID = 827345162429661216
restrictReactionLogID = 827262769786650625
serverLogID = 827247290329726986
otherLogID = 827247308902105150

# Roles to move to restrict message log
restrictRoles = [558818974230511672, 558818939082375199, 826547399429193739]


class logs(commands.Cog):

    def __init__(self, client):
        self.client = client

    # @commands.command() Instead of @client.command()
    # @commands.Cog.listener() Instead of @client.event

    def checkIfRestricted(self, roles):
        for role in roles:
            for restrict in restrictRoles:
                if role.id == restrict:
                    return 0

    # For initial creation of channel.
    # Will return array or arrays, for embed. Name and Value
    def getChannelPerms(self, perms):
        allPerms = ['add_reactions',
                    'administrator',
                    'attach_files',
                    'ban_members',
                    'change_nickname',
                    'connect',
                    'create_instant_invite',
                    'deafen_members',
                    'embed_links',
                    'external_emojis',
                    'kick_members',
                    'manage_channels',
                    'manage_emojis',
                    'manage_guild',
                    'manage_messages',
                    'manage_nicknames',
                    'manage_permissions',
                    'manage_roles',
                    'manage_webhooks',
                    'mention_everyone',
                    'move_members',
                    'mute_members',
                    'priority_speaker',
                    'read_message_history',
                    'read_messages',
                    'request_to_speak',
                    'send_messages',
                    'send_tts_messages',
                    'speak',
                    'stream',
                    'use_external_emojis',
                    'use_slash_commands',
                    'use_voice_activation',
                    'view_audit_log',
                    'view_channel',
                    'view_guild_insights']

        errors = 0
        j = 0
        nextPerm = [[None] * 2 for _ in range(len(perms))]
        for key in perms:
            i = 0
            nextPerm[j][0] = f'{key}'
            nextPerm[j][1] = ""
            for perm in perms[key].pair():
                for title in allPerms:
                    try:
                        if i == 0 and getattr(perm, title):
                            nextPerm[j][1] += f':white_check_mark: {title}\n'
                        elif i == 1 and getattr(perm, title):
                            nextPerm[j][1] += f':x: {title}\n'
                    except:
                        errors += 1
                i += 1
            j += 1
        return nextPerm

    # Split between #typing-log and #restrict-typing-log
    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        if not user.bot:
            logChannel = self.client.get_channel(typingLogID)
            result = self.checkIfRestricted(user.roles)
            if result == 0:
                logChannel = self.client.get_channel(restrictTypingLogID)
            embedVar = discord.Embed(title=f'User {user}', description=f'{user.mention} Has started typing in <#{channel.id}>.', color=2575039)
            embedVar.set_author(name="User typing", icon_url="https://cdn.icon-icons.com/icons2/933/PNG/512/keyboard-right-arrow-button-1_icon-icons.com_72690.png")
            embedVar.set_footer(text=f'Typing started at {when}')
            embedVar.set_thumbnail(url=f'{user.avatar_url}')
            await logChannel.send(embed=embedVar)

    # Split between #sent-message-log #restrict-sent-message-log
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            logChannel = self.client.get_channel(sentMessageLogID)
            result = self.checkIfRestricted(message.author.roles)
            if result == 0:
                logChannel = self.client.get_channel(restrictSentMessageLogID)
            embedVar = discord.Embed(title=f'User {message.author}', description=f'{message.author.mention} Sent a message in channel <#{message.channel.id}>. {message.jump_url}', color=65302)
            embedVar.set_author(name="Message Sent", icon_url="https://icon-icons.com/downloadimage.php?id=122510&root=1946/PNG/512/&file=1904660-email-envelope-letter-mail-message-post-send_122510.png")
            embedVar.set_footer(text=f'Message sent at {message.created_at}')
            embedVar.set_thumbnail(url=f'{message.author.avatar_url}')
            embedVar.add_field(name="Content:", value=f'{message.content}', inline=False)
            await logChannel.send(embed=embedVar)

    # Split between #message-log and #restrict-message-log
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:
            logChannel = self.client.get_channel(messageLogID)
            result = self.checkIfRestricted(message.author.roles)
            if result == 0:
                logChannel = self.client.get_channel(restrictMessageLogID)
            embedVar = discord.Embed(title=f'User {message.author}', description=f'A message sent by {message.author.mention} has been deleted in <#{message.channel.id}>.', color=16714507)
            embedVar.set_author(name="Message Deleted", icon_url="https://cdn.icon-icons.com/icons2/10/PNG/256/remove_delete_exit_close_1545.png")
            embedVar.set_thumbnail(url=f'{message.author.avatar_url}')
            embedVar.add_field(name="Content:", value=f'{message.content}', inline=False)

            # Assigned who deleted the message is way too difficult
            if checkIfRuleBroke(self, message):
                embedVar.set_footer(text=f'Message sent at {message.created_at}\nMessage deleted at {datetime.utcnow()}\nResponsible User (guess): HackUCF Bot -- AutoMod')
            else:
                hit = 0
                async for entry in message.guild.audit_logs(action=discord.AuditLogAction.message_delete):
                    try:
                        if entry.target == message.author and entry.extra.channel == message.channel and (abs((datetime.utcnow() - entry.created_at)).total_seconds() / 60.0) < 5:
                            embedVar.set_footer(text=f'Message sent at {message.created_at}\nMessage deleted at {datetime.utcnow()}\nResponsible User (guess): {entry.user}')
                            hit = 1
                            break
                    except:
                        pass
                if hit == 0:
                    embedVar.set_footer(text=f'Message sent at {message.created_at}\nMessage deleted at {datetime.utcnow()}\nResponsible User (guess): {message.author}')

            await logChannel.send(embed=embedVar)

    # Split between #message-log and #restrict-message-log
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        # Shouldn't matter if message was from bot or not
        logChannel = self.client.get_channel(messageLogID)
        result = self.checkIfRestricted(messages[0].author.roles)
        if result == 0:
            logChannel = self.client.get_channel(restrictMessageLogID)
        embedVar = discord.Embed(title=f'{len(messages)} messages', description=f'A bulk message deletion occurred. {len(messages)} messages have been deleted in <#{messages[0].channel.id}>.', color=16714507)
        embedVar.set_author(name="Bulk Message Deletion", icon_url="https://cdn.icon-icons.com/icons2/10/PNG/256/remove_delete_exit_close_1545.png")
        for message in messages:
            embedVar.add_field(name=f'Author: {message.author}', value=f'Contents:  {message.content}', inline=False)

        embedVar.set_footer(text=f'Messages deleted at {datetime.utcnow()}')
        await logChannel.send(embed=embedVar)

    # Split between #message-log and #restrict-message-log
    # BUG: Messages of length > 1024 will cause error. Embeds are limited to 1024 characters.
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.author.bot:
            unknownEmbedVar = discord.Embed(title=f'A message by {before.author}', description=f'A message sent by {before.author.mention} In Channel <#{before.channel.id}> has been edited. {after.jump_url}\n Here is what we know:', color=2575039)
            unknownEmbedVar.set_author(name="Message Edited (Raw Data)", icon_url="https://cdn.icon-icons.com/icons2/66/PNG/128/system_unknown_13010.png")
            unknownEmbedVar.set_footer(text=f'Message sent at {before.created_at}\nMessage edited at {datetime.utcnow()}')
            unknownEmbedVar.set_thumbnail(url=f'{before.author.avatar_url}')

            if before.activity != after.activity:
                unknownEmbedVar.add_field(name="activity changed: ", value=f'Before: {before.activity}\nAfter: {after.activity}', inline=False)

            if before.application != after.application:
                unknownEmbedVar.add_field(name="application changed: ", value=f'Before: {before.application}\nAfter: {after.application}', inline=False)

            if before.attachments != after.attachments:
                unknownEmbedVar.add_field(name="attachments changed: ", value=f'Before: {before.attachments}\nAfter: {after.attachments}', inline=False)

            if before.channel != after.channel:
                unknownEmbedVar.add_field(name="channel changed: ", value=f'Before: {before.channel}\nAfter: {after.channel}', inline=False)

            if before.channel_mentions != after.channel_mentions:
                unknownEmbedVar.add_field(name="channel_mentions changed: ", value=f'Before: {before.channel_mentions}\nAfter: {after.channel_mentions}', inline=False)

            if before.created_at != after.created_at:
                unknownEmbedVar.add_field(name="created_at changed: ", value=f'Before: {before.created_at}\nAfter: {after.created_at}', inline=False)

            if before.edited_at != after.edited_at:
                unknownEmbedVar.add_field(name="edited_at changed: ", value=f'Before: {before.edited_at}\nAfter: {after.edited_at}', inline=False)

            if before.flags != after.flags:
                unknownEmbedVar.add_field(name="flags changed: ", value=f'Before: {before.flags}\nAfter: {after.flags}', inline=False)

            if before.flags.value != after.flags.value:
                unknownEmbedVar.add_field(name="flags.value changed: ", value=f'Before: {before.flags.value}\nAfter: {after.flags.value}', inline=False)

            if before.flags.is_crossposted != after.flags.is_crossposted:
                unknownEmbedVar.add_field(name="flags.is_crossposted changed: ", value=f'Before: {before.flags.is_crossposted}\nAfter: {after.flags.is_crossposted}', inline=False)

            if before.flags.source_message_deleted != after.flags.source_message_deleted:
                unknownEmbedVar.add_field(name="flags.source_message_deleted changed: ", value=f'Before: {before.flags.source_message_deleted}\nAfter: {after.flags.source_message_deleted}', inline=False)

            if before.flags.urgent != after.flags.urgent:
                unknownEmbedVar.add_field(name=".flags.urgent changed: ", value=f'Before: {before.flags.urgent}\nAfter: {after.flags.urgent}', inline=False)

            if before.guild != after.guild:
                unknownEmbedVar.add_field(name="guild changed: ", value=f'Before: {before.guild}\nAfter: {after.guild}', inline=False)

            if before.id != after.id:
                unknownEmbedVar.add_field(name="id changed: ", value=f'Before: {before.id}\nAfter: {after.id}', inline=False)

            if before.jump_url != after.jump_url:
                unknownEmbedVar.add_field(name="jump_url changed: ", value=f'Before: {before.jump_url}\nAfter: {after.jump_url}', inline=False)

            if before.mention_everyone != after.mention_everyone:
                unknownEmbedVar.add_field(name="mention_everyone changed: ", value=f'Before: {before.mention_everyone}\nAfter: {after.mention_everyone}', inline=False)

            if before.mentions != after.mentions:
                unknownEmbedVar.add_field(name="mentions changed: ", value=f'Before: {before.mentions}\nAfter: {after.mentions}', inline=False)

            if before.nonce != after.nonce:
                unknownEmbedVar.add_field(name="nonce changed: ", value=f'Before: {before.nonce}\nAfter: {after.nonce}', inline=False)

            if before.raw_channel_mentions != after.raw_channel_mentions:
                unknownEmbedVar.add_field(name="raw_channel_mentions changed: ", value=f'Before: {before.raw_channel_mentions}\nAfter: {after.raw_channel_mentions}', inline=False)

            if before.raw_mentions != after.raw_mentions:
                unknownEmbedVar.add_field(name="raw_mentions changed: ", value=f'Before: {before.raw_mentions}\nAfter: {after.raw_mentions}', inline=False)

            if before.raw_role_mentions != after.raw_role_mentions:
                unknownEmbedVar.add_field(name="raw_role_mentions changed: ", value=f'Before: {before.raw_role_mentions}\nAfter: {after.raw_role_mentions}', inline=False)

            if before.reactions != after.reactions:
                unknownEmbedVar.add_field(name="reactions changed: ", value=f'Before: {before.reactions}\nAfter: {after.reactions}', inline=False)

            if before.reference != after.reference:
                unknownEmbedVar.add_field(name="reference changed: ", value=f'Before: {before.reference}\nAfter: {after.reference}', inline=False)

            if before.role_mentions != after.role_mentions:
                unknownEmbedVar.add_field(name="role_mentions changed: ", value=f'Before: {before.role_mentions}\nAfter: {after.role_mentions}', inline=False)

            if before.stickers != after.stickers:
                unknownEmbedVar.add_field(name="stickers changed: ", value=f'Before: {before.stickers}\nAfter: {after.stickers}', inline=False)

            if before.tts != after.tts:
                unknownEmbedVar.add_field(name="tts changed: ", value=f'Before: {before.tts}\nAfter: {after.tts}', inline=False)

            if before.type != after.type:
                unknownEmbedVar.add_field(name="type changed: ", value=f'Before: {before.type}\nAfter: {after.type}', inline=False)

            if before.webhook_id != after.webhook_id:
                unknownEmbedVar.add_field(name="webhook_id changed: ", value=f'Before: {before.webhook_id}\nAfter: {after.webhook_id}', inline=False)

            logChannel = self.client.get_channel(messageLogID)
            result = self.checkIfRestricted(before.author.roles)
            if result == 0:
                logChannel = self.client.get_channel(restrictMessageLogID)

            hits = 0
            # BUG: Embeds have to be 1024 characters or less, discord allows messages of up to 2000 characters. A large messages fails to create an embed
            if before.content != after.content:
                hits += 1
                embedVar = discord.Embed(title=f'User {before.author}', description=f'{before.author.mention} Has edited a message in <#{before.channel.id}>. {after.jump_url}', color=2575039)
                embedVar.set_author(name="Message Content Edited", icon_url="https://cdn.icon-icons.com/icons2/624/PNG/512/Create_New-80_icon-icons.com_57345.png")
                embedVar.set_footer(text=f'Message sent at {before.created_at}\nMessage edited at {after.edited_at}')
                embedVar.set_thumbnail(url=f'{before.author.avatar_url}')
                embedVar.add_field(name="Before:", value=f'{before.content}', inline=False)
                embedVar.add_field(name="After:", value=f'{after.content}', inline=False)
                await logChannel.send(embed=embedVar)

            if before.embeds != after.embeds:
                hits += 1
                embedVar = discord.Embed(title=f'A message by {before.author}', description=f'A message sent by {before.author.mention} in channel <#{before.channel.id}> has had embeds updated {after.jump_url}', color=2575039)
                embedVar.set_author(name="Message Embeds updated", icon_url="https://cdn.icon-icons.com/icons2/909/PNG/512/embed_icon-icons.com_70979.png")
                embedVar.set_footer(text=f'Message sent at {before.created_at}\nMessage edited at {datetime.utcnow()}')
                embedVar.set_thumbnail(url=f'{before.author.avatar_url}')
                embedVar.add_field(name="Message:", value=f'{before.content}', inline=False)
                await logChannel.send(embed=embedVar)

            if before.pinned != after.pinned:
                if after.pinned:
                    hits += 1
                    embedVar = discord.Embed(title=f'A message by {before.author}', description=f'A message sent by {before.author.mention} In Channel <#{before.channel.id}> was just pinned. {after.jump_url}', color=2575039)
                    embedVar.set_author(name="Message Pinned", icon_url="https://cdn.icon-icons.com/icons2/317/PNG/512/pin-icon_34381.png")
                    embedVar.set_footer(text=f'Message sent at {before.created_at}\nMessage edited at {datetime.utcnow()}')
                    embedVar.set_thumbnail(url=f'{before.author.avatar_url}')
                    embedVar.add_field(name="Message:", value=f'{before.content}', inline=False)
                    await logChannel.send(embed=embedVar)

                else:
                    hits += 1
                    embedVar = discord.Embed(title=f'A message by {before.author}', description=f'A message sent by {before.author.mention} In Channel <#{before.channel.id}> was just unpinned. {after.jump_url}', color=2575039)
                    embedVar.set_author(name="Message Un-pinned", icon_url="https://cdn.icon-icons.com/icons2/317/PNG/512/pin-icon_34381.png")
                    embedVar.set_footer(text=f'Message sent at {before.created_at}\nMessage edited at {datetime.utcnow()}')
                    embedVar.set_thumbnail(url=f'{before.author.avatar_url}')
                    embedVar.add_field(name="Message:", value=f'{before.content}', inline=False)
                    await logChannel.send(embed=embedVar)

            if before.flags.crossposted != after.flags.crossposted:
                if after.flags.crossposted:
                    hits += 1
                    embedVar = discord.Embed(title=f'A message by {before.author}', description=f'A message sent by {before.author.mention} In Channel <#{before.channel.id}> was just published. {after.jump_url}', color=2575039)
                    embedVar.set_author(name="Message published", icon_url="https://cdn.icon-icons.com/icons2/795/PNG/512/1-33_icon-icons.com_65689.png")
                    embedVar.set_footer(text=f'Message sent at {before.created_at}\nMessage edited at {datetime.utcnow()}')
                    embedVar.set_thumbnail(url=f'{before.author.avatar_url}')
                    embedVar.add_field(name="Message:", value=f'{before.content}', inline=False)
                    await logChannel.send(embed=embedVar)

                else:
                    hits += 1
                    embedVar = discord.Embed(title=f'A message by {before.author}', description=f'A message sent by {before.author.mention} In Channel <#{before.channel.id}> was just un-published. {after.jump_url}', color=2575039)
                    embedVar.set_author(name="Message un-published", icon_url="https://cdn.icon-icons.com/icons2/795/PNG/512/1-33_icon-icons.com_65689.png")
                    embedVar.set_footer(text=f'Message sent at {before.created_at}\nMessage edited at {datetime.utcnow()}')
                    embedVar.set_thumbnail(url=f'{before.author.avatar_url}')
                    embedVar.add_field(name="Message:", value=f'{before.content}', inline=False)
                    await logChannel.send(embed=embedVar)

            if before.flags.suppress_embeds != after.flags.suppress_embeds:
                if after.flags.suppress_embeds:
                    hits += 1
                    embedVar = discord.Embed(title=f'A message by {before.author}', description=f'A message sent by {before.author.mention} In Channel <#{before.channel.id}> has just had it\'s embeds suppressed. {after.jump_url}', color=2575039)
                    embedVar.set_author(name="Message embeds suppressed", icon_url="https://cdn.icon-icons.com/icons2/909/PNG/512/embed_icon-icons.com_70979.png")
                    embedVar.set_footer(text=f'Message sent at {before.created_at}\nMessage edited at {datetime.utcnow()}')
                    embedVar.set_thumbnail(url=f'{before.author.avatar_url}')
                    embedVar.add_field(name="Message:", value=f'{before.content}', inline=False)
                    await logChannel.send(embed=embedVar)

                else:
                    hits += 1
                    embedVar = discord.Embed(title=f'A message by {before.author}', description=f'A message sent by {before.author.mention} In Channel <#{before.channel.id}> has just had it\'s embeds un-suppressed. {after.jump_url}', color=2575039)
                    embedVar.set_author(name="Message embeds un-suppressed", icon_url="https://cdn.icon-icons.com/icons2/909/PNG/512/embed_icon-icons.com_70979.png")
                    embedVar.set_footer(text=f'Message sent at {before.created_at}\nMessage edited at {datetime.utcnow()}')
                    embedVar.set_thumbnail(url=f'{before.author.avatar_url}')
                    embedVar.add_field(name="Message:", value=f'{before.content}', inline=False)
                    await logChannel.send(embed=embedVar)

            # Send raw edit data to messageLog if it hasn't been recognized above
            if hits == 0:
                await logChannel.send(embed=unknownEmbedVar)

    # Split between #reaction-log and #restrict-reaction-log
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        logChannel = self.client.get_channel(reactionLogID)
        result = self.checkIfRestricted(user.roles)
        if result == 0:
            logChannel = self.client.get_channel(restrictReactionLogID)
        embedVar = discord.Embed(title=f'User {user}', description=f'{user.mention} just reacted {reaction} in channel <#{reaction.message.channel.id}>. {reaction.message.jump_url}', color=65302)
        embedVar.set_author(name="Reaction Made", icon_url="https://cdn.icon-icons.com/icons2/402/PNG/512/trafficlight-green_40427.png")
        embedVar.set_footer(text=f'Message sent at {reaction.message.created_at}\nReaction added at {datetime.utcnow()}')
        embedVar.set_thumbnail(url=f'{user.avatar_url}')
        embedVar.add_field(name="Message contents:", value=f'{reaction.message.content}', inline=False)
        await logChannel.send(embed=embedVar)

    # Split between #reaction-log and #restrict-reaction-log
    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        logChannel = self.client.get_channel(reactionLogID)
        result = self.checkIfRestricted(user.roles)
        if result == 0:
            logChannel = self.client.get_channel(restrictReactionLogID)
        embedVar = discord.Embed(title=f'User {user}', description=f'{user.mention} just un-reacted {reaction} in channel <#{reaction.message.channel.id}>. {reaction.message.jump_url}', color=16714507)
        embedVar.set_author(name="Reaction Removed", icon_url="https://cdn.icon-icons.com/icons2/402/PNG/512/trafficlight-red_40428.png")
        embedVar.set_footer(text=f'Message sent at {reaction.message.created_at}\nReaction removed at {datetime.utcnow()}')
        embedVar.set_thumbnail(url=f'{user.avatar_url}')
        embedVar.add_field(name="Message contents:", value=f'{reaction.message.content}', inline=False)
        await logChannel.send(embed=embedVar)

    # Split between #reaction-log and #restrict-reaction-log
    @commands.Cog.listener()
    async def on_reaction_clear(self, message, reactions):
        logChannel = self.client.get_channel(reactionLogID)
        result = self.checkIfRestricted(message.author.roles)
        if result == 0:
            logChannel = self.client.get_channel(restrictReactionLogID)
        embedVar = discord.Embed(title=f'User {message.author}', description=f'A message by {message.author.mention} in channel <#{reactions[0].message.channel.id}> has just had all reactions cleared. {reactions[0].message.jump_url}', color=16714507)
        embedVar.set_author(name="Reactions Cleared", icon_url="https://cdn.icon-icons.com/icons2/402/PNG/512/trafficlight-red_40428.png")
        embedVar.set_footer(text=f'Message sent at {reactions[0].message.created_at}\nReactions cleared at {datetime.utcnow()}')
        embedVar.set_thumbnail(url=f'{message.author.avatar_url}')
        for reaction in reactions:
            embedVar.add_field(name=f'Reaction {reaction} removed', value=f'This reaction was reacted {reaction.count} time(s)', inline=False)
        embedVar.add_field(name="Message contents:", value=f'{reactions[0].message.content}', inline=False)
        await logChannel.send(embed=embedVar)

    # Split between #reaction-log and #restrict-reaction-log
    # I have no idea how to trigger this. Maybe it is deprecated?
    @commands.Cog.listener()
    async def on_reaction_clear_emoji(self, reaction):
        logChannel = self.client.get_channel(reactionLogID)
        result = self.checkIfRestricted(reaction.message.author.roles)
        if result == 0:
            logChannel = self.client.get_channel(restrictReactionLogID)
        embedVar = discord.Embed(title=f'User {reaction.me}', description=f'{reaction.me.mention} just got {reaction} cleared in channel <#{reaction.message.channel.id}>. {reaction.message.jump_url}', color=16714507)
        embedVar.set_author(name="Reaction Cleared", icon_url="https://cdn.icon-icons.com/icons2/402/PNG/512/trafficlight-red_40428.png")
        embedVar.set_footer(text=f'Message sent at {reaction.message.created_at}\nReaction cleared at {datetime.utcnow()}')
        embedVar.set_thumbnail(url=f'{reaction.me.avatar_url}')
        embedVar.add_field(name="Message contents:", value=f'{reaction.message.content}', inline=False)
        await logChannel.send(embed=embedVar)

    # Log to #channel-log
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        embedVar = None
        if isinstance(channel, discord.CategoryChannel):
            embedVar = discord.Embed(title=f'Category {channel.name}', description=f'Category #{channel.name} was just deleted.', color=16714507)
        elif isinstance(channel, discord.TextChannel):
            embedVar = discord.Embed(title=f'Text Channel #{channel.name}', description=f'Text Channel #{channel.name} was just deleted.', color=16714507)
        elif isinstance(channel, discord.VoiceChannel):
            embedVar = discord.Embed(title=f'Voice Channel #{channel.name}', description=f'Voice #{channel.name} was just deleted.', color=16714507)
        else:
            embedVar = discord.Embed(title=f'Unknown type of Channel #{channel.name}', description=f'Unknown Channel type #{channel.name} was just deleted.', color=16714507)
        logChannel = self.client.get_channel(channelLogID)
        embedVar.set_author(name="Channel Deleted", icon_url="https://cdn.icon-icons.com/icons2/1808/PNG/512/trash-can_115312.png")
        embedVar.set_footer(text=f'Channel created at {channel.created_at}\nChannel deleted at {datetime.utcnow()}')
        embedVar.add_field(name="Channel Category:", value=f'{channel.category}', inline=False)
        embedVar.add_field(name="Channel Position:", value=f'{channel.position}', inline=False)
        await logChannel.send(embed=embedVar)

    # Log to #channel-log
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        embedVar = None
        if isinstance(channel, discord.CategoryChannel):
            embedVar = discord.Embed(title=f'Category {channel.name}', description=f'Category {channel.mention} was just created.', color=65302)
        elif isinstance(channel, discord.TextChannel):
            embedVar = discord.Embed(title=f'Text Channel #{channel.name}', description=f'Text Channel {channel.mention} was just created.', color=65302)
        elif isinstance(channel, discord.VoiceChannel):
            embedVar = discord.Embed(title=f'Voice Channel #{channel.name}', description=f'Voice {channel.mention} was just created.', color=65302)
        else:
            return

        logChannel = self.client.get_channel(channelLogID)
        embedVar.set_author(name="Channel created", icon_url="https://cdn.icon-icons.com/icons2/1358/PNG/512/if-advantage-creation-1034354_88852.png")
        embedVar.add_field(name="Channel Category:", value=f'{channel.category}', inline=False)
        embedVar.add_field(name="Channel Position:", value=f'{channel.position}', inline=False)
        perms = self.getChannelPerms(channel.overwrites)
        for perm in perms:
            if perm[1] == "":
                embedVar.add_field(name=f'{perm[0]}', value=f'No overwrites', inline=False)
            else:
                embedVar.add_field(name=f'{perm[0]}', value=f'{perm[1]}', inline=False)
        hit = 0
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create):
            try:
                print('{0.user} created channel {0.target}'.format(entry))
                if entry.target == channel:
                    embedVar.set_footer(text=f'Channel created at {channel.created_at}\nResponsible User: {entry.user}')
                    hit = 1
                    break
            except:
                pass
        if hit == 0:
            embedVar.set_footer(text=f'Channel created at {channel.created_at}\nResponsible User: Unknown')

        await logChannel.send(embed=embedVar)

    # Log to #channel-log
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if isinstance(after, discord.CategoryChannel):
            embedVar = discord.Embed(title=f'Category {after.name}', description=f'Category {after.mention} was just updated.', color=2575039)
        elif isinstance(after, discord.TextChannel):
            embedVar = discord.Embed(title=f'Text Channel #{after.name}', description=f'Text Channel {after.mention} was just updated.', color=2575039)
        elif isinstance(after, discord.VoiceChannel):
            embedVar = discord.Embed(title=f'Voice Channel #{after.name}', description=f'Voice {after.mention} was just updated.', color=2575039)
        else:
            return
        logChannel = self.client.get_channel(channelLogID)
        embedVar.set_author(name="Channel updated", icon_url="https://cdn.icon-icons.com/icons2/1381/PNG/512/systemsoftwareupdate_94333.png")
        embedVar.set_footer(text=f'Channel updated at {datetime.utcnow()}\nChannel created at {before.created_at}')
        # bitrate, category, name, NSFW, permissions, permissions_synced, position, rtc_region, slowmode, topic, type, and user_limit can all be tracked
        # Type only works for text channels, we cannot difference voice vs staging yet
        # Cannot check if forced video quality is changed either

        # bitrate
        try:
            if before.bitrate != after.bitrate:
                embedVar.add_field(name="Channel bitrate has been updated", value=f'Before: {before.bitrate}\nAfter: {after.bitrate}', inline=False)
        except:
            pass

        # category
        try:
            if before.category != after.category:
                embedVar.add_field(name="Channel category changed", value=f'Before: {before.category}\nAfter: {after.category}', inline=False)
        except:
            pass

        # name
        try:
            if before.name != after.name:
                embedVar.add_field(name="Channel name changed", value=f'Before: {before.name}\nAfter: {after.name}', inline=False)
        except:
            pass

        # is_nsfw()
        try:
            if before.is_nsfw() != after.is_nsfw():
                embedVar.add_field(name="Channel NSFW marking changed", value=f'Before: {before.is_nsfw()}\nAfter: {after.is_nsfw()}', inline=False)
        except:
            pass

        # overwrites
        try:
            if before.overwrites != after.overwrites:
                embedVar.add_field(name="Channel permissions changed", value=f'Before: {before.bitrate}\nAfter: {after.bitrate}', inline=False)
                # perms = self.getChannelPerms(channel.overwrites)
        except:
            pass

        # permissions_synced
        try:
            if before.permissions_synced != after.permissions_synced:
                embedVar.add_field(name="Channel synced permission status has changed", value=f'Before: {before.permissions_synced}\nAfter: {after.permissions_synced}', inline=False)
        except:
            pass

        # position
        try:
            if before.position != after.position:
                embedVar.add_field(name="Channel position has changed", value=f'Before: {before.position}\nAfter: {after.position}', inline=False)
        except:
            pass

        # rtc_region
        try:
            if before.rtc_region != after.rtc_region:
                embedVar.add_field(name="Channel region has changed", value=f'Before: {before.rtc_region}\nAfter: {after.rtc_region}', inline=False)
        except:
            pass

        # slowmode_delay
        try:
            if before.slowmode_delay != after.slowmode_delay:
                embedVar.add_field(name="Channel slowmode has changed", value=f'Before: {before.slowmode_delay}\nAfter: {after.slowmode_delay}', inline=False)
        except:
            pass

        # topic
        try:
            if before.topic != after.topic:
                embedVar.add_field(name="Channel topic has changed", value=f'Before: {before.topic}\nAfter: {after.topic}', inline=False)
        except:
            pass

        # type
        try:
            if before.type != after.type:
                embedVar.add_field(name="Channel type has changed", value=f'Before: {before.type}\nAfter: {after.type}', inline=False)
        except:
            pass

        # user_limit
        try:
            if before.user_limit != after.user_limit:
                embedVar.add_field(name="Voice channel max users updated", value=f'Before: {before.user_limit}\nAfter: {after.user_limit}', inline=False)
        except:
            pass

        await logChannel.send(embed=embedVar)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            logChannel = self.client.get_channel(memberLogID)
            await logChannel.send(f'{member} has joined the server.')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not member.bot:
            logChannel = self.client.get_channel(memberLogID)
            await logChannel.send(f'{member} has left the server.')


def setup(client):
    client.add_cog(logs(client))
