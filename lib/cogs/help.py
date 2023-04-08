from typing import Optional

import discord
import asyncio

from discord import Embed
from discord import guild
from discord.utils import get
from discord.ext.menus import MenuPages, ListPageSource
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord_components import *
from datetime import datetime


def syntax(command):
	cmd_and_aliases = "|".join([str(command), *command.aliases])
	params = []

	for key, value in command.params.items():
		if key not in ("self", "ctx"):
			params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")

	params = " ".join(params)

	return f"`{cmd_and_aliases} {params}`"


class HelpMenu(ListPageSource):
	def __init__(self, ctx, data):
		self.ctx = ctx

		super().__init__(data, per_page=3)

	async def write_page(self, menu, fields=[]):
		offset = (menu.current_page*self.per_page) + 1
		len_data = len(self.entries)

		embed = Embed(title="Help",
					  description=f"Help Command dialog!",
					  colour=self.ctx.author.colour)
		embed.set_thumbnail(url=self.ctx.guild.icon_url)
		embed.set_footer(text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} commands.")

		for name, value in fields:
			embed.add_field(name=name, value=value, inline=False)

		return embed

	async def format_page(self, menu, entries):
		fields = []

		for entry in entries:
			fields.append((entry.brief or "No description", syntax(entry)))

		return await self.write_page(menu, fields)


class Help(Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cmd_help(self, ctx, command):
		embed = Embed(title=f"Help with `{command}`",
					  description=syntax(command),
					  colour=ctx.author.colour)
		embed.add_field(name="Command description", value=command.help)
		await ctx.send(embed=embed)

	@command(name="help2")
	async def show_help(self, ctx, cmd: Optional[str]):
		"""Shows this message."""
		if cmd is None:
			menu = MenuPages(source=HelpMenu(ctx, list(self.bot.commands)),
							 delete_message_after=True,
							 timeout=60.0)
			await menu.start(ctx)

		else:
			if (command := get(self.bot.commands, name=cmd)):
				await self.cmd_help(ctx, command)

			else:
				await ctx.send("That command does not exist.")

	@command(name="help")
	async def help_command(self, ctx):
		home_embed = discord.Embed(title=f"Command List of {ctx.guild}",
							  description="Here are all commands of this Bot listed.",
							  color=ctx.author.color,
							  timestamp=datetime.utcnow())

		home_embed.add_field(name=":crystal_ball:Fun:", value="Fun Commands")
		home_embed.add_field(name=":bar_chart:Info:", value="Informative Commands")
		home_embed.add_field(name=":chart_with_upwards_trend:Leveling:", value="Leveling Commands")
		home_embed.set_thumbnail(url=ctx.guild.icon_url)
		home_embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

		if ctx.author.guild_permissions.manage_guild:
			home_embed.add_field(name=":closed_lock_with_key:Moderation:", value="Commands for Moderation")
			home_embed.add_field(name=":tools:Einstellungen:", value="Bot Settings")
			embed = await ctx.send(embed=home_embed,
						   components=[
	 						  Select(placeholder="Select Category", options=[
							  SelectOption(label="Home Button", value="Home", emoji="\U0001f3d8"),
							  SelectOption(label="Fun Commands", value="Fun", emoji="\U0001f52e"),
							  SelectOption(label="Info Commands", value="Info", emoji="\U0001f4ca"),
							  SelectOption(label="Leveling Commands", value="Lvl", emoji="\U0001f4c8"),
							  SelectOption(label="Moderation Commands", value="Mod", emoji="\U0001f510"),
							  SelectOption(label="Settings", value="Sett", emoji="\U0001f6e0"),
							  SelectOption(label="Stop", value="Stop", emoji="\U0000274c")
							  ])]
						  )

		elif ctx.author.guild_permissions.manage_messages:
			embed = await ctx.send(embed=home_embed,
						   components=[
	 						  Select(placeholder="Select Category", options=[
							  SelectOption(label="Home Button", value="Home", emoji="\U0001f3d8"),
							  SelectOption(label="Fun Commands", value="Fun", emoji="\U0001f52e"),
							  SelectOption(label="Info Commands", value="Info", emoji="\U0001f4ca"),
							  SelectOption(label="Leveling Commands", value="Lvl", emoji="\U0001f4c8"),
							  SelectOption(label="Moderation Commands", value="Mod", emoji="\U0000274c"),
							  SelectOption(label="Stop", value="Stop", emoji="\U0000274c")
							  ])]
						  )

		else:
			embed = await ctx.send(embed=home_embed,
						   components=[
	 						  Select(placeholder="Select Category", options=[
							  SelectOption(label="Home Button", value="Home", emoji="\U0001f3d8"),
							  SelectOption(label="Fun Commands", value="Fun", emoji="\U0001f52e"),
							  SelectOption(label="Info Commands", value="Info", emoji="\U0001f4ca"),
							  SelectOption(label="Leveling Commands", value="Lvl", emoji="\U0001f4c8"),
							  SelectOption(label="Stop", value="Stop", emoji="\U0000274c", timeout=240)
							  ])]
						  )

		def check(interaction):
			return interaction.message.id == embed.id and ctx.author.id == interaction.user.id

		running = True
		while running:
			try:
				interaction = await self.bot.wait_for("select_option", check=check, timeout=240)

			except asyncio.TimeoutError:
				await ctx.message.delete()
				await embed.delete()
				return

			await interaction.respond(type=6)

			if interaction.component[0].value == "Home":
				await interaction.message.edit(embed=home_embed)

			elif interaction.component[0].value == "Fun":
				fun_embed = discord.Embed(title=f"Fun Command List of {ctx.guild}",
									  description=f"Dice\n```YAML\n{ctx.prefix}dice <number>d<number>```"
									  			  f"Slap\n```YAML\n{ctx.prefix}slap <member> <reason>```"
												  f"Meme\n```YAML\n{ctx.prefix}meme```"
												  f"Fact\n```YAML\n{ctx.prefix}fact <animal>```",
									  color=ctx.author.color,
									  timestamp=datetime.utcnow())

				fun_embed.set_thumbnail(url=ctx.guild.icon_url)
				fun_embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

				await interaction.message.edit(embed=fun_embed)

			elif interaction.component[0].value == "Info":
				info_embed = discord.Embed(title=f"Info Command List of {ctx.guild}",
									  description=f"Userinfo\n```YAML\n{ctx.prefix}userinfo <target>```"
									  			  f"Serverinfo\n```YAML\n{ctx.prefix}serverinfo```",
									  color=ctx.author.color,
									  timestamp=datetime.utcnow())

				info_embed.set_thumbnail(url=ctx.guild.icon_url)
				info_embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

				await interaction.message.edit(embed=info_embed)

			elif interaction.component[0].value == "Lvl":
				if ctx.author.guild_permissions.manage_guild:
					lvl_embed = discord.Embed(title=f"Lvl Command List of {ctx.guild}",
										  description=f"Rank\n```YAML\n{ctx.prefix}rank <target>```"
										  			  f"Leaderboard\n```YAML\n{ctx.prefix}lb```"
													  f"lvlroles\n```YAML\n{ctx.prefix}lvlroles```"
													  f"addlvlrole\n```YAML\n{ctx.prefix}addlvlrole <lvl> <role>```"
													  f"removelvlrolen```YAML\n{ctx.prefix}removelvlrole <role>```",
										  color=ctx.author.color,
										  timestamp=datetime.utcnow())

				else:
					lvl_embed = discord.Embed(title=f"Lvl Command List of {ctx.guild}",
										  description=f"Rank\n```YAML\n{ctx.prefix}rank <target>```"
										  			  f"Leaderboard\n```YAML\n{ctx.prefix}lb```"
													  f"lvlroles\n```YAML\n{ctx.prefix}lvlroles```",
										  color=ctx.author.color,
										  timestamp=datetime.utcnow())

				lvl_embed.set_thumbnail(url=ctx.guild.icon_url)
				lvl_embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

				await interaction.message.edit(embed=lvl_embed)

			elif interaction.component[0].value == "Mod":
				mod_embed = discord.Embed(title=f"Mod Command List of {ctx.guild}",
									  description=f"Clear Messages\n```YAML\n{ctx.prefix}clear <member> <message limit>```"
									  			  f"Kick\n```YAML\n{ctx.prefix}kick <member> <reason>```"
									  			  f"Ban\n```YAML\n{ctx.prefix}ban <member> <Delete messages of the last ? days> <reason>```"
												  f"Unban\n```YAML\n{ctx.prefix}unban <user> <reason>```"
												  f"Mutelist\n```YAML\n{ctx.prefix}mutelist```"
												  f"Mute\n```YAML\n{ctx.prefix}mute <member> <10s/10m/10h/10d> <reason>```"
												  f"Unmute\n```YAML\n{ctx.prefix}unmute <member> <reason>```"
												  f"Warn\n```YAML\n{ctx.prefix}warn <member> <10s/10m/10h/10d> <reason>```"
												  f"Remove Warning\n```YAML\n{ctx.prefix}removewarn <member> <warn number>```"
												  f"Warns of an member\n```YAML\n{ctx.prefix}warns <member>```"
												  f"Custom Embed\n```YAML\n{ctx.prefix}customembed <title> <body>```",
									  color=ctx.author.color,
									  timestamp=datetime.utcnow())

				mod_embed.set_thumbnail(url=ctx.guild.icon_url)
				mod_embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

				await interaction.message.edit(embed=mod_embed)

			elif interaction.component[0].value == "Sett":
				settings_embed = discord.Embed(title=f"Bot Settings Command List of {ctx.guild}",
									  description=f"Prefix\n```YAML\n{ctx.prefix}prefix <target>```"
									  			  f"Set Bot activity\n```YAML\n{ctx.prefix}setactivity <playing/listening/watching/streaming> <text>```"
												  "Use {users,} for a user Count."
												  f"Join to Create\n```YAML\n{ctx.prefix}jointocreate```"
												  f"Set Roster\n```YAML\n{ctx.prefix}setroster <Channel> <roles>```"
												  f"Delete Roster\n```YAML\n{ctx.prefix}delroster```"
												  f"Set Welcomer\n```YAML\n{ctx.prefix}setwelcomer <Channel> <message>```"
												  "Use {member} as the name of the new member"
												  f"Remove Welcomer\n```YAML\n{ctx.prefix}removewelcomer```"
												  f"Set DM Welcomer\n```YAML\n{ctx.prefix}setdmwelcomer <message>```"
												  "Use {member} as the name of the new member"
												  f"Remove DM Welcomer\n```YAML\n{ctx.prefix}removedmwelcomer```"
												  f"Add Custom Command\n```YAML\n{ctx.prefix}addcommand <command name> <answer>```"
												  f"Remove Custom Command\n```YAML\n{ctx.prefix}removecommand <command name>```"
												  f"Set Modmail/Apply System\n```YAML\n{ctx.prefix}setmodmail <Channel>```"
												  f"Set Applys\n```YAML\n{ctx.prefix}addapply <Submit Channel> <Apply Message ID> <Application Name> <Apply Emoji (has to be an custom server emoji!)>```",

									  color=ctx.author.color,
									  timestamp=datetime.utcnow())

				settings_embed.set_thumbnail(url=ctx.guild.icon_url)
				settings_embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

				await interaction.message.edit(embed=settings_embed)

			elif interaction.component[0].value == "Stop":
				await interaction.message.delete()
				running = False



		await ctx.message.delete()


	@Cog.listener()
	async def on_ready(self):
		DiscordComponents(self.bot)
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("help")


def setup(bot):
	bot.add_cog(Help(bot))
