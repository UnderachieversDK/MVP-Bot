import discord
import os
import requests
import sys
import time
from datetime import datetime
import json
import asyncio
from discord.ext import commands
from discord.ext import bridge

bot = bridge.Bot(command_prefix='>', case_insensitive=True, intents=discord.Intents.all())
bot.remove_command("help")

default_color = discord.Color(0xfa8072)
admins = [206636330095083523]

@bot.event
async def on_ready():
	

bot.run('')
