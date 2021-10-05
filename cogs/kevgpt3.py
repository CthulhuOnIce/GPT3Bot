# just a template to copy and paste for use in developing cogs in the future

from discord.ext import commands
import discord
import simplejson as json
import openai
import random
import requests
from kgptj import SimpleCompletion

C = {}

P = {}
CP = "gus"  # the name of the current (default) personality
R = 0 # restriction level, 0 = anyone can conversate with the bot anywhere, 1, conversate with the bot in bot chat only, 2, the bot will only reply randomly everywhere
RC = 2  # the chance that the bot will respond to any given message

Rexplain = {
	0: "Anyone can ping the bot anywhere, and it will reply, as well as responding to posts randomly",
	1: "The bot can only be pinged for a reply in designated channels, everywhere else it just replies randomly",
	2: "The bot cannot be pinged for a reply anywhere, the only way for the bot to respond to something is if it interjects randomly"
}

personalities = [
	"kev", "gus", "fylke"
]

blacklist = []

latestlog = []

def gpt3_answer(question):
	global latestlog

	prepend = P[CP] + "\n".join(latestlog)

	prompt = f"{prepend}\nQ: \"{question}\"\nA: \""

	response = openai.Completion.create(
		engine="davinci", 
		prompt=prompt, 
		max_tokens=80, 
		temperature=0.75, 
		stop="\"",
		frequency_penalty=0.5,
		)

	response_text = response["choices"][0]["text"]

	latestlog.append(f"Q: \"{question}\"\nA: \"{response_text}\"\n")

	latestlog = latestlog[::-1][0:9]

	return response_text

def gptj_answer(question):
	global latestlog

	prepend = P[CP] + "\n".join(latestlog)

	prompt = f"{prepend}\nQ: \"{question}\"\nA: \""

	query = SimpleCompletion(
		prompt, 
		length=60, 
		t=0.75, 
		)

	response_text = query.simple_completion().split("\"")[0]

	latestlog.append(f"Q: \"{question}\"\nA: \"{response_text}\"\n")

	latestlog = latestlog[::-1][0:9]

	return response_text

def answer(question):
	if C["engine"] == "gpt3":	return gpt3_answer(question)
	elif C["engine"] == "gptj":	return gptj_answer(question)

class GPT3(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(brief="List settings.")
	async def settings(self, ctx):
		embed=discord.Embed(title="Settings", description="Bot's current configuration")
		embed.add_field(name="Restriction Level", value=R, inline=False)
		embed.add_field(name="Restriction Level Explained", value=Rexplain[R], inline=False)
		embed.add_field(name="Personality", value=CP, inline=False)
		embed.add_field(name="Personalities", value=personalities, inline=False)
		embed.add_field(name="Engine", value=C["engine"], inline=False)
		embed.add_field(name="Blacklist Status", value=(ctx.author.id in blacklist), inline=False)
		await ctx.send(embed=embed)

	@commands.command(brief="Update restriction level")
	async def setrl(self, ctx, level:int):
		global R
		if ctx.author.id not in C["sudoers"]:
			await ctx.send("You do not have permissiont to run this command.")
			return
		R = level
		await ctx.send("Updated")

	@commands.command(brief="Change personality")
	async def setpersonality(self, ctx, personality:str):
		global CP
		global latestlog
		if ctx.author.id not in C["sudoers"]:
			await ctx.send("You do not have permissiont to run this command.")
			return
		CP = personality
		latestlog = []

		await ctx.send("Updated")

	@commands.command(brief="Change personality")
	async def setengine(self, ctx, newengine:str):
		if ctx.author.id not in C["sudoers"]:
			await ctx.send("You do not have permissiont to run this command.")
			return
		C["engine"] = newengine
		await ctx.send("Updated")

	@commands.command(brief="Toggle blacklist (disables the bot from replying to you randomly)")
	async def blacklistme(self, ctx):
		if ctx.author.id in blacklist:
			blacklist.remove(ctx.author.id)
			await ctx.send("You have been removed from the blacklist.")
		else:
			blacklist.append(ctx.author.id)
			await ctx.send("You have been added to the blacklist.")

	@commands.Cog.listener()
	async def on_message(self, message):
		if self.bot.user.mentioned_in(message) and (
		    (message.channel.id == C["botchannel"] and R == 1) or R == 0): 
			await message.reply(answer(message.clean_content))
			return

		chance = random.randint(0, 100)
		if chance <= RC and message.author.id != self.bot.user.id and message.author.id not in blacklist:
			await message.reply(answer(message.clean_content))

def setup(bot, config):
	global C
	C = config
	openai.api_key = C["key"]
	bot.add_cog(GPT3(bot))
	for personality in personalities:
		data = json.loads(open(f"personalities/{personality}.json", "r").read())
		P[data["name"]] = data["training_data"]
