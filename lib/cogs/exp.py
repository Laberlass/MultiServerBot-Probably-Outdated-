import requests
import discord
import io

from PIL import Image,ImageFont,ImageDraw,ImageOps
from io import BytesIO

from datetime import datetime, timedelta
from random import randint
from typing import Optional
from numerize import numerize

from discord import Member, Embed
from discord.ext import commands
from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions
from discord.ext.commands import RoleNotFound
from discord.ext.menus import MenuPages, ListPageSource

from ..db import db

class HelpMenu(ListPageSource):
	def __init__(self, ctx, data):
		self.ctx = ctx

		super().__init__(data, per_page=10)

	async def write_page(self, menu, offset, fields=[]):
		len_data = len(self.entries)

		embed = Embed(title="XP Leaderboard",
					  colour=self.ctx.author.colour)
		embed.set_thumbnail(url=self.ctx.guild.icon_url)
		embed.set_footer(text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} members.")

		for name, value in fields:
			embed.add_field(name=name, value=value, inline=False)

		return embed

	async def format_page(self, menu, entries):
		offset = (menu.current_page*self.per_page) + 1

		fields = []
		table = ("\n".join(f"{idx+offset}. {self.ctx.guild.get_member(entry[0]).display_name} (XP: {entry[1]} | Level: {entry[2]})"
				for idx, entry in enumerate(entries)))

		fields.append(("Ranks", table))

		return await self.write_page(menu, offset, fields)

class Exp(Cog):
	def __init__(self, bot):
		self.bot = bot

	async def process_xp(self, message):
		xp, lvl, xplock = db.record("SELECT XP, Level, XPLock FROM exp WHERE UserID = ? AND GuildID = ?", message.author.id, message.guild.id)

		if datetime.utcnow() > datetime.fromisoformat(xplock):
			await self.add_exp(message, xp, lvl)

	async def add_exp(self, message, xp, lvl):
		xp_to_add = randint(5, 10)
		new_lvl = int(((xp+xp_to_add)/42) ** 0.55)

		db.execute("UPDATE exp SET XP = XP + ?, Level = ?, XPLock = ? WHERE UserID = ? AND GuildID = ?", xp_to_add, new_lvl, (datetime.utcnow()+timedelta(seconds=10)).isoformat(), message.author.id, message.guild.id)

		if new_lvl > lvl:
			try:
				lvl_up_channel = self.bot.get_channel(846117954407104553)
				await lvl_up_channel.send(f"Congrats {message.author.mention} - you reached Level {new_lvl:,}!")

			except:
				pass
			await self.check_lvl_rewards(message, new_lvl)

	async def check_lvl_rewards(self, message, new_lvl):
		role_id_tuple = db.record("SELECT RoleID FROM lvl_rewards WHERE GuildID = ? AND lvl = ?", message.guild.id, new_lvl)
		to_remove_role_id_tuple = db.record("SELECT RoleID FROM lvl_rewards WHERE GuildID = ? AND lvl > ?", message.guild.id, new_lvl)
		if to_remove_role_id_tuple != None:
			role_id = to_remove_role_id_tuple
			role_id = role_id[0]
			role = message.guild.get_role(role_id)
			await message.author.remove_roles(role)

		if role_id_tuple != None:
			role_id = role_id_tuple
			role_id = role_id[0]
			role = message.guild.get_role(role_id)
			await message.author.add_roles(role)

		else:
			return


	@command(name="lvlroles", aliases=["lvlr"])
	async def lvl_roles_list_command(self, ctx):
		lvl_rewards = db.records("SELECT RoleID, lvl FROM lvl_rewards WHERE GuildID = ? ORDER BY lvl ASC", ctx.guild.id)

		embed = Embed(title=f"{ctx.guild} Lvl reward roles",
					  colour=ctx.author.colour,
					  timestamp=datetime.utcnow())

		embed.set_thumbnail(url=ctx.guild.icon_url)

		for RoleID, lvl in lvl_rewards:
			role = ctx.guild.get_role(RoleID)
			embed.add_field(name=f"Lvl {lvl} reward Role", value=f"{role.mention}\n{RoleID}", inline=False)

		await ctx.send(embed=embed)

	@command(name="addlvlrole", aliases=["alr"])
	async def add_lvl_role_command(self, ctx, lvl, role: discord.Role):
		db.execute("INSERT INTO lvl_rewards VALUES (?, ?, ?)", role.id, ctx.guild.id, lvl)
		await ctx.send("Level reward role added successfully.")

	@add_lvl_role_command.error
	async def add_lvl_rank_command_error(self, ctx, error):
	    if isinstance(error, RoleNotFound):
	        await ctx.send("Role not found.")

	@command(name="removelvlrole", aliases=["rlr"])
	async def remove_lvl_role_command(self, ctx, role: discord.Role):
		role_id = role.id
		db.execute("DELETE FROM lvl_rewards WHERE RoleID = ? AND GuildID = ?", role_id, ctx.guild.id)
		await ctx.send("Level reward role removed successfully.")

	@remove_lvl_role_command.error
	async def remove_lvl_rank_command_error(self, ctx, error):
	    if isinstance(error, RoleNotFound):
	        await ctx.send("Role not found.")

	@command(name="rank")
	async def rank_command(self, ctx, target: Optional[Member]):
		target = target or ctx.author

		ids = db.column("SELECT UserID FROM exp WHERE GuildID = ? ORDER BY XP DESC", ctx.guild.id)
		xp, lvl = db.record("SELECT XP, Level FROM exp WHERE UserID = ? AND GuildID = ?", target.id, ctx.guild.id) or (None, None)
		if xp is not None:
			async with ctx.typing():
				lvl_x_start_xp = int(((lvl**1.8181818181818181)*42))+1 #anfang des xps vom lvl des members
				lvl_x_end_xp = int((((lvl+1)**1.8181818181818181)*42)) #ende des xps vom lvl des members

				rankcard = Image.open("./data/rankcard/rank_card_base.png")

	#-------------------------------------------------------------------------------------------------
				#url = requests.get(target.avatar_url_as(static_format="png"))
				#avatar = Image.open(BytesIO(url.content))
				#avatar = await target.avatar_url.save("./data/rankcard/avatar.png")
				#avatar = Image.open("./data/rankcard/avatar.png")

				avatar = await target.avatar_url_as(static_format="png").read()
				avatar = Image.open(BytesIO(avatar))

				avatar = avatar.resize((163, 163));
				avatar.convert("RGBA")
				bigsize = (avatar.size[0] * 3, avatar.size[1] * 3)
				mask = Image.new("L", bigsize, 0)
				draw = ImageDraw.Draw(mask)
				draw.ellipse((0, 0) + bigsize, fill=255)
				mask = mask.resize(avatar.size, Image.ANTIALIAS)
				avatar.putalpha(mask)
				avatar = avatar.convert("RGBA")
	#-------------------------------------------------------------------------------------------------
				#load rectangle(progress bar)
				rectangle = Image.open("./data/rankcard/rect.png")

				#percentage of progress bar
				percent = ((xp - lvl_x_start_xp)/(lvl_x_end_xp - lvl_x_start_xp))*100
				if percent < 1:
					percent = 1

				#change width of progress bar based on percentage
				rectangle = rectangle.resize((round(rectangle.size[0] * percent / 100), rectangle.size[1]))

				w, h = rectangle.size
				rectangle = rectangle.crop((1, 0, w-1, h))
	#-------------------------------------------------------------------------------------------------
				#pasting avatar+lvl bar into the rankcard
				rankcard.paste(rectangle, (206, 173), rectangle)
				rankcard.paste(avatar, (23,46), avatar)
	#-------------------------------------------------------------------------------------------------
				xp_little = numerize.numerize(xp)
				xp_end_little = numerize.numerize(lvl_x_end_xp)
				lvl_xp_got_little = numerize.numerize(xp - lvl_x_start_xp)
				lvl_xp_end_little = numerize.numerize(lvl_x_end_xp - lvl_x_start_xp)
	#-------------------------------------------------------------------------------------------------
				#adding text
				lvl_text = f"Level {lvl:,}"
				rank_text = f"Rank: {ids.index(target.id)+1} of {len(ids)}"
				xp_text = f"{xp_little} XP"
				xpleft_text = f"{lvl_xp_got_little} / {lvl_xp_end_little} XP"
				target_name = f"{target.name}"

				draw = ImageDraw.Draw(rankcard)
				font = ImageFont.truetype("./data/fonts/agencyfb.ttf", 30)
				fontb = ImageFont.truetype("./data/fonts/agencyfb.ttf", 36)

				draw.text((799,50), lvl_text, (255,255,255,), anchor="ra", font=fontb)
				draw.text((504,50), rank_text, (255,255,255,), font=fontb)
				draw.text((802,123), xpleft_text, (255,255,255,), anchor="ra", font=font)
				draw.text((213,123), target_name, (255,255,255,), font=font)
	#-------------------------------------------------------------------------------------------------
				#save image

				with io.BytesIO() as image_binary:
					rankcard.save(image_binary, "PNG")
					image_binary.seek(0)
					await ctx.send(file=discord.File(fp=image_binary, filename="rankcard.png"))

		else:
			await ctx.send("That member is not tracked by the experience system.")

#-------------------------------------------------------------------------------------------------

	@command(name="leaderboard", aliases=["lb"])
	async def display_leaderboard(self, ctx):
		records = db.records("SELECT UserID, XP, Level FROM exp WHERE GuildID = ? ORDER BY XP DESC", ctx.guild.id)

		menu = MenuPages(source=HelpMenu(ctx, records),
						 clear_reactions_after=True,
						 timeout=60.0)
		await menu.start(ctx)

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("exp")

	@Cog.listener()
	async def on_message(self, message):
		if message.guild is not None:
			if not message.author.bot:
				if message.author != None:
					await self.process_xp(message)

	@Cog.listener()
	async def on_member_join(self, member):
		db.execute("INSERT INTO exp (UserID, GuildID) VALUES (?, ?)", member.id, member.guild.id)
		db.commit()

	@Cog.listener()
	async def on_member_remove(self, member):
		db.execute("DELETE FROM exp WHERE UserID = ? AND GuildID = ?", member.id, member.guild.id)
		db.commit()

def setup(bot):
	bot.add_cog(Exp(bot))
