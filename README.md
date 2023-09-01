# Pawprints notification discord bot
This is a discord bot that aims to provide notifications when new pawprints are posted, so that more members of the RIT community can participate and vote on issues that are raised

## Usage
Grant the bot access to your server:
TODO: add oauth link here


To subscribe to a feed of pawprints, an administrator must run the command `/subscribe` in the channel that should be subscribed to


## Development

To run the bot locally, you need to make a `.env` file containing the text `DISCORD_TOKEN=` followed by a discord bot token created from the discord developer portal.

Then you can build the docker container with `docker build -t <image name> .`. The database will generate on first run.

To run the bot, you can use the command `docker run --rm --env-file .env <image name>`.


This bot depends on the pawprints-api library/repo, which it currently expects to be cloned into a directory at the same level as it.


