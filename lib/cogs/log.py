import discord

from datetime import datetime

from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions

from ..db import db

class Log(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:

			self.bot.cogs_ready.ready_up("log")

#	@Cog.listener()
#	async def on_user_update(self, before, after):
#		if before.name != after.name:
#			embed = Embed(title="Username change",
#						  colour=after.colour,
#						  timestamp=datetime.utcnow())
#
#			fields = [("Before", before.name, False),
#					  ("After", after.name, False)]
#
#			for name, value, inline in fields:
#				embed.add_field(name=name, value=value, inline=inline)
#
#			await self.log_channel.send(embed=embed)
#
#		if before.discriminator != after.discriminator:
#			embed = Embed(title="Discriminator change",
#						  colour=after.colour,
#						  timestamp=datetime.utcnow())
#
#			fields = [("Before", before.discriminator, False),
#					  ("After", after.discriminator, False)]
#
#			for name, value, inline in fields:
#				embed.add_field(name=name, value=value, inline=inline)
#
#			await self.log_channel.send(embed=embed)
#
#		if before.avatar_url != after.avatar_url:
#			embed = Embed(title="Avatar change",
#						  description="New image is below, old to the right.",
#						  colour=self.log_channel.guild.get_member(after.id).colour,
#						  timestamp=datetime.utcnow())
#
#			embed.set_thumbnail(url=before.avatar_url)
#			embed.set_image(url=after.avatar_url)
#
#			await self.log_channel.send(embed=embed)

	@command(name="addnamelog")
	@has_permissions(manage_guild=True)
	async def addnamelog_command(self, ctx, channel: discord.TextChannel):
		try:
			channel = ctx.guild.get_channel(channel.id)

		except ChannelNotFound:
			await ctx.send("Channel not found.")
			return

		try:
			db.execute("INSERT INTO nickname_log VALUES (?, ?)", ctx.guild.id, channel.id)
			await ctx.send("Successfully added the Nickname Log.")

		except:
			await ctx.send("You already defined a Nickname Log channel.")
			pass

	@command(name="removenamelog")
	@has_permissions(manage_guild=True)
	async def removenamelog_command(self, ctx):
		try:
			db.execute("DELETE FROM nickname_log WHERE GuildID = ?", ctx.guild.id)
			await ctx.send("Successfully removed the Nickname Log.")

		except:
			await ctx.send("You never defined a Nickname Log Channel.")
			pass

	@command(name="addrolelog")
	@has_permissions(manage_guild=True)
	async def addrolelog_command(self, ctx, channel: discord.TextChannel):
		try:
			channel = ctx.guild.get_channel(channel.id)

		except ChannelNotFound:
			await ctx.send("Channel not found.")
			return

		try:
			db.execute("INSERT INTO role_log VALUES (?, ?)", ctx.guild.id, channel.id)
			await ctx.send("Successfully added the role Log.")

		except:
			await ctx.send("You already defined a role log channel.")
			pass

	@command(name="removerolelog")
	@has_permissions(manage_guild=True)
	async def removerolelog_command(self, ctx):
		try:
			db.execute("DELETE FROM role_log WHERE GuildID = ?", ctx.guild.id)
			await ctx.send("Successfully removed the role Log.")

		except:
			await ctx.send("You never defined a role Log Channel.")
			pass

	@Cog.listener()
	async def on_member_update(self, before, after):
		if before.display_name != after.display_name:
			embed = Embed(title="Nickname change",
						  colour=after.colour,
						  timestamp=datetime.utcnow())

			fields = [("Before", before.display_name, False),
					  ("After", after.display_name, False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)



			nickname_log_channel_id = db.field("SELECT nickname_log_channel FROM nickname_log WHERE GuildID = ?", before.guild.id)

			if nickname_log_channel_id == None:
				return

			nickname_log_channel = before.guild.get_channel(nickname_log_channel_id)

			await nickname_log_channel.send(embed=embed)

		elif before.roles != after.roles:
			embed = Embed(title="Role update",
						  colour=after.colour,
						  timestamp=datetime.utcnow())

			fields = [("Before", ", ".join([r.mention for r in before.roles]), False),
					  ("After", ", ".join([r.mention for r in after.roles]), False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)

			try:

				role_log_channel_id = db.field("SELECT role_log_channel FROM role_log WHERE GuildID = ?", before.guild.id)

				if role_log_channel_id == None:
					return

				role_log_channel = before.guild.get_channel(role_log_channel_id)

				await role_log_channel.send(embed=embed)

			except:
				pass

	@command(name="addmessagelog")
	@has_permissions(manage_guild=True)
	async def addmessagelog_command(self, ctx, channel: discord.TextChannel):
		try:
			channel = ctx.guild.get_channel(channel.id)

		except ChannelNotFound:
			await ctx.send("Channel not found.")
			return

		try:
			db.execute("INSERT INTO message_log VALUES (?, ?)", ctx.guild.id, channel.id)
			await ctx.send("Successfully added the message Log.")

		except:
			await ctx.send("You already defined a message Log channel.")
			pass

	@command(name="removemessagelog")
	@has_permissions(manage_guild=True)
	async def removemessagelog_command(self, ctx):
		try:
			db.execute("DELETE FROM message_log WHERE GuildID = ?", ctx.guild.id)
			await ctx.send("Successfully removed the message Log.")

		except:
			await ctx.send("You already defined a message Log channel.")
			pass

	@Cog.listener()
	async def on_message_edit(self, before, after):
		if not after.author.bot:
			if before.content != after.content:
				embed = Embed(title="Message edit",
							  description=f"Edit by {after.author.display_name}.",
							  colour=after.author.colour,
							  timestamp=datetime.utcnow())

				fields = [("Before", before.content, False),
						  ("After", after.content, False)]

				for name, value, inline in fields:
					embed.add_field(name=name, value=value, inline=inline)

				try:
					message_log_channel_id = db.field("SELECT message_log_channel FROM message_log WHERE GuildID = ?", before.guild.id)
					message_log_channel = before.guild.get_channel(message_log_channel_id)

					await message_log_channel.send(embed=embed)

				except:
					pass

	@Cog.listener()
	async def on_message_delete(self, message):
		if not message.author.bot:
			embed = Embed(title="Message deletion",
						  description=f"Action by {message.author.display_name}.",
						  colour=message.author.colour,
						  timestamp=datetime.utcnow())

			fields = [("Content", message.content, False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)

			message_log_channel_id = db.field("SELECT message_log_channel FROM message_log WHERE GuildID = ?", message.guild.id)

			if message_log_channel_id == None:
				return

			message_log_channel = message.guild.get_channel(message_log_channel_id)

			await message_log_channel.send(embed=embed)


def setup(bot):
	bot.add_cog(Log(bot))
