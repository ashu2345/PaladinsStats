import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
import hashlib
from datetime import datetime
import requests
import webbrowser

sep = '/'
TOKEN = process.env.TOKEN
devID = process.env.devID
authKey = process.env.authKey
pcURL = process.env.pcURL

Client = discord.Client()
client = commands.Bot(command_prefix = "!")

@client.event
async def on_ready():
	print("Bot is ready")

@client.event
async def on_message(message):

	#Have a cookie
	if message.content == "cookie":
		await message.channel.send(":cookie:")

	#Ping yourself
	elif message.content == "!ping":
		await message.channel.send("<@{0}> Hello there".format(message.author.id))

	#Check if you are an admin
	elif message.content.startswith("!amiadmin"):
		if 525596710433718272 in [role.id for role in message.author.roles]:
			await message.channel.send("You are an admin!")
		else:
			await message.channel.send("You are not an admin")

	#Player statistics
	elif message.content.startswith("p!stats"):
		player = message.content.split(' ')[1]
		await message.channel.send(createRequest('getplayer',player)[0][0])

	#Champion details
	elif message.content.startswith("p!champs"):
		player = message.content.split(' ')[1]
		await message.channel.send(createRequest('getchampionranks',player))

	#Match Details
	elif message.content.startswith("p!match"):
		matchid = message.content.split(' ')[1]
		await message.channel.send(createRequest('getmatchdetails',matchid))

#Generate MD5 Hash
def getMD5Hash(string):
	encode = hashlib.md5(string.encode('utf-8'))
	return encode.hexdigest()

#Create a specific url for a given method and return its JSON
def createRequest(*args):

	#current UTC timestamp
	timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

	#creating session for sessionID
	toHash = str(devID)+"createsession"+authKey+timestamp
	sessionURL = sep.join([pcURL,'createsessionJSON',str(devID),getMD5Hash(toHash),timestamp])
	r = requests.get(sessionURL)
	sessionID = r.json()['session_id']

	#Get statistics for a player
	if args[0] == 'getplayer':
		toHash = str(devID)+args[0]+authKey+timestamp
		url = sep.join([pcURL,'getplayerJSON',str(devID),getMD5Hash(toHash),sessionID,timestamp,args[1]])
		r = requests.get(url)
		return r.json(),str(r.json()[0]['Id'])

	#Get all champion stats for a player
	elif args[0] == 'getchampionranks':
		toHash = str(devID)+args[0]+authKey+timestamp
		url = sep.join([pcURL,'getchampionranksJSON',str(devID),getMD5Hash(toHash),sessionID,timestamp,createRequest('getplayer',args[1])[1]])
		webbrowser.open(url)
		return requests.get(url).json()

	#Get match details for a matchID
	elif args[0] == 'getmatchdetails':
		toHash = str(devID)+args[0]+authKey+timestamp
		url = sep.join([pcURL,'getmatchdetailsJSON',str(devID),getMD5Hash(toHash),sessionID,timestamp,args[1]])
		webbrowser.open(url)
		return requests.get(url).json()

client.run(TOKEN)
