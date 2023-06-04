import discord

from datetime import datetime
import json

from json_functions import addVote
from json_functions import createVote
from json_functions import parent_dir

bot = discord.Bot(case_insensitive=True)

default_color = discord.Color(0x0045BE)
admins = [206636330095083523]

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
emojis = ['👍🏼', '❤️', '☺️']
bot_id = 1113284590057042020

@bot.command()
async def createavote(ctx, employee1: str, employee2: str, employee3: str, channel: discord.TextChannel=False, month: str=False, year: int=False):
	if month == False:
		month = months[datetime.now().month-1]
	else:
		if month not in months:
			return
	if year == False:
		year = datetime.now().year
	else:
		if (int(datetime.now().year)+1) <= year <= (int(datetime.now().year)-1):
			return
	createVote(ctx.guild.id, employee1, employee2, employee3, month, year)
	embed = discord.Embed(title=f'{year} MVP Vote for {month}!', description=f'Please react with who you think earned the top MVP spot! \n\n	{emojis[0]} - __{employee1}__ \n\n   {emojis[1]} - __{employee2}__ \n\n   {emojis[2]} - __{employee3}__', color=default_color)
	if channel == False:
		channel = ctx.channel
	if channel != ctx.channel:
		await ctx.respond(f'Successfully created MVP vote for {month}, {year} with candidates {employee1}, {employee2}, and {employee3}!')
	else:
		await ctx.respond("Success!", delete_after=0)
	message = await channel.send(embed=embed)
	for emoji in emojis:
		await message.add_reaction(emoji)

@bot.event
async def on_raw_reaction_add(payload):
	emoji = payload.emoji
	if emoji.name in emojis:
		channel = await bot.fetch_channel(payload.channel_id)
		message = await channel.fetch_message(payload.message_id)
		user = await bot.fetch_user(payload.user_id)
		if message.author.id == 1113284590057042020:
			if message.author.id != payload.user_id:
				if ' MVP Vote for ' in message.embeds[0].title:
					year, month = message.embeds[0].title.strip('!').split(" MVP Vote for ")
					guildid = message.guild.id
					file_path = f'{parent_dir}/resources/votes/{guildid}/{year}/{month}.json'
					with open(file_path, "r+") as file:
						employees = list(json.load(file).keys())
					if emoji.name == '👍🏼':
						addVote(payload.user_id, guildid, employees[0], month, year)
						await message.remove_reaction('👍🏼', user)
					elif emoji.name == '❤️':
						addVote(payload.user_id, guildid, employees[1], month, year)
						await message.remove_reaction('❤️', user)
					elif emoji.name == '☺️':
						addVote(payload.user_id, guildid, employees[2], month, year)
						await message.remove_reaction('☺️', user)
					with open(file_path, "r+") as file:
						votes = json.load(file)
					for vote in votes:
						if len(votes[vote]) == 0:
							votes[vote] = ''
						else:
							votes[vote] = f' {len(votes[vote])}'
					embed = discord.Embed(title=f'{year} MVP Vote for {month}!', description=f'Please react with who you think earned the top MVP spot! \n\n	{emojis[0]}{votes[employees[0]]} - __{employees[0]}__ \n\n   {emojis[1]}{votes[employees[1]]} - __{employees[1]}__ \n\n   {emojis[2]}{votes[employees[2]]} - __{employees[2]}__', color=default_color)
					await message.edit(embed=embed)
