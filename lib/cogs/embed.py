import discord

from discord import Member, Embed
from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions
from datetime import datetime

from ..db import db

class Embed(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="CustomEmbed")
    @has_permissions(ban_members=True)
    async def CustomEmbed_command(self, ctx, title, arg):
        embed=discord.Embed(color=0x2f3136)
        embed.title = title
        embed.description = arg
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @command()
    @has_permissions(ban_members=True)
    async def applyembed(self, ctx):
        embed = discord.Embed(title="Team Creed Application",
							  description="Willkommen auf dem Team Creed Discord-Server!\n\n"

                                          "Hier kannst du dich bewerben, um Teil unseres Teams zu werden!\n"
                                          "Reagiere mit dem Emoji, für das als das du dich bewerben willst!\n\n"

                                          ":video_game:   ➔ für  `Player`           ( Minis,Academy,Talent )\n"
                                          ":clapper:   ➔ für  `Content Creator`\n"
                                          ":pencil2:   ➔ für  `Graphic Designer`    ( GFX )\n"
                                          ":movie_camera:   ➔  für `Editor`         ( VFX )\n\n"

                                          "__Mit etwas Glück schaffst es auch **du** ins Team!.__\n\n"

                                          "Viel Glück wünscht dir __**Team Creed**__\n"
                                          "PS: Bitte schreibe keinem Teammitgliedern, dass du dich beworben hast oder, dass diese deine Bewerbung anschauen sollen!\n\n"

                                          "~Das Serverteam",
							  color=0x2f3136,
							  timestamp=datetime.utcnow())

        embed.set_footer(text="Team Creed Application", icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("embed")


def setup(bot):
    bot.add_cog(Embed(bot))
