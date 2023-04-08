import discord
import asyncio
import sqlite3

from asyncio import sleep
from typing import Optional
from datetime import datetime, timedelta

from discord import Member, Embed, NotFound
from discord.ext import tasks
from discord.ext.commands import Cog, Greedy, Converter
from discord.ext.commands import CheckFailure, BadArgument
from discord.ext.commands import command, has_permissions, bot_has_permissions

from ..db import db

class TimeConverter(Converter):
	async def convert(self, ctx, argument):
		try:
			timedef = argument[-1]
			timelen = argument[:-1]
			time_convert = {"s":1, "m":60, "h":3600, "d":86400}

			time_sort_convert = {"s": "Seconds", "m": "Minutes", "h": "Hours", "d": "Days"}

			time_end = int(timelen) * time_convert[timedef]

			end_time = datetime.utcnow() + timedelta(seconds=time_end)

			timedef = time_sort_convert[timedef]

			return argument

		except Exception as E:
			raise BadArgument


class Mod(Cog):
	def __init__(self, bot):
		self.bot = bot

		self.bot.loop.create_task(self.mute_check())
		self.bot.loop.create_task(self.warn_check())

	async def kick_members(self, message, targets, reason):
		for target in targets:
			if (message.guild.me.top_role.position > target.top_role.position
				and not target.guild_permissions.administrator):
				await target.kick(reason=reason)

				embed = Embed(title="Member kicked",
							  colour=0xDD2222,
							  timestamp=datetime.utcnow())

				embed.set_thumbnail(url=target.avatar_url)

				fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
						  ("Actioned by", message.author.display_name, False),
						  ("Reason", reason, False)]

				for name, value, inline in fields:
					embed.add_field(name=name, value=value, inline=inline)

				await self.log_channel.send(embed=embed)

	@command(name="kick")
	@bot_has_permissions(kick_members=True)
	@has_permissions(kick_members=True)
	async def kick_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
		if not len(targets):
			await ctx.send("One or more required arguments are missing.")

		else:
			await self.kick_members(ctx.message, targets, reason)
			await ctx.send("Action complete.")

	@kick_command.error
	async def kick_command_error(self, ctx, exc):
		if isinstance(exc, CheckFailure):
			await ctx.send("Insufficient permissions to perform that task.")

	async def ban_members(self, message, targets, reason):
		for target in targets:
			await target.ban(reason=reason)
			print(await message.guild.bans())

			embed = Embed(title="Member banned",
						  colour=0xDD2222,
						  timestamp=datetime.utcnow())

			embed.set_thumbnail(url=target.avatar_url)

			fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
					  ("Actioned by", message.author.display_name, False),
					  ("Reason", reason, False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)

			try:
				log_channel_id = db.field("SELECT mod_log_channel FROM mod_log WHERE GuildID = ?", message.guild.id)
				log_channel = message.guild.get_channel(log_channel_id)
				await self.log_channel.send(embed=embed)

			except:
				pass

	@command(name="ban2")
	@bot_has_permissions(ban_members=True)
	@has_permissions(ban_members=True)
	async def ban2_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
		if not len(targets):
			await ctx.send("One or more required arguments are missing.")

		else:
			await self.ban_members(ctx.message, targets, reason)
			await ctx.send("Action complete.")

	@ban2_command.error
	async def ban2_command_error(self, ctx, exc):
		if isinstance(exc, CheckFailure):
			await ctx.send("Insufficient permissions to perform that task.")


	@command(name="ban")
	@bot_has_permissions(ban_members=True)
	@has_permissions(ban_members=True)
	async def ban_command(self, ctx, targets: Greedy[discord.User], days: Optional[int] = 1, *, reason: Optional[str] = "No reason provided."):
		if days > 7:
			days = 7
		print(targets)
		for target in targets:
			try:
				await ctx.guild.fetch_ban(target)
				embed = discord.Embed(title=f"❌ Failed to bann {target.name}.",
									  color=discord.Color.red(),
									  timestamp=datetime.utcnow())

				embed.description=f"> **Reason:** {target} is already banned."
				embed.set_footer(text=f"{target.name}", icon_url=target.avatar_url)
				await ctx.send(embed=embed)

			except NotFound:
				await ctx.guild.ban(target, reason=reason, delete_message_days=days)
				embed = discord.Embed(title=f"✅ Successfully banned {target.name}.",
									  color=discord.Color.green(),
									  timestamp=datetime.utcnow())
				if days == 1:
					embed.description=f"> **Banned:** {target}  **/**  {target.id}\n> **Reason:** {reason}\n> Deleted all messages of {target} from the last day."

				else:
					embed.description=f"> **Banned:** {target}  **/**  {target.id}\n> **Reason:** {reason}\n> Deleted all messages of {target} from the last {days} days"

				embed.set_footer(text=f"{target.name}", icon_url=target.avatar_url)
				await ctx.send(embed=embed)

	@command(name="unban")
	@bot_has_permissions(ban_members=True)
	@has_permissions(ban_members=True)
	async def unban_command(self, ctx, targets: Greedy[discord.User], *, reason: Optional[str] = "No reason provided."):
		for target in targets:
			try:
				await ctx.guild.fetch_ban(target)
				await ctx.guild.unban(target, reason=reason)
				embed = discord.Embed(title=f"✅ Successfully unbanned {target.name}.",
									  color=discord.Color.green(),
									  timestamp=datetime.utcnow())

				embed.description=f"> **Unbanned:** {target}  **/**  {target.id}\n> **Reason:** {reason}"
				embed.set_footer(text=f"{target.name}", icon_url=target.avatar_url)

				await ctx.send(embed=embed)

			except NotFound:
				embed = discord.Embed(title=f"❌ Failed to unbann {target.name}.",
									  color=discord.Color.red(),
									  timestamp=datetime.utcnow())

				embed.description=f"> **Reason:** {target} is not banned."
				embed.set_footer(text=f"{target.name}", icon_url=target.avatar_url)
				await ctx.send(embed=embed)


	@command(name="clear", aliases=["purge"])
	@bot_has_permissions(manage_messages=True)
	@has_permissions(manage_messages=True)
	async def clear_messages(self, ctx, targets: Greedy[Member], limit: Optional[int] = 1):
		def _check(message):
			return not len(targets) or message.author in targets

		if 0 < limit <= 300:
			with ctx.channel.typing():
				await ctx.message.delete()
				deleted = await ctx.channel.purge(limit=limit, after=datetime.utcnow()-timedelta(days=14),
												  check=_check)

				await ctx.send(f"Deleted {len(deleted):,} messages.", delete_after=5)

		else:
			await ctx.send("The limit provided is not within acceptable bounds.")


############################################# MUTE #############################################
	@command(name="setmute")
	@has_permissions(kick_members=True)
	async def setmutedrole_command(self, ctx, role: discord.Role):
		try:
			db.execute("INSERT INTO muterole VALUES (?, ?)", ctx.guild.id, role.id)
			await ctx.send("Successfully set muted role.")

		except sqlite3.IntegrityError:
			await ctx.send("You already defined a mute role.")

	@command(name="mutelist")
	@has_permissions(kick_members=True)
	async def mutelist_command(self, ctx):

		format = "%Y:%m:%d:%H:%M:%S"

		embed = Embed(title = "Mute List",
					  description = f"All muted Members are listed below",
					  colour=0x2f3136,
					  timestamp=datetime.utcnow())


		MemberIDs = db.record("SELECT UserID FROM mutes WHERE GuildID = ?", ctx.guild.id)
		if MemberIDs != None:
			muted_role_id = db.field("SELECT RoleID FROM muterole WHERE GuildID = ?", ctx.guild.id)
			muted_role = ctx.guild.get_role(muted_role_id)

			for MemberID in MemberIDs:
				member = ctx.guild.get_member(MemberID)
				if muted_role not in member.roles:
					try:
						db.execute("DELETE FROM mutes WHERE GuildID = ? AND UserID = ?", ctx.guild.id, member.id)
						db.commit()

					except:
						pass

		MemberID_EndTime_Reason = db.records("SELECT UserID, EndTime, Reason FROM mutes WHERE GuildID = ?", ctx.guild.id)

		for MemberID, EndTime, Reason in MemberID_EndTime_Reason:

			if EndTime == "Until unmute":
				pass

			else:
				EndTime = datetime.strptime(EndTime, format)

			member = ctx.guild.get_member(MemberID)

			embed.add_field(name=f"{member}",
							value=f"**Reason: **{Reason}\n**End Time: **{EndTime}",
							inline=False
							)

		await ctx.send(embed=embed)

	@command(name="mute")
	@has_permissions(kick_members=True)
	async def mute_command(self, ctx, targets: Greedy[discord.User], time: Optional[TimeConverter], *, reason: Optional[str] = "No reason provided."):
		muted_role_id = db.field("SELECT RoleID FROM muterole WHERE GuildID = ?", ctx.guild.id)

		if muted_role_id == None:
			await ctx.send(f"Before you are able to perform this command you had to define the mute role with: `{ctx.prefix}setmute @role`.")
			return

		if not targets:
			embed = Embed(title = "**Error**",
						  description = f"❌ You have to tag a member.\n`{ctx.prefix}mute <member> <mute lenght> <reason>`",
						  colour=discord.Color.red(),
						  timestamp=datetime.utcnow())

			await ctx.send(embed=embed)

		else:
			muted_role = ctx.guild.get_role(muted_role_id)
			if time == None:

				for target in targets:
					target_name = target
					target = ctx.guild.get_member(target.id)
					if target != None:

						await target.add_roles(muted_role)

						try:
							db.execute("INSERT INTO mutes VALUES (?, ?, ?, ?)", target.id, ctx.guild.id, "Until unmute", reason)

						except sqlite3.IntegrityError:
							embed = Embed(title = "**Error**",
										  description = f"❌ {target} is already muted.",
										  colour=discord.Color.red(),
										  timestamp=datetime.utcnow())

							await ctx.send(embed=embed)
							return


						embed = Embed(description = f"✅ **{target.display_name}#{target.discriminator}** muted successfuly\n> **Reason:** {reason}\n> **Duration:** Until unmute",
									  colour=discord.Color.green(),
									  timestamp=datetime.utcnow())

						await ctx.send(embed=embed)

					elif target == None:
						embed = Embed(title = "**Error**",
									  description = f"❌ {target_name} is not in this guild.",
									  colour=discord.Color.red(),
									  timestamp=datetime.utcnow())

						await ctx.send(embed=embed)

			else:
				timedef = time[-1]
				timelen = time[:-1]
				time_convert = {"s":1, "m":60, "h":3600, "d":86400}

				time_sort_convert = {"s": "Seconds", "m": "Minutes", "h": "Hours", "d": "Days"}

				time_end = int(timelen) * time_convert[timedef]

				end_time = datetime.utcnow() + timedelta(seconds=time_end)

				timedef = time_sort_convert[timedef]

				for target in targets:
					target_name = target
					target = ctx.guild.get_member(target.id)
					if target != None:
						try:
							db.execute("INSERT INTO mutes VALUES (?, ?, ?, ?)", target.id, ctx.guild.id, end_time.strftime("%Y:%m:%d:%H:%M:%S"), reason)

							await target.add_roles(muted_role)
							embed = Embed(description = f"✅ **{target.display_name}#{target.discriminator}** muted successfuly\n> **Reason:** {reason}\n> **Duration:** {timelen} {timedef}",
										  colour=discord.Color.green(),
										  timestamp=datetime.utcnow())

							await ctx.send(embed=embed)

							self.bot.loop.create_task(self.sleep_unmute(time_end, muted_role, target))

						except sqlite3.IntegrityError:
							embed = Embed(title = "**Error**",
										  description = f"❌ {target} is already muted.",
										  colour=discord.Color.red(),
										  timestamp=datetime.utcnow())

							await ctx.send(embed=embed)

					elif target == None:
						embed = Embed(title = "**Error**",
									  description = f"❌ {target_name} is not in this guild.",
									  colour=discord.Color.red(),
									  timestamp=datetime.utcnow())

						await ctx.send(embed=embed)

	async def sleep_unmute(self, time_end, muted_role, target):
		await sleep(time_end)

		await target.remove_roles(muted_role)
		db.execute("DELETE FROM mutes WHERE GuildID = ? AND UserID = ?", target.guild.id, target.id)


	@command(name="unmute")
	@has_permissions(kick_members=True)
	async def unmute_command(self, ctx, targets: Greedy[discord.User], *, reason: Optional[str] = "No reason provided."):

		muted_role_id = db.field("SELECT RoleID FROM muterole WHERE GuildID = ?", ctx.guild.id)

		if muted_role_id == None:
			await ctx.send("No muted role defined.")
			return

		if not targets:
			embed = Embed(title = "**Error**",
						  description = f"❌ You have to tag a member.\n`{ctx.prefix}unmute <member> <reason>`",
						  colour=discord.Color.red(),
						  timestamp=datetime.utcnow())

			await ctx.send(embed=embed)

		else:
			muted_role = ctx.guild.get_role(muted_role_id)


			for target in targets:
				target_name = target
				target = ctx.guild.get_member(target.id)
				if target != None:
					if muted_role not in target.roles:
						embed = Embed(description = f"❌ **{target.display_name}#{target.discriminator}** is not muted",
									  colour=discord.Color.red(),
									  timestamp=datetime.utcnow())

						await ctx.send(embed=embed)
						try:
							db.execute("DELETE FROM mutes WHERE GuildID = ? AND UserID = ?", ctx.guild.id, target.id)

						except:
							pass


					else:

						try:
							db.execute("DELETE FROM mutes WHERE GuildID = ? AND UserID = ?", ctx.guild.id, target.id)

						except:
							pass

						await target.remove_roles(muted_role)

						embed = Embed(description = f"✅ **{target.display_name}#{target.discriminator}** unmuted successfuly\n> **Reason:** {reason}",
									  colour=discord.Color.green(),
									  timestamp=datetime.utcnow())

						await ctx.send(embed=embed)

				elif target == None:
					embed = Embed(title = "**Error**",
								  description = f"❌ {target_name} is not in this guild.",
								  colour=discord.Color.red(),
								  timestamp=datetime.utcnow())

					await ctx.send(embed=embed)

	async def wait_for_unmute(self, time, UserID, GuildID, EndTime, muted_role_id):
		await sleep(time.seconds)

		guild = self.bot.get_guild(GuildID)
		muted_role = guild.get_role(muted_role_id)

		member = guild.get_member(UserID)

		await member.remove_roles(muted_role)

	async def mute_check(self):
		await self.bot.wait_until_ready()

		UserID_GuildID_Endtime = db.records("SELECT UserID, GuildID, EndTime FROM mutes")

		for UserID, GuildID, EndTime in UserID_GuildID_Endtime:

			muted_role_id = db.field("SELECT RoleID FROM muterole WHERE GuildID = ?", GuildID)

			if muted_role_id == None:
				return

			if EndTime == "Until unmute":
				pass

			else:
				TimeNow = datetime.utcnow().strftime("%Y:%m:%d:%H:%M:%S")

				format = '%Y:%m:%d:%H:%M:%S'

				if datetime.strptime(EndTime, format) <= datetime.strptime(TimeNow, format):
					guild = self.bot.get_guild(GuildID)
					muted_role = guild.get_role(muted_role_id)

					member = guild.get_member(UserID)

					await member.remove_roles(muted_role)

					db.execute("DELETE FROM mutes WHERE GuildID = ? AND UserID = ?", GuildID, UserID)

				else:
					rest_time = datetime.strptime(EndTime, format) - datetime.strptime(TimeNow, format)

					asyncio.create_task(self.wait_for_unmute(rest_time, UserID, GuildID, EndTime, muted_role_id))

	@Cog.listener("on_member_update")
	async def unmute_check(self, before, after):
		if before.roles != after.roles:
			muted_role_id = db.field("SELECT RoleID FROM muterole WHERE GuildID = ?", before.guild.id)
			muted_role = before.guild.get_role(muted_role_id)
			if muted_role in before.roles and muted_role not in after.roles:
				try:
					db.execute("DELETE FROM mutes WHERE GuildID = ? AND UserID = ?", before.guild.id, before.id)
					db.commit()

				except:
					pass


############################################# WARN #############################################

	@command(name="warn")
	@has_permissions(kick_members=True)
	async def warn_command(self, ctx, targets: Greedy[Member], time: Optional[TimeConverter], *, reason):

		if not len(targets):
			await ctx.send("One or more required arguments are missing.")

		else:

			if time == None:

				for target in targets:

					Counter = db.execute("SELECT max(Counter) FROM warns WHERE GuildID = ? AND UserID = ?", ctx.guild.id, target.id)

					if Counter == None:
						Counter = 1

					else:
						Counter = Counter + 1

					db.execute("INSERT INTO warns VALUES (?, ?, ?, ?, ?)", target.id, ctx.guild.id, "Until remove", reason, Counter)

					embed = Embed(description = f"✅ **{target.display_name}#{target.discriminator}** warned successfuly\n> **Reason:** {reason}\n> **Duration:** Until remove",
								  colour=discord.Color.green(),
								  timestamp=datetime.utcnow())

					await ctx.send(embed=embed)

			else:
				timedef = time[-1]
				timelen = time[:-1]
				time_convert = {"s":1, "m":60, "h":3600, "d":86400}

				time_sort_convert = {"s": "Seconds", "m": "Minutes", "h": "Hours", "d": "Days"}

				time_end = int(timelen) * time_convert[timedef]

				end_time = datetime.utcnow() + timedelta(seconds=time_end)

				timedef = time_sort_convert[timedef]

				for target in targets:

					Counter = db.records("SELECT Counter FROM warns WHERE GuildID = ? AND UserID = ?", ctx.guild.id, target.id)

					if Counter == None:
						Counter = 1

					else:
						Counter = len(Counter) + 1

					db.execute("INSERT INTO warns VALUES (?, ?, ?, ?, ?)", target.id, ctx.guild.id, end_time.strftime("%Y:%m:%d:%H:%M:%S"), reason, Counter)

					embed = Embed(description = f"✅ **{target.display_name}#{target.discriminator}** warned successfuly\n> **Reason:** {reason}\n> **Duration:** {timelen} {timedef}",
								  colour=discord.Color.green(),
								  timestamp=datetime.utcnow())

					await ctx.send(embed=embed)

					self.bot.loop.create_task(self.sleep_removewarn(time_end, target, Counter))

	async def sleep_removewarn(self, time_end, target, Counter):
		await sleep(time_end)

		db.execute("DELETE FROM warns WHERE GuildID = ? AND UserID = ? AND Counter = ?", target.guild.id, target.id, Counter)

	@command(name="removewarn")
	@has_permissions(kick_members=True)
	async def remove_warn_command(self, ctx, targets: Greedy[Member], warn_number):

		for target in targets:
			reason = db.execute("SELECT Reason FROM warns WHERE GuildID = ? AND UserID = ? AND Counter = ?", ctx.guild.id, target.id, warn_number)
			try:
				db.execute("DELETE FROM warns WHERE AND UserID = ? GuildID = ? AND Counter = ?", ctx.guild.id, target.id, warn_number)

			except:
				embed = Embed(description = f"❌ Warning for **{target.display_name}#{target.discriminator}** doesnt exist.",
							  colour=discord.Color.red(),
							  timestamp=datetime.utcnow())

				await ctx.send(embed=embed)

			embed = Embed(description = f"✅ **{target.display_name}#{target.discriminator}** removed warn {warn_number} successfuly\n> **Original Reason:** {reason}",
						  colour=discord.Color.green(),
						  timestamp=datetime.utcnow())

			await ctx.send(embed=embed)

	@command(name="warns")
	@has_permissions(kick_members=True)
	async def warns_of_command(self, ctx, targets: Greedy[Member]):

		format = "%Y:%m:%d:%H:%M:%S"

		for target in targets:
			embed = Embed(title = f"Warn List",
						  description = f"All warns of {target} are listed bellow.",
						  colour=0x2f3136,
						  timestamp=datetime.utcnow())

			EndTime_Reason_Counter = db.records("SELECT EndTime, Reason, Counter FROM warns WHERE GuildID = ? AND UserID = ? ORDER BY Counter ASC", ctx.guild.id, target.id)

			for EndTime, Reason, Counter in EndTime_Reason_Counter:

				if EndTime == "Until remove":
					pass

				else:
					EndTime = datetime.strptime(EndTime, format)

				embed.add_field(name=f"{target}",
								value=f"**Reason: **{Reason}\n**End Time: **{EndTime}\n**Warn ID:** {Counter}",
								inline=False
								)

			if len(EndTime_Reason_Counter) == 1:
				embed.set_footer(text=f"{target} has {len(EndTime_Reason_Counter)} warning.")

			else:
				embed.set_footer(text=f"{target} has {len(EndTime_Reason_Counter)} warnings.")

			await ctx.send(embed=embed)


	async def wait_for_removewarn(self, time, UserID, GuildID, EndTime, Counter):
		await sleep(time.seconds)

		guild = self.bot.get_guild(GuildID)

		member = guild.get_member(UserID)

		db.execute("DELETE FROM warns WHERE GuildID = ? AND UserID = ? AND Counter = ?", ctx.guild.id, member.id, Counter)

	async def warn_check(self):
		await self.bot.wait_until_ready()

		UserID_GuildID_Endtime_Counter = db.records("SELECT UserID, GuildID, EndTime, Counter FROM warns")

		for UserID, GuildID, EndTime, Counter in UserID_GuildID_Endtime_Counter:

			if EndTime == "Until remove":
				pass

			else:
				TimeNow = datetime.utcnow().strftime("%Y:%m:%d:%H:%M:%S")

				format = '%Y:%m:%d:%H:%M:%S'

				if datetime.strptime(EndTime, format) <= datetime.strptime(TimeNow, format):
					guild = self.bot.get_guild(GuildID)

					member = guild.get_member(UserID)

					db.execute("DELETE FROM warns WHERE GuildID = ? AND UserID = ? AND Counter = ?", GuildID, UserID, Counter)

				else:
					rest_time = datetime.strptime(EndTime, format) - datetime.strptime(TimeNow, format)

					asyncio.create_task(self.wait_for_removewarn(rest_time, UserID, GuildID, EndTime, Counter))

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("mod")

def setup(bot):
	bot.add_cog(Mod(bot))
