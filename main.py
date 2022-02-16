import random
import discord
from discord.ext import commands
import json
import logging
import datetime

logging.basicConfig(level=logging.INFO)
client = commands.Bot()

guild_ids = [799292825429606460,675095702833201180]
words = []
answers = []

@client.event
async def on_ready():
	logging.info(f"Signed in as {client.user}")

async def play_wordle(ctx:discord.ApplicationContext,number:int = 0):
	if number:
		word = answers[number]
	else:
		word = random.choice(answers)
	print(word)
	await ctx.respond("Creating thread...",ephemeral=True)
	thread:discord.Thread = await ctx.channel.create_thread(name=f"{ctx.user.name} Wordle ???",type=discord.ChannelType.public_thread)
	await thread.add_user(ctx.user)
	await thread.send("Type a word to get started...")
	game = []
	for i in range(6):
		message = await client.wait_for("message",check=lambda m: m.channel == thread and m.content in words and m.author == ctx.user)
		blocks = ""
		for j,letter in enumerate(message.content):
			if word[j] == letter:
				blocks += ":green_square:"
			elif letter in word:
				blocks += ":yellow_square:"
			else:
				blocks += ":black_large_square:"
		await thread.send(f"{blocks} {i+1}/6")
		game.append(blocks)
		if blocks == ":green_square:" * 5:
			break
	a = "\n"
	if game[-1] != ":green_square:" * 5:
		await thread.send(word.capitalize())
		number = "X"
	await thread.send(f"Wordle {number if number else '???'} {i+1}/6\n{a.join(game)}")
	await thread.archive(locked=True)
@client.slash_command(name="wordle",guilds_ids=guild_ids)
async def _daily_wordle(ctx:discord.ApplicationContext):
	day = (datetime.datetime.utcnow() - datetime.datetime(2021,6,19)).days # reverse engineered the first wordle date
	await play_wordle(ctx,day)

@client.slash_command(name="random_wordle",guilds_ids=guild_ids)
async def _random_wordle(ctx:discord.ApplicationContext):
	await play_wordle(ctx,0)

def main():
	import dotenv
	values = dotenv.dotenv_values(".env")
	global words, answers
	with open("answers.json") as answersfile: answers = json.load(answersfile)
	with open("words.json") as wordsfile: words = set(json.load(wordsfile) + answers)
	client.run(values['TOKEN'])

if __name__ == "__main__":
	main()