import discord
import sqlite3

from datetime import datetime
from discord import Forbidden, Embed
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions

from ..db import db


class Welcome(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="setwelcomer")
	@has_permissions(manage_guild=True)
	async def setwelcomer_command(self, ctx, channel: discord.TextChannel, *, welcome_message):
		try:
			db.execute("INSERT INTO welcomer VALUES (?, ?, ?)", ctx.guild.id, channel.id, welcome_message)
			
		except sqlite3.IntegrityError:
			embed = Embed(title = "Failed",
						  description = f"❌ {guild} already has a welcomer.",
						  colour=discord.Color.red(),
						  timestamp=datetime.utcnow())

			await ctx.send(embed=embed)
			return

		embed = Embed(title = "Welcomer added",
					  description = f"✅ successfuly added welcomer and set to {channel.mention}.",
					  colour=discord.Color.green(),
					  timestamp=datetime.utcnow())

		await ctx.send(embed=embed)


	@command(name="setdmwelcomer")
	@has_permissions(manage_guild=True)
	async def setdmwelcomer_command(self, ctx, *, welcome_message):
		try:
			db.execute("INSERT INTO dmwelcomer VALUES (?, ?)", ctx.guild.id, welcome_message)

		except sqlite3.IntegrityError:
			embed = Embed(title = "Failed",
						  description = f"❌ {guild} already has a DM welcomer.",
						  colour=discord.Color.red(),
						  timestamp=datetime.utcnow())

			await ctx.send(embed=embed)
			return

		embed = Embed(title = "DM Welcomer added",
					  description = "✅ successfuly added DM welcomer.",
					  colour=discord.Color.green(),
					  timestamp=datetime.utcnow())

		await ctx.send(embed=embed)

	@command(name="removewelcomer")
	@has_permissions(manage_guild=True)
	async def removewelcomer_command(self, ctx):
		try:
			db.execute("DELETE FROM welcomer WHERE GuildID = ?", ctx.guild.id)

		except:
			return

		embed = Embed(title = "Welcomer removed",
					  description = "✅ successfuly removed welcomer.",
					  colour=discord.Color.green(),
					  timestamp=datetime.utcnow())

		await ctx.send(embed=embed)

	@command(name="removedmwelcomer")
	@has_permissions(manage_guild=True)
	async def removedmwelcomer_command(self, ctx):
		try:
			db.execute("DELETE FROM dmwelcomer WHERE GuildID = ?", ctx.guild.id)

		except:
			return

		embed = Embed(title = "DM Welcomer removed",
					  description = "✅ successfuly removed DM welcomer.",
					  colour=discord.Color.green(),
					  timestamp=datetime.utcnow())

		await ctx.send(embed=embed)


	@Cog.listener()
	async def on_member_join(self, member):

		channel_id = db.field("SELECT ChannelID FROM welcomer WHERE GuildID = ?", member.guild.id)
		welcome_message = db.field("SELECT welcome_message FROM welcomer WHERE GuildID = ?", member.guild.id)

		if channel_id != None and welcome_message != None:
			if (welcome_message.__contains__("{member}")):
				welcome_message = welcome_message.replace("{member}", f"{member.name}")

			await self.bot.get_channel(channel_id).send(welcome_message)

		dm_welcome_message = db.field("SELECT welcome_message FROM dmwelcomer WHERE GuildID = ?", member.guild.id)

		if dm_welcome_message != None:
			if (dm_welcome_message.__contains__("{member}")):
				dm_welcome_message = dm_welcome_message.replace("{member}", f"{member.name}")

			try:
				await member.send(dm_welcome_message)

			except Forbidden:
				pass


	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("welcome")

def setup(bot):
	bot.add_cog(Welcome(bot))
