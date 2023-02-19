from datetime import datetime
import requests

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiocron

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

def days_to(date):
	d1 = datetime.strptime(date, "%Y-%m-%d")
	return (d1 - datetime.today()).days


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


def fetch_subscribed_school_ids(guild_id):
	# create a new session object to interact with the database
	session = Session()

	# retrieve the school ID for a given guild ID
	mappings = session.query(GuildToSchool)
	if guild_id:
		mappings = mappings.filter_by(guild_id=guild_id)

	# close the session when done
	session.close()
	return mappings


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
	print(result)
	session.delete(result)
	session.commit()
	# close the session when done
	session.close()

	await ctx.send(f'Deleted {result.school_id} ({result.subscription_name}) subscription')

def condense_subscription_item(item: GuildToSchool):
	if item:
		return f'{item.subscription_name} ({item.school_id}) will notify {item.notification_threshold} days in advance of schedules ending'
	else:
		print(f'No school ID found for guild ID {item.guild_id}.')
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


# post information about any schedules that are about to expire once per day
@aiocron.crontab(os.getenv("CRON_SCHEDULE") or '0 8 * * *')
async def post_schedule_update_notifications():
	session = Session()

	
	subscriptions = fetch_subscribed_school_ids()

	for subscription in subscriptions:

		expires = fetch_schedule_ending_date(subscription.school_id)
		expires_in = days_to(expires)

		if expires_in < subscription.notification_threshold:
			# Make sure your guild cache is ready so the channel can be found via get_channel
			#https://stackoverflow.com/a/66715493/
			await bot.wait_until_ready()
			message_channel = bot.get_channel(subscription.channel_id)
			await message_channel.send(
				f"**Schedules for {subscription.subscription_name} ({subscription.school_id}) will expire in {expires_in} days ({expires})**"
				)
		else:
			print(f"no schedule notifications needed for {subscription.subscription_name} ({subscription.school_id})")


	# close the session when done
	session.close()

	# channel = client.get_channel(int(os.getenv("CHANNEL")))
	# count = await get_current_velma_count()

	await channel.send(generate_count_message(count, get_lastupdate_string(time.time())))

bot.run(TOKEN)

