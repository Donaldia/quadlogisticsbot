import discord
import textwrap
import io
import traceback
import datetime
import mysql.connector
import cogs.checks as checks
from discord.ext import commands
from contextlib import redirect_stdout
from disputils import BotEmbedPaginator, BotConfirmation, BotMultipleChoice



class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = ""

    async def add_punishment(self, discord_id, punishment_type, punishment_reason, moderator_id):
        db = mysql.connector.connect(
            host="31.170.160.1",
            user="u985952930_admin",
            password="Quadadmin123",
            database="u985952930_drivershub"
        )

        cursor = db.cursor()

        query = """INSERT INTO discord_punishments(discord_id, punishment_type, punishment_reason, moderator_id, datetime) VALUES(%s, %s, %s, %s, %s)"""

        cursor.execute(query, (discord_id, punishment_type, punishment_reason, moderator_id, datetime.datetime.now()))

        db.commit()
        cursor.close()
        db.close()

    async def get_punishments(self, user_id):
        db = mysql.connector.connect(
            host="31.170.160.1",
            user="u985952930_admin",
            password="Quadadmin123",
            database="u985952930_drivershub"
        )

        cursor = db.cursor(buffered=True)

        query = f"""SELECT * FROM discord_punishments WHERE discord_id={user_id}"""

        cursor.execute(query)

        res = cursor.fetchall()

        cursor.close()
        db.close()
        return res


    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```

        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.command(aliases=['gp', 'getpunishments', 'check'], description="Gets all the users punishments")
    @commands.check(checks.canWarn)
    async def punishments(self, ctx, user:discord.Member):
        res = await self.get_punishments(user.id)
        embeds = []
        if not res:
            await ctx.send(":thumbsdown: User does not have any punishments.", delete_after=20)
        for p in res:
            (user_id, punishment_id, punishment_type, reason, moderator_id, datetime) = p
            desc = f"""
            Type: {punishment_type.capitalize()}
            Moderator: {ctx.guild.get_member(moderator_id).mention}
            Reason: {reason}
            When: {datetime}
            Punishment ID: {punishment_id}
            """
            embeds.append(discord.Embed(title=f"#{punishment_id} | {user.name}", description=desc, color=discord.Color.random()))

        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()

    @commands.command(aliases=['purge', 'c'], description="Clears the text chat")
    @commands.check(checks.canClear)
    async def clear(self, ctx, amount:int):
        if amount > 500 or amount < 0:
            return await ctx.send("Invalid amount. Maximum is 500.")

        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f":thumbsup: Deleted **{len(deleted)}/{amount}** possible messages for you.", delete_after=20)


    @commands.command(description="Kicks the mentioned user from the server")
    @commands.check(checks.canKick)
    async def kick(self, ctx, user:discord.Member, *, reason:str):
        await self.add_punishment(user.id, "kick", reason, ctx.author.id)
        await ctx.guild.kick(user, reason=reason)
        await ctx.send(f":thumbsup: **{user}** kicked!")

    @commands.command(description="Bans the mentinoned user from the server")
    @commands.check(checks.canBan)
    async def ban(self, ctx, user:discord.Member, *, reason:str):
        await self.add_punishment(user.id, "ban", reason, ctx.author.id)

        await ctx.guild.ban(user, reason=reason)
        await ctx.send(f":thumbsup: **{user}** banned!")

    @commands.command(description="Shuts down the bot")
    @commands.check(checks.isDonald)
    async def l(self, ctx):
        await self.bot.logout()
    
    @commands.command(description="Warns the mentioned user")
    @commands.check(checks.canWarn)
    async def warn(self, ctx, user:discord.Member, *, reason:str):
        await self.add_punishment(user.id, "warn", reason, ctx.author.id)
        if 'Used a blacklisted word(s), message:' in reason:
            return await ctx.send(f'{user.mention} You have been warned for using blacklisted words!')
        await ctx.send(f":writing_hand: {user.mention} has been warned for *{reason}*!")
        embed = discord.Embed()
        embed.title = "You have been warned in Quad Logistics"
        embed.description = f"You have been warned in Quad Logistics for `{reason}`s by {ctx.author}"
        embed.color = discord.Color.dark_red()
        await user.send(embed=embed)


    @commands.command(description="Sends an embedded message to the Rules channel.")
    @commands.check(checks.canAnnounce)
    async def rule(self, ctx, *, body: str):
        cmd = self.bot.get_command('announce')
        await ctx.invoke(cmd, body=body, type="rules")

    @commands.command(description="Sends an announcement to the Announcement channel.\nDesign your announcement here: [Link](https://cog-creators.github.io/discord-embed-sandbox/)")
    @commands.check(checks.canAnnounce)
    async def announce(self, ctx, *, body: str):
        cmd = self.bot.get_command('eval')
        await ctx.invoke(cmd, body=body, type="announce")

    @commands.command(pass_context=True, hidden=True, name='eval', description="Evaluates a code")
    @commands.check(checks.isDonald)
    async def _eval(self, ctx, *, body: str, type=None):
        """Evaluates a code"""

        if body == "link":
            return await ctx.send('https://cog-creators.github.io/discord-embed-sandbox/')

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result,
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()
        if type == "announce":
            body = body.replace('await ctx.send(embed=embed)', 'channel = guild.get_channel(805994225119920138)\nawait channel.send(embed=embed)')
            to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'
        if type == 'rules':
            body = body.replace('await ctx.send(embed=embed)', 'channel = guild.get_channel(805995023517876235)\nawait channel.send(embed=embed)')
            to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'
        try:
            exec(to_compile, env)
        except Exception as e:
            print(to_compile)
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')


def setup(bot):
    bot.add_cog(Mod(bot))