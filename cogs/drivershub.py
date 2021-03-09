import random
import string
import discord
import mysql.connector
import cogs.checks as checks
from discord.ext import commands

class DriversHub(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(checks.isOwner)
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
        await ctx.author.send(embed=embed)


    @commands.command()
    async def sync(self, ctx, *, username:str):
        db = mysql.connector.connect(
            host="31.170.160.1",
            user="u985952930_admin",
            password="Quadadmin123",
            database="u985952930_drivershub"
        )

        cursor = db.cursor()


        cursor.execute(f"SELECT * FROM users WHERE username='{username}'")

        results = cursor.fetchone()

        if results is None:
            cursor.close()
            db.close()
            embed = discord.Embed()
            embed.description=f'User **"{username}"** not found'
            embed.color = discord.Color.red()
            return await ctx.send(embed=embed)
        (_id, discord_id, username, balance, rank, email, password, _admin, datetime) = results
        if discord_id != 0:
            cursor.close()
            db.close()
            embed = discord.Embed()
            embed.description=f'User **"{username}"** already synced with a Discord User. \nPlease contact a Developer for help!'
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


    @commands.command()
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
            return await ctx.send(embed=discord.Embed(description="You have not synced your Discord with the Drivers hub.\n\n Use `!sync < your drivershub username >` in order to sync the two.", color=discord.Color.red()))

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

    @commands.command()
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

        if(rank == "Driver In Training"):
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