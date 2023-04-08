import discord
import asyncio

from discord import Member, Embed, NotFound
from discord.ext.commands import Cog, EmojiNotFound, ChannelNotFound

from datetime import datetime

from discord.ext.commands import command, has_permissions

from ..db import db

class Modmail(Cog):
	def __init__(self, bot):
		self.bot = bot


	@command(name="setmodmail")
	async def set_modmail_embed_command(self, ctx, channel: discord.TextChannel):

		try:
			channel = ctx.guild.get_channel(channel.id)

		except ChannelNotFound:
			await ctx.send("Channel not found.")
			return


		embed = Embed(title=f"{ctx.guild} Application setup",
                      description="Application setup starting ...",
 					  colour=ctx.author.colour,
 					  timestamp=datetime.utcnow())

		embed_message = await ctx.send(embed=embed)

		new_embed = Embed(description="Enter a RGB colour for the Embed.")

		await embed_message.edit(embed=new_embed)

		def checkM(m):
			return m.author.bot is False and m.channel.id == ctx.channel.id


		msg = await self.bot.wait_for("message", check=checkM, timeout=1200)
		await msg.delete(delay=2)
		colourpre = msg.content

		colourfin = colourpre.replace("#", "0x")

		colourfin = int(colourfin, 0)

		new_embed = Embed(description="Enter now the Applictaion Title.", colour=colourfin)

		await embed_message.edit(embed=new_embed)


		msg = await self.bot.wait_for("message", check=checkM, timeout=1200)
		await msg.delete(delay=2)
		title = msg.content


		new_embed = Embed(description="Enter now the Applictaion Description.", colour=colourfin)

		await embed_message.edit(embed=new_embed)

		msg = await self.bot.wait_for("message", check=checkM, timeout=1200)
		await msg.delete(delay=2)
		description = msg.content

		embed = Embed(title=title,
                      description=description,
 					  colour=colourfin,
 					  timestamp=datetime.utcnow())

		await embed_message.edit(embed=embed)


		embed = Embed(title=f"{ctx.guild} Application setup",
                      description="Do you want to confirm the the Application Embed?",
 					  colour=colourfin,
 					  timestamp=datetime.utcnow())

		confirmation = await ctx.send(embed=embed)

		await confirmation.add_reaction("\U00002705")
		await confirmation.add_reaction("\U0000274c")

		def checkYN(reaction, user):
			return user.bot is False and reaction.message.id == confirmation.id and str(reaction.emoji) in ["\U00002705", "\U0000274c"]

		reaction, user = await self.bot.wait_for("reaction_add", check=checkYN, timeout=120)

		if str(reaction) == "\U00002705":

			embed = Embed(title=title,
	                      description=description,
	 					  colour=colourfin,
	 					  timestamp=datetime.utcnow())

			channel_embed = await channel.send(embed=embed)

			prefix = ctx.prefix
			new_embed = Embed(description="Applictaion Setup confirmed.")

			new_embed.add_field(name="Next Step", value=f"Use `{prefix}addapply <Application MessageID> <Emoji>` to add the apply choices.", inline=True)

			await confirmation.edit(embed=new_embed)

			await confirmation.clear_reactions()

		elif str(reaction) == "\U0000274c":
			new_embed = Embed(description="Stopped the Applictaion Setup.")
			await embed_message.edit(embed=new_embed)
			await confirmation.delete(delay=5)

	@command(name="addapply")
	async def addapply_command(self, ctx, submit_channel: discord.TextChannel, apply_message_id, apply_name, emoji: discord.Emoji):

		question_wait = True

		counter = 0

		q_list = []

		embed = Embed(title=f"Question Setup for {emoji}",
					  description=f"Starting Question query...",
					  colour=0x2f3136,
					  timestamp=datetime.utcnow())

		QEmbed = await ctx.send(embed=embed)

		while question_wait:

			counter = counter + 1

			embed = Embed(title=f"Question Setup for {emoji}",
	                      description=f"Send your {counter}. Question which should be asked to applicant or type `stop` to stop adding questions.",
	 					  colour=0x2f3136,
	 					  timestamp=datetime.utcnow())

			await QEmbed.edit(embed=embed)


			def checkM(m):
				return m.author.bot is False and m.channel.id == ctx.channel.id

			question = await self.bot.wait_for("message", check=checkM, timeout=1200)
			await question.delete(delay=2)
			if question.content == "stop":
				question_wait = False

			else:
				q_list.append(question.content)


		embed = Embed(title=f"Question Setup for {emoji}",
					  description=f"Finished the Question query.\nDo you want to confirm these Questions?",
					  colour=0x2f3136,
					  timestamp=datetime.utcnow())

		await QEmbed.edit(embed=embed)


		await QEmbed.add_reaction("\U00002705")
		await QEmbed.add_reaction("\U0000274c")

		def checkYN(reaction, user):
			return user.bot is False and reaction.message.id == QEmbed.id and str(reaction.emoji) in ["\U00002705", "\U0000274c"]

		reaction, user = await self.bot.wait_for("reaction_add", check=checkYN, timeout=120)


		if str(reaction) == "\U00002705":


			q_list = ", ".join(q_list)

			apply_message = None

			while apply_message == None:
				for channel in ctx.guild.channels:
					try:
						apply_message = await channel.fetch_message(apply_message_id)

					except:
						pass

			await apply_message.add_reaction(emoji)

			db.execute("INSERT INTO modmail VALUES (?, ?, ?, ?, ?, ?)", ctx.guild.id, apply_message_id, submit_channel.id, apply_name, emoji.name, q_list)

			embed = Embed(title=f"Question Setup for {emoji}",
						  description="All Questions got saved and applied.",
						  colour=0x2f3136,
						  timestamp=datetime.utcnow())

			await QEmbed.edit(embed=embed)


		elif str(reaction) == "\U0000274c":

			embed = Embed(title=f"Question Setup for {emoji}",
						  description="Stopped Question Setup and removed all Questions.",
						  colour=0x2f3136,
						  timestamp=datetime.utcnow())

			await QEmbed.edit(embed=embed)



	@addapply_command.error
	async def addapply_command_error(self, ctx, error):
		if isinstance(error, EmojiNotFound):
			await ctx.send("Emoji not Found")


	@Cog.listener("on_raw_reaction_add")
	async def apply_check_event(self, payload):
		try:
			if payload.member.bot:
				return

		except AttributeError:
			return

		try:
			apply_name = db.field("SELECT Apply_Name FROM modmail WHERE GuildID = ? AND MessageID = ? AND Emoji = ?", payload.guild_id, payload.message_id, payload.emoji.name)
			Submit_Channel_ID = db.field("SELECT submit_channel FROM modmail WHERE GuildID = ? AND MessageID = ? AND Emoji = ?", payload.guild_id, payload.message_id, payload.emoji.name)
			Questions = db.record("SELECT Questions FROM modmail WHERE GuildID = ? AND MessageID = ? AND Emoji = ?", payload.guild_id, payload.message_id, payload.emoji.name)

		except:
			raise
			return

		if Submit_Channel_ID == None:
			return

		else:
			def checkM(m):
				return m.author == member and m.channel == dm.channel

			member = payload.member
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
			user = await self.bot.fetch_user(payload.user_id)

			await message.remove_reaction(payload.emoji, user)


			final_embed = discord.Embed(title="**Application**",
									  	description=f"{member} applied as {apply_name}",
									  	color=member.color,
									  	timestamp=datetime.utcnow())

			final_embed.add_field(name = "Status", value = "Unprocessed", inline = False)

			final_embed.set_thumbnail(url=member.avatar_url)
			final_embed.set_footer(text=f"Application from {member}")

			Questions = Questions[0]
			Questions = Questions.split(",")

			for question in Questions:
				embed = discord.Embed(title=f"**{apply_name} Application**",
									  description=f"**{question}**",
									  color=member.color,
									  timestamp=datetime.utcnow())

				embed.set_footer(text=f"Application for {member}")

				dm = await member.send(embed = embed)
				msg = await self.bot.wait_for("message", check = checkM, timeout=1200)
				final_embed.add_field(name = question, value = msg.content, inline = False)
				await asyncio.sleep(0.1)


			submit_wait = True
			while submit_wait:
				embed = discord.Embed(title=f"**{apply_name} Application**",
									  description="**Willst du deine Anfrage so Weitergeleiten?**" ,
									  color=member.color,
									  timestamp=datetime.utcnow())
				embed.set_footer(text="Reagiere mit ✅ oder ❌!")
				message = await member.send(embed = embed)
				await message.add_reaction("\U00002705")
				await message.add_reaction("\U0000274c")

				def checkYN(reaction, user):
					return reaction.message.channel == message.channel and user == member and str(reaction.emoji) in ["\U00002705", "\U0000274c"]

				reaction, user = await self.bot.wait_for("reaction_add", check=checkYN, timeout=120)

				if str(reaction.emoji) == "\U00002705":
					submit_wait = False

					Submit_Channel = self.bot.get_channel(Submit_Channel_ID)

					submission = await Submit_Channel.send(embed=final_embed)

					await submission.add_reaction("\U00002705")
					await submission.add_reaction("\U0000274c")

					db.execute("INSERT INTO modmail_submissions VALUES (?, ?, ?, ?)", payload.guild_id, submission.id, member.id, apply_name)

					embed = discord.Embed(title=f"**{apply_name} Application**", description="**Deine Anfrage wurde Weitergeleitet!**" , color=discord.Color.green())
					await message.edit(embed = embed)

				if str(reaction.emoji) == "\U0000274c":
					submit_wait = False
					embed = discord.Embed(title=f"**{apply_name} Application**", description="**Deine Anfrage wurde Abgebrochen!**" , color=discord.Color.red())
					await message.edit(embed = embed)


	@Cog.listener("on_raw_reaction_add")
	async def submission_check_event(self, payload):
		try:
			if payload.member.bot:
				return

		except AttributeError:
			return

		try:
			ApplicantID = db.field("SELECT ApplicantID FROM modmail_submissions WHERE GuildID = ? AND MessageID = ?", payload.guild_id, payload.message_id)
			Application_Name = db.field("SELECT Application_Name FROM modmail_submissions WHERE GuildID = ? AND MessageID = ?", payload.guild_id, payload.message_id)
		except:
			return

		if ApplicantID == None:
			return

		channel = await self.bot.fetch_channel(payload.channel_id)
		submission = await channel.fetch_message(payload.message_id)
		guild = self.bot.get_guild(payload.guild_id)
		member = guild.get_member(ApplicantID)

		if str(payload.emoji) == "\U00002705":
			embed = discord.Embed(title=f"{Application_Name} Application Update",
								  description=f"**Your application as {Application_Name} on the {guild} Discord got accepted.\n Contact {payload.member} for further instructions**",
								  color=discord.Color.red(),
								  timestamp=datetime.utcnow())

			embed.set_footer(text=f"Application for {member}")

			await member.send(embed=embed)

			db.execute("DELETE FROM modmail_submissions WHERE GuildID = ? AND MessageID = ?", payload.guild_id, payload.message_id)

			embed = submission.embeds
			embed = embed[0]

			embed.set_field_at(0, name=f"Status", value=f"✅ Accepted by {payload.member}")
			await submission.edit(embed=embed)

		if str(payload.emoji) == "\U0000274c":
			embed = discord.Embed(title=f"{Application_Name} Application Update",
								  description=f"**Your application as {Application_Name} on the {guild} Discord got declined.**",
								  color=discord.Color.green(),
								  timestamp=datetime.utcnow())

			embed.set_footer(text=f"Application for {member}")

			db.execute("DELETE FROM modmail_submissions WHERE GuildID = ? AND MessageID = ?", payload.guild_id, payload.message_id)

			await member.send(embed=embed)
			await submission.delete()



	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("modmail")


def setup(bot):
	bot.add_cog(Modmail(bot))
