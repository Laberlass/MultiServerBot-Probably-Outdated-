from datetime import datetime, timedelta
from random import choice
from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions

from ..db import db

numbers = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣","6⃣", "7⃣", "8⃣", "9⃣", "🔟")


class Reactions(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.polls = []
            self.giveaways = []
            self.starboard_channel = self.bot.get_channel(841402515857604616)
            self.bot.cogs_ready.ready_up("reactions")

    @command(name="createpoll", aliases=["mkpoll"])
    @has_permissions(manage_guild=True)
    async def create_poll(self, ctx, hours: int, question: str, *options):
            if len(options) > 10:
                await ctx.send("You can only supply a maximum of 10 options.")

            else:
                embed = Embed(title="Poll",
    						  description=question,
    						  colour=ctx.author.colour,
    						  timestamp=datetime.utcnow())

                fields = [("Options", "\n".join([f"{numbers[idx]} {option}" for idx, option in enumerate(options)]), False),
    					  ("Instructions", "React to cast a vote!", False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                message = await ctx.send(embed=embed)

                for emoji in numbers[:len(options)]:
                    await message.add_reaction(emoji)

                self.polls.append((message.channel.id, message.id))

                self.bot.scheduler.add_job(self.complete_poll, "date", run_date=datetime.now()+timedelta(seconds=hours), args=[message.channel.id, message.id, message, embed]) #seconds=hours*3600

    async def complete_poll(self, channel_id, message_id, emessage, embed):
        message = await self.bot.get_channel(channel_id).fetch_message(message_id)

        most_voted = max(message.reactions, key=lambda r: r.count)

        embed.set_field_at(1, name = "Results", value = f"The results are in and option {most_voted.emoji} was the most popular with {most_voted.count-1:,} votes!", inline=True)

        await emessage.edit(embed=embed)
        
        self.polls.remove((message.channel.id, message.id))

    @command(name="giveaway", aliases=["cg"])
    @has_permissions(manage_guild=True)
    async def create_giveaway(self, ctx, mins: int, *, description: str):
        embed = Embed(title="Giveaway",
                      description=description,
                      colour=ctx.author.colour,
                      timestamp=datetime.utcnow())

        fields = [("End time", f"{datetime.utcnow()+timedelta(seconds=mins)}", False)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        message = await ctx.send(embed=embed)
        await message.add_reaction("\U0001f973")

        self.giveaways.append((message.channel.id, message.id))

        self.bot.scheduler.add_job(self.complete_giveway, "date", run_date=datetime.now()+timedelta(seconds=mins), args=[message.channel.id, message.id]) #seconds=mins*60

    async def complete_giveway(self, channel_id, message_id):
        message = await self.bot.get_channel(channel_id).fetch_message(message_id)

        if len((entrants := [u for u in await message.reactions[0].users().flatten() if not u.bot])) > 0:
            winner = choice(entrants)
            await message.channel.send(f"Congratulations {winner.mention} - you won the giveaway!")
            self.giveaways.remove((message.channel.id, message.id))

        else:
            await message.channel.send("Giveaway ended - no one entered!")
            self.giveaways.remove((message.channel.id, message.id))


    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.emoji.name == "\U00002b50":
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            if not message.author.bot and payload.member.id != message.author.id:
                msg_id, stars = db.record("SELECT StarMessageID, Stars FROM starboard WHERE RootMessageID = ?", message.id) or (None, 0)

                embed = Embed(title="Starred message",
                              colour=message.author.colour,
                              timestamp=datetime.utcnow())

                fields = [("Author", message.author.mention, False),
                          ("Content", message.content or "See attachment", False),
                          ("Stars", stars+1, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                if len(message.attachments):
                    embed.set_image(url = message.attachments[0].url)

                if not stars:
                    star_message = await self.starboard_channel.send(embed=embed)
                    db.execute("INSERT INTO starboard (RootMessageID, StarMessageID) VALUES (?, ?)", message.id, star_message.id)

                else:
                    star_message = await self.starboard_channel.fetch_message(msg_id)
                    await star_message.edit(embed=embed)
                    db.execute("UPDATE starboard SET Stars = Stars + 1 WHERE RootMessageID = ?". message.id)

            else:
                await message.remove_reaction(payload.emoji, payload.member)


    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        pass


def setup(bot):
    bot.add_cog(Reactions(bot))
