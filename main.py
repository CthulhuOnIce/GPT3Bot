import discord
from discord.ext import commands
import yaml
import asyncio
import sys
import traceback
import os
import subprocess

# add cogs
sys.path.insert(1, "cogs")

# cogs
import kevgpt3

# from disputils import BotEmbedPaginator, BotConfirmation, BotMultipleChoice

try:
	with open("config.yml", "r") as r:
		C = yaml.load(r.read(), Loader=yaml.FullLoader)
except FileNotFoundError:
	print("No config.yml, please copy and rename config-example.yml and fill in the appropriate values.")
	exit()

feedbacktimeout = []

intents = discord.Intents.default()

bot = commands.Bot(
	command_prefix=C["prefix"],
	intents=intents
	)

# cogs setup
kevgpt3.setup(bot, C)

@bot.event
async def on_ready():  # I just like seeing basic info like this
	await bot.change_presence(activity=discord.Game(name=f'{C["prefix"]}help')) 
	print("-----------------Info-----------------")
	print(f"Total Servers: {len(bot.guilds)}")

@bot.event
async def on_command_error(ctx, error):  # share certain errors with the user
	if(isinstance(error, commands.CommandNotFound)):
		return
	if isinstance(error, commands.BadArgument):
		await ctx.send(f"Bad Argument: {error}")
		return
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f"Missing Argument: {error}")
		return
	if isinstance(error, commands.CommandInvokeError):
		original = error.original
		if isinstance(original, IndexError):
			await ctx.send(f"IndexError: {original}\n[This might mean your search found no results]")
			return
	await ctx.send("😖 Sorry, that command caused an error! Devs are investigating the issue.")
	print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
	traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
	if(ctx):
		print(f"Author: {ctx.author}")
		print(f"Command: {ctx.message.clean_content}")

bot.run(C["token"])
