# ClassClock schedule update notification discord bot
This is a discord bot that can monitor a ClassClock school and provide notifications when the school is about to run out of configured schedules. This provides school admins an oportunity to receive notifications and update their schedules.  

## Usage
Grant the bot access to your server:
https://discord.com/api/oauth2/authorize?client_id=1081952183353876530&permissions=2147486720&scope=bot


## Development

To run the bot locally, you need to make a `.env` file containing the text `DISCORD_TOKEN=` followed by a discord bot token created from the discord developer portal.

Then you can build the docker container with `docker build -t <image name> .`. The database will generate on first run.

To run the bot, you can use the command `docker run --rm --env-file .env -v$(pwd)/discord_school_mapping.db:/database/discord_school_mapping.db <image name>`. You may need to run `touch discord_school_mapping.db` first so the database file exists.
