import discord
import asyncio
import sqlite3

from asyncio import sleep
from datetime import datetime
from discord import Embed, NotFound
from discord.ext.commands import Cog, has_permissions
from discord.ext.commands import command

from ..db import db


class Jointocreate(Cog):
	def __init__(self, bot):
		self.bot = bot
		self.bot.loop.create_task(self.join_to_create_channel_check())
		self.bot.loop.create_task(self.join_to_create_check())

	async def join_to_create_channel_check(self):
		await self.bot.wait_until_ready()
		created_channels = db.records("SELECT ChannelID FROM join_to_create_user_channels")

		if created_channels == None:
			return

		for channel_id in created_channels:
			channel = await self.bot.fetch_channel(channel_id[0])
			if channel == None:
				db.execute("DELETE FROM join_to_create_user_channels WHERE ChannelID = ?", channel_id)
				db.commit()

			if channel != None:
				if not channel.members:
					await channel.delete()
					db.execute("DELETE FROM join_to_create_user_channels WHERE GuildID = ? AND ChannelID = ?", channel.guild.id, channel.id)
					db.commit()

	async def join_to_create_check(self):
		await self.bot.wait_until_ready()
		jtc_channels = db.records("SELECT GuildID, ChannelID FROM join_to_create_channels")

		if jtc_channels == None:
			return

		for guild_id, channel_id in jtc_channels:
			channel = await self.bot.fetch_channel(channel_id)
			if channel == None:
				db.execute("DELETE FROM join_to_create_channels WHERE ChannelID = ?", channel_id)
				db.commit()


	async def join_to_create_timeout(self, channel):
		print("join_to_create_timeout")
		await sleep(15)
		print("Sleeped")
		if not channel.members:
			print("passed")
			try:
				await channel.delete()
				db.execute("DELETE FROM join_to_create_user_channels WHERE GuildID = ? AND ChannelID = ?", channel.guild.id, channel.id)
				db.commit()

			except NotFound:
				pass


	@command(name="jointocreate")
	@has_permissions(manage_guild=True)
	async def create_join_to_create(self, ctx):

		join_to_create_channel = await ctx.guild.create_voice_channel("Join To Create")

		try:
			db.execute("INSERT INTO join_to_create_channels VALUES (?, ?)", ctx.guild.id, join_to_create_channel.id)
			db.commit()

		except sqlite3.IntegrityError:
			embed = Embed(title = "Failed",
						  description = f"❌ Failed to create Join to Create Channel.",
						  colour=discord.Color.red(),
						  timestamp=datetime.utcnow())

			await ctx.send(embed=embed)
			return

		embed = Embed(title = "Successfully created Join to Create Channel",
					  description = f"✅ successfuly created join to create Channel: {join_to_create_channel.mention}",
					  colour=discord.Color.green(),
					  timestamp=datetime.utcnow())

		await ctx.send(embed=embed)


	@Cog.listener("on_voice_state_update")
	async def created_channel_check(self, member, before, after):
		if member.bot:
			return

		if after.channel == None:
			return

		join_to_create_channel_id = db.field("SELECT ChannelID FROM join_to_create_channels WHERE GuildID = ?", member.guild.id)

		if join_to_create_channel_id != None:

			if after.channel.id == join_to_create_channel_id:

				overwrites = {
					member: discord.PermissionOverwrite(mute_members = True),
					member: discord.PermissionOverwrite(deafen_members = True),
					member: discord.PermissionOverwrite(manage_channels = True)
				}

				member_channel = await member.guild.create_voice_channel(f"{member.name}`s Channel", overwrites=overwrites, category=after.channel.category)

				await member.move_to(member_channel)

				db.execute("INSERT INTO join_to_create_user_channels VALUES (?, ?)", member.guild.id, member_channel.id)
				db.commit()


	@Cog.listener("on_voice_state_update")
	async def delete_channel_check(self, member, before, after):
		if before.channel == None:
			return

		created_channels = db.records("SELECT ChannelID FROM join_to_create_user_channels WHERE GuildID = ?", member.guild.id)

		if created_channels == None:
			return

		for channel_id in created_channels:
			if channel_id[0] == before.channel.id:
				if not before.channel.members:
					asyncio.create_task(self.join_to_create_timeout(before.channel))


	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("jointocreate")

def setup(bot):
	bot.add_cog(Jointocreate(bot))
