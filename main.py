import discord
import json
import sys
import traceback
from discord.ext import commands
import cogs.checks as checks

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

bot.remove_command('help')

exts = [
    "mod",
    "drivershub",
    "errorhandler"
]


with open('./config.json') as f:
    bot.config = json.load(f)


@bot.event
async def on_ready():
    print("Bot Online")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="!help"))

@bot.command()
async def help(ctx):
    embed = discord.Embed()
    embed.color = discord.Color.random()
    embed.description = """
    **DriversHub Commands:**
    
    `!rank` - Shows you your DriversHub Rank.
    `!rankup` - Ranks up your DriversHub Account.
    `!sync <username>*` - Syncs your Discord Account with the provided username in the DriversHub

    **Moderation Commands:**
    `!ban <@user>* <reason>` - Bans the user from the Discord Guild.
    `!clear <amount>*` - Clears an amount of messages from the chat.
    `!kick <@user>* <reason>` - Kicks the user from the Discord Guild.
    `!warn <@user>* <reason>*` - Warns the user for breaking the rules.
    `!announce <code>*` - Announces messages in the announcement channel.
    """
    embed.set_footer(text = "Note: Commands arguments with an asterisk ( * ) is required.")
    return await ctx.send(embed=embed)

if __name__ == "__main__":

    for ext in exts:
        try:
            bot.load_extension('cogs.'+ext)
            print("Loaded " + ext)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n[{}]'.format(ext, e))


@bot.command(hidden=True)
@commands.check(checks.isDonald)
async def r(ctx, ext):
    try:
        bot.unload_extension('cogs.'+ext)
        bot.load_extension('cogs.'+ext)
        await ctx.send(":thumbsup: Reloaded cogs."+ext)
    except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            await ctx.send('Failed to load extension {}\n[{}]'.format(ext, e))


bot.run(bot.config['TOKEN'])