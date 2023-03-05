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
import asyncio
import websockets

from io import StringIO
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# client = discord.Client()
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

WEBSOCKET_URL = 'wss://pawprints.rit.edu/ws/'

# Define a coroutine to receive data from the WebSocket feed
async def receive_data():
	async with websockets.connect(WEBSOCKET_URL) as websocket:
		while True:
			data = await websocket.recv()
			# Process the data as needed
			# For example, you could parse the JSON data and extract relevant information
			# Here, we'll just send the raw data to Discord

			data = json.loads(data)
			cmd = data.get("command")
			if cmd:

				if cmd == "new-petition":
					await send_to_discord(data)

# Define a coroutine to send data to the Discord channel
async def send_to_discord(data):
	content = format_pawprint_post(data)

	subscriptions = fetch_subscribed_channels()
	for subscription in subscriptions:
		channel = bot.get_channel(subscription.channel_id)
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
	r += f"Link: https://pawprints.rit.edu/?p={ident}\n"
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

def condense_subscription_item(item: GuildToSchool):
	if item:
		return f'{item.subscription_name} ({item.school_id}) will notify {item.notification_threshold} days in advance of schedules ending'
	else:
		logger.info(f'No school ID found for guild ID {item.guild_id}.')
		return ""


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

