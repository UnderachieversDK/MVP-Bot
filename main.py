import discord
import pickle
import os
import requests
import sys
import pytz
import time
import traceback
from datetime import datetime
import json
import re
import asyncio
from discord.ext import commands
from discord.ext import bridge

bot = bridge.Bot(command_prefix='>', case_insensitive=True, intents=discord.Intents.all())
bot.remove_command("help")

default_color = discord.Color(0xfa8072)
owner = 206636330095083523
errors = []

@bot.event
async def on_ready():
	servers = bot.guilds[0]
	for server in bot.guilds:
		if server != bot.guilds[0]:
			servers = f'{servers}, {server}'
	user = await bot.fetch_user(owner)
	for error in errors:
		await user.send(f'__**{error.split(" ")[1].capitalize()} Failed:**__ \n{error.split(": ")[3]}')

def format_time(time, timezone="US/Eastern"):
	time = time.astimezone(pytz.timezone(timezone))
	time = time.strftime(f'%m/%d/%Y @ %#I:%M:%S %p')
	return(time)

async def senderror(error, cogname):
	try:
		user = await bot.fetch_user(owner)
		await user.send(f'Cog {cogname} failed: {error}')
	except:
		pass
	errors.append(f'Cog {cogname} failed: {error}')

def write_json(cogname, folder="cogs", type="load"):
	if type == "load":
		with open(f'resources/bot/cogs.json', 'r') as f:
			dict = json.load(f)
			if folder[:5] == "cogs.":
				dict["loaded"].append(f'{folder.strip("cogs.")}/{cogname}')
			elif folder != "cogs":
				dict["loaded"].append(f'{folder}/{cogname}')
			else:
				dict["loaded"].append(f'{cogname}')
		with open(f'resources/bot/cogs.json', 'w') as f:
			json.dump(dict, f)
	else:
		with open(f'resources/bot/cogs.json', 'r') as f:
			dict = json.load(f)
			if folder[:5] == "cogs.":
				dict["loaded"].remove(f'{folder.strip("cogs.")}/{cogname}')
			elif folder != "cogs":
				dict["loaded"].remove(f'{folder}/{cogname}')
			else:
				dict["loaded"].remove(f'{cogname}')
		with open(f'resources/bot/cogs.json', 'w') as f:
			json.dump(dict, f)

def load_cog(cogname, folder="cogs"):
	cogname = str(cogname).lower()
	if isinstance(cogname, str) == True:
		if cogname != "all":
			filepath = folder.replace("/", ".")
			try:
				bot.load_extension(f'{filepath}.{cogname}')
				write_json(f'{cogname}', f'{filepath}')
				return f'loaded:{filepath.replace(".", "/")}/{cogname}'
			except:
				try:
					bot.unload_extension(f'{filepath}.{cogname}')
					bot.load_extension(f'{filepath}.{cogname}')
					return f'reloaded:{filepath}/{cogname}'
				except:
					try:
						bot.load_extension(f'{filepath}.{cogname}')
					except Exception as error:
						if os.path.exists(f'cogs/{cogname}.py') == True:
							bot.loop.create_task(senderror(error, cogname))
							return f'failed:{filepath}/{cogname}'
						else:
							bot.loop.create_task(senderror(error, cogname))
							return f'doesn\'t exist:{filepath}/{cogname}'
		else:
			loaded = []
			errored = []
			filepath = folder
			if filepath[0] == ".":
				filepath = filepath[1:]
			if filepath[0] == "./":
				filepath = filepath[2:]
			for cog in os.listdir(f'./{filepath}'):
				if cog.endswith(".py"):
					cogname = cog[:-3]
					if cog[0] != "#":
						try:
							result = load_cog(cogname, filepath)
							result = result.split(":")[0]
							if result == "failed":
								errored.append(cogname)
							if result in ["loaded", "reloaded"]:
								loaded.append(cogname)
							if result == "loaded":
								write_json(f'{cogname}', f'{filepath}')
						except:
							errored.append(cogname)
					else:
						try:
							bot.unload_extension(f'{filepath}.{cogname}')
							result = load_cog(cogname, filepath)
							result = result.split(":")[0]
							if result == "failed":
								errored.append(cogname)
							if result == "loaded" or "reloaded":
								loaded.append(cogname)
							if result == "loaded":
								write_json(f'{cogname}', f'{filepath}')
						except:
							pass
			return {"loaded": loaded, "errored": errored}
	return False

def unload_cog(cogname, folder="cogs"):
	cogname = str(cogname).lower()
	if isinstance(cogname, str) == True:
		if cogname != "all":
			filepath = folder.replace("/", ".")
			try:
				bot.unload_extension(f'{filepath}.{cogname}')
				write_json(f'{cogname}', f'{filepath}', 'unload')
				return f'unloaded:{filepath.replace(".", "/")}/{cogname}'
			except:
				return f'notloaded:{filepath.replace(".", "/")}/{cogname}'
		else:
			unloaded = []
			notloaded = []
			filepath = folder
			if filepath[0] == ".":
				filepath = filepath[1:]
			if filepath[0] == "./":
				filepath = filepath[2:]
			for cog in os.listdir(f'./{filepath}'):
				if cog.endswith(".py"):
					cogname = cog[:-3]
					try:
						result = unload_cog(cogname, filepath)
						result = result.split(":")[0]
						if result == "unloaded":
							unloaded.append(cogname)
							write_json(f'{cogname}', f'{filepath}', "unloaded")
						else:
							notloaded.append(cogname)
					except:
						notloaded.append(cogname)
			return {"unloaded": unloaded, "notloaded": notloaded}
	return False

def make_embed(loaded=[], errored=[], word1="Loaded", word2="Failed"):
	string = f''
	if len(loaded) > 0:
		loadedcontent = ", ".join(loaded)
		if string == '':
			string = f'Cogs {word1} ({len(loaded)}): {loadedcontent}'
		else:
			string = f'{string} \nCogs {word1} ({len(loaded)}): {loadedcontent}'
	if len(errored) > 0:
		erroredcontent = ", ".join(errored)
		if string == '':
			string = f'Cogs {word2} ({len(errored)}): {erroredcontent}'
		else:
			string = f'{string} \nCogs {word2} ({len(errored)}): {erroredcontent}'
	e = discord.Embed(title="Cog Manager", description=string, color=default_color)
	return e

@bot.command(aliases=["cogs", "c"])
async def cog(ctx, *args):
	if ctx.author.id == owner:
		async with ctx.typing():
			e = discord.Embed(title="Cog Commands", description=f'`>cog load (cog)/all` \n`>cog load from/in (location) (cog)/all` \n`>cog unload (cog)/all` \n`>cog unload from/in (location) (cog)/all` \n`>cog list`', color=default_color)
			if args[0] in ["load", "reload", "rl"]:
				if args[1] not in ["from", "in"]:
					result = load_cog(args[1], "cogs")
					if args[1] == "all":
						e = make_embed(result["loaded"], result["errored"])
					else:
						result = result.split(":")
						e = discord.Embed(title="Cog Manager", description=f'Cog \'{result[1]}\' {result[0]}.', color=default_color)
				else:
					result = load_cog(args[3], args[2])
					if args[3] == "all":
						e = make_embed(result["loaded"], result["errored"])
					else:
						result = result.split(":")
						e = discord.Embed(title="Cog Manager", description=f'Cog \'{result[1]}\' {result[0]}.', color=default_color)
			elif args[0] in ["unload", "u"]:
				if args[1] not in ["from", "in"]:
					result = unload_cog(args[1], "cogs")
					if args[1] == "all":
						e = make_embed(result["unloaded"], result["notloaded"], "Unloaded", "Not Loaded")
					else:
						result = result.split(":")
						e = discord.Embed(title="Cog Manager", description=f'Cog \'{result[1]}\' {result[0]}.', color=default_color)
				else:
					result = unload_cog(args[3], args[2])
					if args[3] == "all":
						e = make_embed(result["unloaded"], result["notloaded"], "Unloaded", "Not Loaded")
					else:
						result = result.split(":")
						e = discord.Embed(title="Cog Manager", description=f'Cog \'{result[1]}\' {result[0]}.', color=default_color)
			elif args[0] in ["list", "l"]:
				with open(f'resources/bot/cogs.json', 'r') as f:
					dict = json.load(f)
				list = ", ".join(dict["loaded"])
				e = discord.Embed(title="Cog Manager", description=f'Cogs Loaded ({len(dict["loaded"])}): {list}.', color=default_color)
			print(e.description)
			await ctx.respond(embed=e, mention_author=False)

result = load_cog("all")
if len(result["loaded"]) > 0:
	loaded = ', '.join(result["loaded"])
	print(f'{len(result["loaded"])} Cogs Loaded: {loaded}')
if len(result["errored"]) > 0:
	errored = ', '.join(result["errored"])
	print(f'{len(result["errored"])} Cogs Failed: {errored}')
print("\n")
for cog in result["loaded"]:
	try:
		cog1 = bot.get_cog(cog)
		commands = cog1.get_commands()
		commandnames = commands[0]
		for command in commands:
			if command:
				if command != commands[0]:
					commandnames = f'{commandnames}, {command.name}'
		if commandnames != '':
			print(f'{cog} commands: {commandnames}')
	except:
		pass
with open(f'resources/bot/cogs.json', 'w') as f:
	json.dump({"loaded": result["loaded"]}, f)

bot.run('NDk4NjU1MzMzNDY0NTM5MTM3.W7qm-A.Q1cUweO6tKgQYAKW1AcEL-uvYRU')
