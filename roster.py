    async def roster_updatea(self):

        channel_id, message_id, guild_id = db.records("SELECT ChannelID, MessageID, GuildID FROM roster WHERE Counter = 1")[0]

        guild = self.client.get_guild(guild_id)
        roster_channel =
        message = await ctx.guild.fetch_message(message_id)

        roster_content = db.records("SELECT RoleID FROM roster WHERE ChannelID = ? AND MessageID = ? ORDER BY counter ASC", channel_id, message_id)

        embed = Embed(title=f"**{message.guild} Roster**",
 					  colour=ctx.author.colour,
 					  timestamp=datetime.utcnow())

        embed.set_thumbnail(url=ctx.guild.icon_url)

        for RoleID in roster_content:
            role = message.guild.get_role(RoleID)

            embed.add_field(name=role.mention, value=("\n".join(map(str, role.members))), inline=False)

        await message.channel.send(embed=embed)

    @command(name="setrostera")
    @has_permissions(manage_guild=True)
    async def setroster_command(self, ctx, channel: discord.TextChannel, roles: Greedy[discord.Role]):
        counter = 1
        for role in roles:
            db.execute("INSERT INTO rostera VALUES (?, ?, ?, ?, ?)", role.id, channel.id, ctx.message.id, ctx.guild.id, counter)
            counter = counter + 1
        await self.roster_update()
        await ctx.send("Roster activated.")

    @command(name="delrostera")
    @has_permissions(manage_guild=True)
    async def delroster_command(self, ctx):
        db.execute("DELETE FROM roster WHERE GuildID = ?", ctx.guild.id)
        await ctx.send("Roster deactivated.")
