import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
import hashlib
from datetime import datetime
import requests

sep = '/'
TOKEN = process.env.TOKEN
devID = process.env.devID
authKey = process.env.authKey
pcURL = process.env.pcURL

ranks = {1:"Bronze V",2:"Bronze IV",3:"Bronze III",4:"Bronze II",5:"Bronze I",
		6:"Silver V",7:"Silver IV",8:"Silver III",9:"Silver II",10:"Silver I",
		11:"Gold V",12:"Gold IV",13:"Gold III",14:"Gold II",15:"Gold I",
		16:"Platinum V",17:"Platinum IV",18:"Platinum III",19:"Platinum II",20:"Platinum I",
		21:"Diamond V",22:"Diamond IV",23:"Diamond III",24:"Diamond II",25:"Diamond I",
		26:"Master",27:"Grandmaster"}

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
		playerID = str(createRequest('getplayeridbyname',player)[0]['player_id'])
		await message.channel.send(formatJSON('stats',createRequest('getplayer',playerID)))

	#Champion details
	elif message.content.startswith("p!champ"):
		player,champion = message.content.split(' ')[1:]
		playerID = str(createRequest('getplayeridbyname',player)[0]['player_id'])
		champsDetails = createRequest('getchampionranks',playerID)
		champDetails = None
		for temp in champsDetails:
			if temp['champion'].replace(' ','').lower() == champion.lower():
				champDetails = temp
				break
		if champDetails is not None:
			await message.channel.send(formatJSON('champ',champDetails))
		else:
			await message.channel.send("```css\nPlease enter a valid champion name!```")

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

	#Get statistics for a player using playerID
	if args[0] == 'getplayer':
		toHash = str(devID)+args[0]+authKey+timestamp
		url = sep.join([pcURL,'getplayerJSON',str(devID),getMD5Hash(toHash),sessionID,timestamp,args[1]])
		return requests.get(url).json()

	#Get all champion stats for a player using playerID
	elif args[0] == 'getchampionranks':
		toHash = str(devID)+args[0]+authKey+timestamp
		url = sep.join([pcURL,'getchampionranksJSON',str(devID),getMD5Hash(toHash),sessionID,timestamp,args[1]])
		return requests.get(url).json()

	#Get match details for a matchID
	elif args[0] == 'getmatchdetails':
		toHash = str(devID)+args[0]+authKey+timestamp
		url = sep.join([pcURL,'getmatchdetailsJSON',str(devID),getMD5Hash(toHash),sessionID,timestamp,args[1]])
		return requests.get(url).json()

	#Get playerID for player name
	elif args[0] == 'getplayeridbyname':
		toHash = str(devID)+args[0]+authKey+timestamp
		url = sep.join([pcURL,'getplayeridbynameJSON',str(devID),getMD5Hash(toHash),sessionID,timestamp,args[1]])
		return requests.get(url).json()

def formatJSON(*args):

	message = ''

	#Format message for a champion
	if args[0] == 'champ':
		kills = args[1]['Kills']
		deaths = args[1]['Deaths']
		assists = args[1]['Assists']
		hours = args[1]['Minutes']//60
		wins = args[1]['Wins']
		losses = args[1]['Losses']
		wr = round((wins/(wins+losses))*100)
		message = f"""```css\n
					Champion Name: {args[1]['champion']}\n
					Champion Level: {args[1]['Rank']}\n
					Hours Played: {hours} hours\n
					Kills/Deaths/Assists: {kills}/{deaths}/{assists}\n
					Wins/Losses: {wins}/{losses} ({wr}% winrate)```"""
	
	#Format message for a player's stats
	elif args[0] == 'stats':
		hours = args[1][0]['HoursPlayed']
		level = args[1][0]['Level']
		name = args[1][0]['Name']
		mastery = args[1][0]['MasteryLevel']
		wins = args[1][0]['Wins']
		losses = args[1][0]['Losses']
		wr = round((wins/(wins+losses))*100,2)
		try:
			rank = ranks[args[1][0]['RankedConquest']['Tier']]
		except:
			rank = "Qualifying"
		message = f"""```css\n
					Name: {name}\n
					Level: {level}\n
					Hours Played: {hours} hours\n
					Rank: {rank}\n
					Wins/Losses: {wins}/{losses} ({wr}% winrate)```"""

	return message

client.run(TOKEN)

#Author:Tech_Crazy
