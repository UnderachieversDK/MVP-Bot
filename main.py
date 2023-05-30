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


def addVote(userid, employee, month, year):
    file_path = f'resources/Votes/{month}.{year}.json'
    if os.path.isfile(file_path) == True:
    	file = open(filepath)
    	file_data = json.load(file)
        for employeevalues in file_data:
        	if userid in file_data[employeevalues]:
                file_data[employeevalues].pop(userid)
        file_data[employee].append(userid)
        with open(file_path, "w") as file:
        	file.write(json_object)
        return True
    else:
        return False
        
def createVote(employee1, employee2, employee3, month, year):
    file_path = f'resources/Votes/{month}.{year}.json'
    json_object = {employee1: [], employee2: [], employee3: []}
    with open(file_path, "w+") as file:
		file.write(json_object)

bot.run('')
