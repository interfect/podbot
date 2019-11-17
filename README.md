# PodBot: A bot to play your podcasts

PodBot is a Matrix bot designed to listen for the messages that AntennaPod creates if you share a podcast episode URL with a timestamp in a Matrix channel.

You can set up the bot to sit in a Matrix room, and then send podcast episodes to it from your phone. This lets you send a podcast you were listening to on your phone to better speakers in your house without losing your place.

## Requirements

* Python 3 (and virtualenv for the instructions below)
* VLC
* A Matrix account of your own.

PodBot is designed for use with AntennaPod and the Riot.im app, but anything that produces Matrix messages of the form `... <URL> ...` or  `... <URL> [<HH:MM:SS timestamp>] ...`, with or without brackets, will work.

## Preparation

* Create a new Matrix user for the bot. Get the homeserver, username and password.
* Create a new private Matrix room, as the Matrix user you want to be able to control the bot. **Anyone in the room** will be able to command the bot. Make sure to grab its ID, which looks something like `!CxsSqzSVhrdxfVxTpb:matrix.org`.
* Invite the bot's user to the room. When the bot logs inm it will accept the invite.

## Installation

```
git clone https://github.com/interfect/podbot.git
cd podbot

# Install dependencies
virtualenv --python python3 venv
. venv/bin/activate
pip install -r requirements.txt

# Configure
cp podbot.conf.example podbot.conf
# Edit podbot.conf to include your homeserver, username, and password for your bot account, as well as the room ID you want it to join.
# Use a fresh room; anybody in the room will be able to control the bot!

# Run
./podbot.py
```

# Usage

* From AntennaPod, open up the currently playing episode.
* Hit `...` in the upper right corner, and then `Share...` -> `Share Media File URL with Position`.
* Select the Riot.im app as the share destination.
* Select the room with you and the bot as the destination room.
* Hit send on the pre-filled message to start it playing.

To **stop** the playing audio, send the one-word message `stop`.
