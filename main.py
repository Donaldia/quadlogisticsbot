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
    "errorhandler",
    "events"
]


with open('./config.json') as f:
    bot.config = json.load(f)


@bot.event
async def on_ready():
    print("Bot Online")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="!help"))

@bot.command(description="Shows this message")
async def help(ctx):
    embed = discord.Embed(title="Available Commands:")
    embed.color = discord.Color.random()
    cmds = bot.commands
    for cmd in cmds:
        if await cmd.can_run(ctx):
            field_name = f'`!{cmd.name} {cmd.signature}`' if cmd.signature else f'`!{cmd.name}`'
            embed.add_field(name=field_name, value=cmd.description if cmd.description else 'Lisum Liosum eiau lsoei asiaks', inline=False)
            #commands_string.append(f'!{cmd.name} {cmd.signature} - {cmd.description}')

    embed.set_footer(text=f"{len(cmds)} commands")
    return await ctx.send(embed=embed)

if __name__ == "__main__":

    for ext in exts:
        try:
            bot.load_extension('cogs.'+ext)
            print("Loaded " + ext)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n[{}]'.format(ext, e))


@bot.command(hidden=True, description="Reloads an extension")
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