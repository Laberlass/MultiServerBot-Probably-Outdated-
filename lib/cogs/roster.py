import typing
import discord
import sqlite3

from typing import Optional
from datetime import datetime

from sqlite3 import IntegrityError
from discord import HTTPException
from discord.ext.commands import ChannelNotFound

from discord import Embed
from discord.ext.commands import Cog, Greedy
from discord.ext.commands import command, has_permissions

from ..db import db

class Roster(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def roster_update(self, guild):

        try:
            role_ids, channel_id, message_id = db.record("SELECT RoleIDs, ChannelID, MessageID FROM roster WHERE GuildID = ?", guild.id)

        except TypeError:
            return

        roles = [guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]

        channel = guild.get_channel(channel_id)
        message = await channel.fetch_message(message_id)

        embed = Embed(title=f"**{guild} Roster**",
                      description="▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
 					  colour=message.author.colour,
 					  timestamp=datetime.utcnow())

        embed.set_thumbnail(url=guild.icon_url)

        for role in roles:
            embed.add_field(name="\u200b", value=f"{role.mention} \n" + "\n".join([m.display_name for m in role.members]), inline=False)

        try:
            await message.edit(embed=embed)

        except HTTPException:
            await channel.send("The Roster is to long.")

    @command(name="setroster")
    @has_permissions(manage_guild=True)
    async def setroster_command(self, ctx, channel: discord.TextChannel, roles: Greedy[discord.Role]):

        message = await channel.send("Setting up...")

        role_ids = ",".join([str(r.id) for r in roles])

        try:
            db.execute("INSERT INTO roster VALUES (?, ?, ?, ?)",
                        ctx.guild.id, role_ids, channel.id, message.id)

            db.commit()

        except IntegrityError:
            await ctx.send("You are not able to have more than one active roster.")
            return

        guild = ctx.guild

        await self.roster_update(guild)

        await message.edit(content="\u200b")

        await ctx.send("Roster created.")

    @setroster_command.error
    async def setroster_command_error(self, ctx, exc):
        exco = getattr(exc, "original", exc)
        if isinstance(exc, ChannelNotFound):
            await ctx.send("Channel not found.")

    @command(name="delroster")
    @has_permissions(manage_guild=True)
    async def delroster_command(self, ctx):
        channel_id, message_id = db.record("SELECT ChannelID, MessageID FROM roster WHERE GuildID = ?", ctx.guild.id)
        channel = ctx.guild.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        await message.delete()
        db.execute("DELETE FROM roster WHERE GuildID = ?", ctx.guild.id)
        await ctx.send("Roster deactivated.")

    @Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            guild = after.guild

            await self.roster_update(guild)


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("roster")

def setup(bot):
    bot.add_cog(Roster(bot))
