import discord
import textwrap
import io
import traceback
import datetime
import mysql.connector
import cogs.checks as checks
from discord.ext import commands
from contextlib import redirect_stdout


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

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```

        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.command(aliases=['purge', 'c'])
    @commands.check(checks.isStaff)
    async def clear(self, ctx, amount:int):
        if amount > 500 or amount < 0:
            return await ctx.send("Invalid amount. Maximum is 500.")

        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f":thumbsup: Deleted **{len(deleted)}/{amount}** possible messages for you.", delete_after=20)


    @commands.command()
    @commands.check(checks.isStaff)
    async def kick(self, ctx, user:discord.Member, *, reason:str = None):
        if not reason: reason = "#"
        await ctx.guild.kick(user, reason="")
        await ctx.send(f":thumbsup: **{user}** kicked!")

    @commands.command()
    @commands.check(checks.isAdmin)
    async def ban(self, ctx, user:discord.Member, *, reason:str = None):
        if not reason: reason = "#"
        await ctx.guild.ban(user, reason="")
        await ctx.send(f":thumbsup: **{user}** banned!")

    @commands.command()
    @commands.check(checks.isDonald)
    async def l(self, ctx):
        await self.bot.logout()
    
    @commands.command()
    @commands.check(checks.isStaff)
    async def warn(self, ctx, user:discord.Member, *, reason:str):
        await self.add_punishment(user.id, "warn", reason, ctx.author.id)

        await ctx.send("punished :thumbsup:")



    @commands.command(pass_context=True, hidden=True, name='eval', aliases=['announce'])
    async def _eval(self, ctx, *, body: str):
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

        body = body.replace('await ctx.send(embed=embed)', 'channel = guild.get_channel(714755750240583710)\nawait channel.send(embed=embed)')
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