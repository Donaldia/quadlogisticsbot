import random
import string
import discord
import mysql.connector
import cogs.checks as checks
from discord.ext import tasks, commands
from datetime import datetime
class DriversHub(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invitecode_cleanup.start() 


    @tasks.loop(hours=24)
    async def invitecode_cleanup(self):

        query = "DELETE FROM invite_codes WHERE datetime < (NOW() - INTERVAL 7 DAY) ORDER BY datetime DESC"

        db = mysql.connector.connect(
            host="31.170.160.1",
            user="u985952930_admin",
            password="Quadadmin123",
            database="u985952930_drivershub"
        )

        cursor = db.cursor()

        cursor.execute(query)

        db.commit()
        cursor.close()
        db.close()
        print('Deleted all expired Invite Codes.')

    @invitecode_cleanup.before_loop
    async def before_invitecode_cleanup(self):
        print('Invite Code cleanup waiting for bot.')
        await self.bot.wait_until_ready()

    @commands.command(description="Creates an invite code for the DriverHub")
    @commands.check(checks.canInviteCode)
    async def invitecode(self, ctx):
        invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

        db = mysql.connector.connect(
            host="31.170.160.1",
            user="u985952930_admin",
            password="Quadadmin123",
            database="u985952930_drivershub"
        )

        cursor = db.cursor()

        cursor.execute(f"INSERT INTO invite_codes(discord_id, invite_code) VALUES({ctx.author.id}, '{invite_code}')")

        db.commit()
        cursor.close()
        db.close()


        embed = discord.Embed()
        embed.description = f"Your new Invite Code to the DriversHub is: `{invite_code}`"
        embed.set_footer(text="The invite code is one time use only, it will be removed once used or after 7 days")
        await ctx.author.send(embed=embed)
        await ctx.send(f'{ctx.author.mention} Please check your DMs for the invite code.')

    @commands.command(name="sync", description="Syncs the Discord with your DriversHub account. Only works in DMs!")
    async def sync(self, ctx, recovery_code:str):
        if ctx.guild:
            await ctx.message.delete()
            await ctx.author.send('Please redo the sync command here!')
            return await ctx.send('You can only sync in the DMs. I messaged you, please redo the command in the DM channel with the me.')

        db = mysql.connector.connect(
            host="31.170.160.1",
            user="u985952930_admin",
            password="Quadadmin123",
            database="u985952930_drivershub"
        )

        cursor = db.cursor()


        cursor.execute(f"SELECT * FROM users WHERE recovery_code='{recovery_code}'")

        results = cursor.fetchone()

        if results is None:
            cursor.close()
            db.close()
            embed = discord.Embed()
            embed.description=f'User with the recovery code not found'
            embed.color = discord.Color.red()
            return await ctx.send(embed=embed)
        (_id, discord_id, username, balance, rank, email, password, _admin, datetime, recovery_code) = results
        if discord_id != 0:
            cursor.close()
            db.close()
            embed = discord.Embed()
            embed.description=f'User with the recovery code already synced with a Discord User. \nPlease contact a Developer for help!'
            embed.color = discord.Color.red()
            return await ctx.send(embed=embed)
        else:
            query = """
            UPDATE users
            SET discord_id = %s
            WHERE id = %s
            """

            cursor.execute(query, (ctx.author.id, _id))
            db.commit()
            cursor.close()
            db.close()
            embed = discord.Embed()
            embed.description=f'You are now synced.'
            embed.set_footer(text=f'DriversHub Username: "{username}"')
            embed.color = discord.Color.green()
            return await ctx.send(embed=embed)

    @commands.command(name="resetpassword", description="Sends a link to reset the DriversHub password. Only works in DMs!", aliases=['rp'])
    async def resetpassword(self, ctx, recovery_code):
        if ctx.guild:
            await ctx.message.delete()
            await ctx.author.send('Please redo the command here!')
            return await ctx.send('You can only request a password reset in the DMs. I messaged you, please redo the command in the DM channel with the me.')

        db = mysql.connector.connect(
            host="31.170.160.1",
            user="u985952930_admin",
            password="Quadadmin123",
            database="u985952930_drivershub"
        )

        cursor = db.cursor()


        cursor.execute(f"SELECT * FROM users WHERE recovery_code='{recovery_code}'")

        results = cursor.fetchone()

        if results is None:
            cursor.close()
            db.close()
            embed = discord.Embed()
            embed.description=f'User with the recovery code not found'
            embed.color = discord.Color.red()
            return await ctx.send(embed=embed)
        else:
            await ctx.send(f"http://drivers.quadlogisticsvtc.com/reset_password?rec_code={recovery_code}")

    @commands.command(description="Shows your DriversHub Rank")
    async def rank(self, ctx):
        db = mysql.connector.connect(
            host="31.170.160.1",
            user="u985952930_admin",
            password="Quadadmin123",
            database="u985952930_drivershub"
        )

        cursor = db.cursor()

        cursor.execute(f"SELECT id, rank FROM users WHERE discord_id = {ctx.author.id}")

        results = cursor.fetchone()
        if results is None:
            db.close()
            return await ctx.send(embed=discord.Embed(description="You have not synced your Discord with the DriversHub.\n\n Use `!sync <recovery_code>` in DMs in order to sync the two.", color=discord.Color.red()))

        (_id, rank) = results
        embed = discord.Embed()
        embed.description = f"Your Drivers Hub rank is: **{rank}**"
        embed.color = discord.Color.random()
        await ctx.send(embed=embed)
        cursor.close()
        db.close()

    async def db_rankup(self, new_rank, _id):
        db = mysql.connector.connect(
            host="31.170.160.1",
            user="u985952930_admin",
            password="Quadadmin123",
            database="u985952930_drivershub"
        )
        cursor = db.cursor()

        cursor.execute(f"UPDATE users SET rank = '{new_rank}' WHERE id = {_id}")
        db.commit()
        cursor.close()
        db.close()

    @commands.command(description="Ranks up your DriversHub Account")
    async def rankup(self, ctx):
        db = mysql.connector.connect(
            host="31.170.160.1",
            user="u985952930_admin",
            password="Quadadmin123",
            database="u985952930_drivershub"
        )
        cursor = db.cursor()
        ranks={
            "Probationary Driver": 0,
            "Rookie": 150000,
            "Driver": 500000,
            "Senior Driver": 1200000,
            "Veteran Driver": 5000000,
            "Legendary Driver": 10000000,
            "Platinum Driver": 20000000
        }

        cursor.execute(f"SELECT id, rank, balance FROM users WHERE discord_id = {ctx.author.id}")
        results = cursor.fetchone()
        (_id, rank, balance) = results

        cursor.close()
        db.close()

        embed = discord.Embed()

        if(rank == "Driver in Training"):
            embed.description = "You are Driver in Training. You need to complete all the required trainings to get promoted to a Probationary Driver"
            embed.color = discord.Color.red()
        elif(rank == "Probationary Driver"):
            if balance >= ranks.get("Rookie"):
                await self.db_rankup("Rookie", _id)
                embed.title = "Congratulations!"
                embed.description = "You have successfully ranked up to Rookie. :white_check_mark:"
                embed.color = discord.Color.random()
            else:
                embed.title = "Sorry!"
                embed.description = f"""
                You have not gathered enough money to rank up!
                You need **${ranks.get('Rookie')}**.
                You have gathered **${balance}**."""
                embed.color = discord.Color.red()

        elif(rank == "Rookie"):
            if balance >= ranks.get("Driver"):
                await self.db_rankup("Driver", _id)
                embed.title = "Congratulations!"
                embed.description = "You have successfully ranked up to Driver. :white_check_mark:"
                embed.color = discord.Color.random()
            else:
                embed.title = "Sorry!"
                embed.description = f"""
                You have not gathered enough money to rank up!
                You need **${ranks.get('Driver')}**.
                You have gathered **${balance}**."""
                embed.color = discord.Color.red()
        elif(rank == "Driver"):
            if balance >= ranks.get("Senior Driver"):
                await self.db_rankup("Senior Driver", _id)
                embed.title = "Congratulations!"
                embed.description = "You have successfully ranked up to Senior Driver. :white_check_mark:"
                embed.color = discord.Color.random()
            else:
                embed.title = "Sorry!"
                embed.description = f"""
                You have not gathered enough money to rank up!
                You need **${ranks.get('Senior Driver')}**.
                You have gathered **${balance}**."""
                embed.color = discord.Color.red()
        elif(rank == "Senior Driver"):
            if balance >= ranks.get("Veteran Driver"):
                await self.db_rankup("Veteran Driver", _id)
                embed.title = "Congratulations!"
                embed.description = "You have successfully ranked up to Veteran Driver. :white_check_mark:"
                embed.color = discord.Color.random()
            else:
                embed.title = "Sorry!"
                embed.description = f"""
                You have not gathered enough money to rank up!
                You need **${ranks.get('Veteran Driver')}**.
                You have gathered **${balance}**."""
                embed.color = discord.Color.red()
        elif(rank == " Veteran Driver"):
            if balance >= ranks.get("Legendary Driver"):
                await self.db_rankup("Legendary Driver", _id)
                embed.title = "Congratulations!"
                embed.description = "You have successfully ranked up to Legendary Driver. :white_check_mark:"
                embed.color = discord.Color.random()
            else:
                embed.title = "Sorry!"
                embed.description = f"""
                You have not gathered enough money to rank up!
                You need **${ranks.get('Legendary Driver')}**.
                You have gathered **${balance}**."""
                embed.color = discord.Color.red()
        elif(rank == " Legendary Driver"):
            if balance >= ranks.get("Rookie"):
                await self.db_rankup("Rookie", _id)
                embed.title = "Congratulations!"
                embed.description = "You have successfully ranked up to Rookie. :white_check_mark:"
                embed.color = discord.Color.random()
            else:
                embed.title = "Sorry!"
                embed.description = f"""
                You have not gathered enough money to rank up!
                You need **${ranks.get('Rookie')}**.
                You have gathered **${balance}**."""
                embed.color = discord.Color.red()
        elif(rank == "Platinum Driver"):
            if balance >= ranks.get("Platinum Driver"):
                await self.db_rankup("Platinum Driver", _id)
                embed.title = "Congratulations!"
                embed.description = "You have successfully ranked up to Platinum Driver. :white_check_mark:"
                embed.color = discord.Color.random()
            else:
                embed.title = "Sorry!"
                embed.description = f"""
                You have not gathered enough money to rank up!
                You need **${ranks.get('Platinum Driver')}**.
                You have gathered **${balance}**."""
                embed.color = discord.Color.red()
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(DriversHub(bot))