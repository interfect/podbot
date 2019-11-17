#!/usr/bin/env python3

"""
podbot.py: Matrix bot that will play your podcasts.

For Ubuntu, needs libolm-dev installed for matrix-nio[e2e]
But python-olm no longer really exists, so matrix-nio[e2e] doesn't work

Takes configuration from podbot.conf, which needs:

[chat.privacytools.io]
user = podbot
password = PASSWORD_HERE
room = !CxsSqzSVhrdxfVxTpb:matrix.org

"""

import asyncio
import re
import configparser

from nio import (AsyncClient, RoomMessageText, InviteEvent)
import vlc

class PodBot:
    """
    Represents a bot instance which logs into Matrix, hangs out in a room, and obeys commands.
    """

    def __init__(self, HOMESERVER, USER, PASSWORD, ROOM, PROTOCOL="https"):
        """
        Start up a bot and connect to the given homeserver with the given
        credentials, and join the given room.
        """
        
        # Note that we are replaying recent history until we are synced. Until then, skip all commands.
        self.replaying = True
        
        # Save our important config items
        self.ROOM = ROOM
        self.PASSWORD = PASSWORD
        
        # This holds our media player
        self.player = None
        
        # This holds our Matrix connection
        self.client = AsyncClient(PROTOCOL + "://" + HOMESERVER, USER)
        self.client.add_event_callback(self.message_cb, RoomMessageText)
        self.client.add_event_callback(self.invite_cb, InviteEvent)
        
        # Make a task that runs some code every time we sync with the server.
        # Then client.rooms should be filled in.
        sync_task = asyncio.get_event_loop().create_task(self.watch_for_sync(self.client.synced))
        
    async def run(self):
        """
        After creating the bot, this should be called and awaited to make it
        actually do its work.
        """
        
        result = await self.client.login(self.PASSWORD)
        print('Login result: {}'.format(str(result)))
        
        await self.client.sync_forever(timeout=30000)

    async def message_cb(self, room, event):
        """
        Handle a message we see in a room somewhere.
        """
        
        if room.machine_name == self.ROOM or room.display_name == self.ROOM:
            # We like this room
            print("{} | {}: {}".format(room.display_name, room.user_name(event.sender), event.body))
            
            if not self.replaying:
                # This came in since we started running
                # Try handling the message as a command
                await self.run_command(event.body)
            
        else:
            # Ignore messages in other rooms
            return
        
        
        
    async def invite_cb(self, room, event):
        """
        Handle an invite to a room.
        """
        
        print("Room: {} Event: {}".format(repr(room), repr(event)))
        
        if room.machine_name == self.ROOM or room.display_name == self.ROOM:
            # We want to be in this room, so join
            result = await self.client.join(ROOM)
            print('Attempted to accept invite to {}: {}'.format(self.ROOM, str(result)))
        else:
            # Reject the invite
            result = await self.client.room_leave(room.machine_name)
            # TODO: We may get the same events on next startup in which case this fails.
            print('Attempted to reject invite to {}: {}'.format(room.machine_name, str(result)))
        
        
      
    async def watch_for_sync(self, sync_event):
        """
        Task which waits repeatedly on the sync event and calls our callback.
        """
        
        while True:
            await sync_event.wait()
            await self.sync_cb()
        
    async def sync_cb(self):
        """
        Handle the periodic "synced" event that we get when we come up to speed with the server.
        """
        
        print("Client is synced!")
        print('Rooms:' + str(self.client.rooms))
        
        # Now we can run commands
        self.replaying = False
        
        for room_id in self.client.rooms.keys():
            # Decide if we should be in this room
            if room_id != self.ROOM:
                # Nope. Leave it.
                result = await self.client.room_leave(room_id)
                
                print('Attempted to leave {}: {}'.format(room_id, str(result)))
                
        if self.ROOM not in self.client.rooms:
            # We need to join the room we want to be in
            result = await self.client.join(self.ROOM)
            
            print('Attempted to join {}: {}'.format(self.ROOM, str(result)))
            
            
    async def run_command(self, command):
        print("Try command: {}".format(repr(command)))
        if command.lower() == "stop":
            # Stop media
            print("Stop media")
            self.update_media()
        else:
            # See if it is something to start
            # Matches blah URL or blah URL [hh:mm:ss]
            match = re.match('.*(https?://[^ ]*) ?\[?([0-9:]+)?\]?.*', command)
            
            if match:
                print("Play media: {}".format(match.groups()))
                self.update_media(match.groups())
                
    def update_media(self, parts=None):
        """
        Play media given a tuple of parts.
        
        0 parts: stop
        1 part (url): play URL from beginning
        2 parts (url and h:m:s): play URL from time
        
        """
        
        if parts is None or len(parts) == 0:
            if self.player is not None:
                # Stop the player
                print("Stop playing anything")
                self.player.stop()
                player = None
        elif len(parts) == 1:
            # Play the URL
            if self.player is not None:
                # Stop any existing player
                print("Stop old player")
                self.player.stop()
            print("Play {} from start".format(parts[0]))
            self.player = vlc.MediaPlayer(parts[0])
            self.player.play()
        elif len(parts) == 2:
            # Play the URL from the given time, if we can parse the time
            try:
                time_parts = [int(x) for x in parts[1].split(':')]
                time = 60 * 60 * time_parts[0] + 60 * time_parts[1] + time_parts[2]
            except:
                # Skip unparseable time
                print("Could not parse time {}".format(parts[1]))
                return
            
            if self.player is not None:
                # Stop any existing player
                print("Stop old player")
                self.player.stop()
                
            print("Play {} from {} seconds".format(parts[0], time))
            self.player = vlc.MediaPlayer(parts[0])
            self.player.play()
            self.player.set_time(1000 * time)

async def main():
    """
    Start up the program.
    """
    
    # Load the config
    config = configparser.ConfigParser()
    config.read('podbot.conf')
    
    # Hold bots. We should probably have just one, since they play audio.
    bots = []
    
    for homeserver in config.sections():
        # For each homeserver, work out how to connect
        user = config[homeserver]['user']
        password = config[homeserver]['password']
        room = config[homeserver]['room']
        protocol = config[homeserver].get('protocol', 'https')
        
        # Make a bot that will connect with those credentials
        bots.append(PodBot(HOMESERVER, USER, PASSWORD, ROOM, PROTOCOL="https"))
        
    # Start all the bots
    results = [bot.run() for bot in bots]
    
    for result in results:
        # Await them all
        await result
        
asyncio.get_event_loop().run_until_complete(main())
