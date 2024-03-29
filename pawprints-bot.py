from datetime import datetime
import requests

import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import logging
import json
from bs4 import BeautifulSoup

from database import Session, GuildToSchool
import logging

from pawprints_api import PawPrints
from helpers import strip_tags

import traceback
import csv
from pathlib import Path
import datetime


load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
SIGS_FILENAME="database/sigs.csv"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# client = discord.Client()
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

pawprints = PawPrints()

# Define a coroutine to receive data from the WebSocket feed
async def receive_data():

	await pawprints.connect()
	try:
		async for data in pawprints.listen():
			# Handle the message as needed
			cmd = data.get("command")
			logging.info(cmd)
			if cmd:
				logging.info(data)

				if cmd == "new-petition":
					#TODO make sure these keys exist (they should but to prevent errors)
					petition_id = data["petition"]["petition_id"]

					# request the full data
					# Send a WebSocket request
					if petition_id:
						petition_data = await pawprints.get_petition(petition_id)
						logging.info(petition_data)
						if petition_data:
							await send_to_discord(petition_data)

				elif cmd == "update-sigs":
					file_exists = Path(SIGS_FILENAME).exists()
					with open(SIGS_FILENAME, 'a' if file_exists else 'a', newline='') as csvfile:
						fieldnames = ['timestamp', 'sigs', 'petition_id']
						writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

						if not file_exists:
							writer.writeheader()
						writer.writerow({'timestamp': (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds(), 'sigs': data["sigs"], 'petition_id': data["petition_id"]})
	except Exception as e:
		logger.info('Stopping...')
		logger.error(e)
		logger.error(traceback.format_exc())

		await pawprints.disconnect()
			

# Define a coroutine to send data to the Discord channel
async def send_to_discord(data):
	content = format_pawprint_post(data)

	subscriptions = fetch_subscribed_channels()
	for subscription in subscriptions:
		channel = bot.get_channel(subscription.channel_id)
		# add some filtering. the dev bot may not be in every channel that the prod one is, if they share a database this could create errors
		if channel:
			await channel.send(content)

def limit_length(string, lim):
	if len(string) > lim:
		return string[:lim]
	return string

def format_pawprint_post(data):
	title = data.get("title")
	desc = data.get("description")
	ident = data.get("id")
	r = f"New Pawprint: **{title}**\n"
	r += f"summary: {limit_length(strip_tags(desc), 300)}\n"
	r += f"Link: https://pawprints.rit.edu/petition/bots/{ident}\n"
	return r

@bot.event
async def on_ready():
	logger.info(f'{bot.user} has connected to Discord!')
	await receive_data()

def fetch_subscribed_channels(channel_id = None):
	# create a new session object to interact with the database
	session = Session()

	# retrieve the school ID for a given guild ID
	mappings = session.query(GuildToSchool)
	if channel_id:
		mappings = mappings.filter_by(channel_id=channel_id)

	# close the session when done
	session.close()
	return mappings

@bot.command()
@commands.has_permissions(administrator = True)
async def permission(ctx):
	await ctx.send('You have administrator access...')


@bot.command()
@commands.has_permissions(administrator = True)
async def subscribe(ctx):
	session = Session()

	session.add(GuildToSchool(guild_id=ctx.guild.id, channel_id = ctx.channel.id ))
	session.commit()

	await ctx.send(f'Subscribed to pawprints notifications in the current channel.')


@bot.command()
@commands.has_permissions(administrator = True)
async def unsubscribe(ctx):
	session = Session()

	result = session.query(GuildToSchool).filter_by(channel_id=ctx.channel.id).first()
	logger.info(result)
	session.delete(result)
	session.commit()
	# close the session when done
	session.close()

	await ctx.send(f'Unsubscribed from pawprints notifications in the current channel.')


@bot.command(name='list')
@commands.has_permissions(administrator = True)
async def _list(ctx):
	session = Session()

	mappings = fetch_subscribed_channels(ctx.channel.id)
	

	# close the session when done
	session.close()
	if mappings.count() > 0:
		await ctx.send("this channel is subscribed to pawprints notifications")
	else:
		await ctx.send("No subscriptions")
	
bot.run(TOKEN)

