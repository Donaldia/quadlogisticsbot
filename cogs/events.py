import discord
import datetime
import mysql.connector
import wordfilter
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chatlog_channel = 819231310543323157
        self.blacklisted_words = ['nigga','nigger','n1gga','n1gg4','nigg4','n1gger','n1gg3r','nigg3r','fag', 'faggot', 'f4g', 'f4ggot','f4gg0t', 'fagg0t','pornhub.com','xnxx.com','redtube.com']
        wordfilter.clear_list()
        wordfilter.add_words(self.blacklisted_words)

    async def log_message(self, message):
        db = mysql.connector.connect(
            host="31.170.160.1",
            user="u985952930_admin",
            password="Quadadmin123",
            database="u985952930_drivershub"
        )

        cursor = db.cursor()

        cursor.execute(f"INSERT INTO discord_chatlogs(discord_id, channel_id, message, datetime) VALUES({message.author.id}, {message.channel.id}, '{message.content}', '{datetime.datetime.now()}')")

        db.commit()
        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content == "":
            return

        if wordfilter.blacklisted(message.content):
            await message.delete()
            cmd = self.bot.get_command('warn')
            ctx = await self.bot.get_context(message)
            await ctx.invoke(cmd, user=message.author, reason=f'Used a blacklisted word(s), message: `{message.content}`')

        channel = message.guild.get_channel(self.chatlog_channel)
        embed = discord.Embed(color=discord.Color.random())
        embed.timestamp = datetime.datetime.now()
        embed.add_field(name="Message Author", value=message.author.mention, inline=False)
        embed.add_field(name="Message Channel", value=message.channel.mention, inline=False)
        embed.add_field(name="Message:", value=f"```{message.content}```", inline=False)
        

        await channel.send(embed=embed)
        await self.log_message(message)


def setup(bot):
    bot.add_cog(Events(bot))