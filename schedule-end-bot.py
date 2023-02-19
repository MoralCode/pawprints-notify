from datetime import datetime
import requests

import os

from discord.ext import commands
from dotenv import load_dotenv

from database import Session, GuildToSchool

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# client = discord.Client()
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# http://stackoverflow.com/questions/8419564/ddg#8419655
def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return (d2 - d1).days


def fetch_schedule_ending_date(school_id):
	response = requests.get("https://api.classclock.app/v0/bellschedules/" + school_id, headers={"Accept": "application/json"})
	if response.status_code == 200:
		response = response.json()
		dates = []
		data = response.get("data")
		for schedule in data:
			dates.extend(schedule.get("dates"))

		dates.sort()
		return dates[-1]



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

	await ctx.send(f'Subscribed to {school_id} ({subscription_name}) with notifications {str(notification_threshold)} days in advance')


@bot.command(name='list')
@commands.has_permissions(administrator = True)
async def _list(ctx):
	session = Session()

	mappings = session.query(GuildToSchool).filter_by(guild_id=ctx.guild.id)
	for mapping in mappings:
		if mapping:
			print(f'The school ID for guild ID {guild_id} is {mapping.school_id}.')
		else:
			print(f'No school ID found for guild ID {guild_id}.')

	# close the session when done
	session.close()

	await ctx.send(f'Done')
bot.add_command(_list)
bot.add_command(subscribe)
