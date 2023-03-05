from datetime import datetime
import requests

import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import logging

from bs4 import BeautifulSoup

from database import Session, GuildToSchool
import asyncio
import websockets

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# client = discord.Client()
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
	logger.info(f'{bot.user} has connected to Discord!')
	


@bot.command()
@commands.has_permissions(administrator = True)
async def permission(ctx):
    await ctx.send('You have administrator access...')


@bot.command()
@commands.has_permissions(administrator = True)
async def subscribe(ctx, school_id, notification_threshold, subscription_name=""):
	session = Session()

	session.add(GuildToSchool(guild_id=ctx.guild.id, school_id=school_id, notification_threshold=int(notification_threshold), subscription_name=subscription_name, channel_id = ctx.channel.id ))
	session.commit()

	await ctx.send(f'Subscribed to {school_id} ({subscription_name}) with notifications {str(notification_threshold)} days in advance in the current channel.')


@bot.command()
@commands.has_permissions(administrator = True)
async def unsubscribe(ctx, subscription_name):
	session = Session()

	result = session.query(GuildToSchool).filter_by(subscription_name=subscription_name).first()
	logger.info(result)
	session.delete(result)
	session.commit()
	# close the session when done
	session.close()

	await ctx.send(f'Deleted {result.school_id} ({result.subscription_name}) subscription')

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

	mappings = fetch_subscribed_school_ids(ctx.guild.id)
	

	# close the session when done
	session.close()
	if mappings.count() > 0:
		await ctx.send("\n".join([condense_subscription_item(mapping) for mapping in mappings]))
	else:
		await ctx.send("No subscriptions")
	

@bot.command()
@commands.has_permissions(administrator = True)
async def check(ctx):
	session = Session()

	mappings = fetch_subscribed_school_ids(ctx.guild.id)

	for mapping in mappings:
		expires = fetch_schedule_ending_date(mapping.school_id)
		expires_in = days_to(expires)
		message = f"Schedules for {mapping.subscription_name} ({mapping.school_id}) will expire in {expires_in} days ({expires})"
		
		if expires_in < mapping.notification_threshold:
			message = f"**{message}**"

		await ctx.send(message)


	# close the session when done
	session.close()

bot.run(TOKEN)

