
from datetime import datetime

from discord import Member, Embed
from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, Greedy, has_permissions

from ..db import db

class Customcommands(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="addcommand", aliases=["addcc"])
	@has_permissions(manage_guild=True)
	async def addcommand_command(self, ctx, name, *, content):

		check = db.field("SELECT Content FROM customcommands WHERE GuildID = ? AND Commandname = ?", ctx.guild.id, name)

		if check != None:
			await ctx.send("A command with this name is already registered.")
			return

		db.execute("INSERT INTO customcommands VALUES (?, ?, ?)", ctx.guild.id, name, content)

		embed = Embed(title="Command Successfully added",
					  description="Command:",
					  colour=ctx.author.colour,
					  timestamp=datetime.utcnow())

		embed.add_field(name=name, value=content, inline=False)

		await ctx.send(embed=embed)

	@command(name="removecommand", aliases=["delcc"])
	@has_permissions(manage_guild=True)
	async def removecommand_command(self, ctx, name):
		content = db.field("SELECT Content FROM customcommands WHERE GuildID = ? AND Commandname = ?", ctx.guild.id, name)
		db.execute("DELETE FROM customcommands WHERE GuildID = ? AND Commandname = ?", ctx.guild.id, name)

		embed = Embed(title="Command Successfully removed",
					  description="Command:",
					  colour=ctx.author.colour,
					  timestamp=datetime.utcnow())

		embed.add_field(name=name, value=content, inline=False)

		await ctx.send(embed=embed)


	@command(name="bewerber")
	@has_permissions(ban_members=True)
	async def bewerber_command(self, ctx, targets: Greedy[Member]):
		for target in targets:
			try:
				bewerber_role = ctx.guild.get_role(811697980658810931)
				await target.add_roles(bewerber_role)
				await ctx.send(f"Added Bewerber role to {target}")

			except:
				pass

	@command(name="vfxbewerber")
	@has_permissions(ban_members=True)
	async def vfxbewerber_command(self, ctx, targets: Greedy[Member]):
		for target in targets:
			try:
				bewerber_role = ctx.guild.get_role(811710247940784218)
				await target.add_roles(bewerber_role)
				await ctx.send(f"Added Bewerber role to {target}")

			except:
				pass

	@command(name="gfxbewerber")
	@has_permissions(ban_members=True)
	async def gfxbewerber_command(self, ctx, targets: Greedy[Member]):
		for target in targets:
			try:
				bewerber_role = ctx.guild.get_role(812097156872667167)
				await target.add_roles(bewerber_role)
				await ctx.send(f"Added Bewerber role to {target}")

			except:
				pass


	@Cog.listener()
	async def on_message(self, message):
		if message.guild is not None:
			if message.author.bot:
				return

			content = db.field("SELECT Content FROM customcommands WHERE GuildID = ? AND Commandname = ?", message.guild.id, message.content)

			if content == None:
				return

			else:
				await message.channel.send(content)

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("customcommands")


def setup(bot):
	bot.add_cog(Customcommands(bot))
