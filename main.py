#!/usr/bin/env python3

import asyncio
import codecs
import os
import pprint
import subprocess

from dotenv import load_dotenv
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
from twitchAPI.oauth import UserAuthenticator, UserAuthenticationStorageHelper
#from twitchAPI.pubsub import PubSub
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope, ChatEvent

load_dotenv()

TWITCH_APP_ID     = os.getenv("TWITCH_APP_ID")
TWITCH_APP_SECRET = os.getenv("TWITCH_APP_SECRET")
TWITCH_USER_SCOPE = [
        AuthScope.CHAT_READ,
        AuthScope.CHAT_EDIT,
        AuthScope.WHISPERS_READ,
        AuthScope.CHANNEL_READ_REDEMPTIONS,
    ]
TARGET_CHANNEL    = 'syntax976'
ALLOWED_USERS     = ['billweiss', 'beardbyte']
# this is generated from some magic fucking site. Why, API, why.
CHANNEL_ID        = 198813553

# this will be called when the event READY is triggered, which will be on bot start
async def on_ready(ready_event: EventData):
    print('Bot is ready for work, joining channels')
    # join our target channel, if you want to join multiple, either call join for each individually
    # or even better pass a list of channels as the argument
    await ready_event.chat.join_room(TARGET_CHANNEL)
    # you can do other bot initialization things in here

# this will be called whenever a message in a channel was send by either the bot OR another user
async def on_message(msg: ChatMessage):
    print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')

# this will be called whenever someone subscribes to a channel
async def on_sub(sub: ChatSub):
    print(f'New subscription in {sub.room.name}: '
          f'Type: {sub.sub_plan} '
          f'Message: {sub.sub_message}')

# this will be called whenever the !reply command is issued
async def reply_command(cmd: ChatCommand):
    print(f'in {cmd.room.name}: {cmd.user.name} used {cmd.name}')
    if len(cmd.parameter) == 0:
        print(f'in {cmd.room.name}: {cmd.user.name} sent !reply without params')
        await cmd.reply('you did not tell me what to reply with')
    else:
        print(f'in {cmd.room.name}: {cmd.user.name} used reply with: {cmd.parameter}')
        await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')

async def asdf_command(cmd: ChatCommand):
    print(f'in {cmd.room.name}: {cmd.user.name} used {cmd.name}')
    if cmd.user.name not in ALLOWED_USERS:
        print(f'in {cmd.room.name}: {cmd.user.name} sent a !{cmd.name} but isnt in the list')
    else:
        if len(cmd.parameter) == 0:
            print(f'in {cmd.room.name}: {cmd.user.name} sent !{cmd.name} without params')
            await cmd.reply('you did not tell me what to {cmd.name} with')
        else:
            print(f'in {cmd.room.name}: {cmd.user.name} used {cmd.name} with: {cmd.parameter}')
            response = subprocess.run(
                                      f'echo {cmd.parameter} | /usr/games/cowsay',
                                      capture_output=True,
                                      shell=True
                                      ).stdout
            response = codecs.decode(response, 'utf-8')
            await cmd.reply(f'{cmd.user.name}: {response}')

COMMANDS = {
        'reply': reply_command,
        'asdf': asdf_command,
        }
#
#async def points_listener(uuid, data):
#    print(f'Callback for pubsub UUID {uuid}')
#    pprint.pp(data)

# this is where we set up the bot
async def run():
    # set up twitch api instance and add user authentication with some scopes
    twitch = await Twitch(TWITCH_APP_ID, TWITCH_APP_SECRET)
    helper = UserAuthenticationStorageHelper(twitch, TWITCH_USER_SCOPE)
    await helper.bind()

    # create chat instance
    chat = await Chat(twitch)

#    pubsub = PubSub(twitch)

    # listen to when the bot is done starting up and ready to join channels
    chat.register_event(ChatEvent.READY, on_ready)
    # listen to chat messages
    chat.register_event(ChatEvent.MESSAGE, on_message)
    # listen to channel subscriptions
    chat.register_event(ChatEvent.SUB, on_sub)
    # there are more events, you can view them all in this documentation

    # you can directly register commands and their handlers, this will register the !reply command
    for command in COMMANDS.items():
        chat.register_command(command[0], command[1])

#    uuid = await pubsub.listen_channel_points(CHANNEL_ID, points_listener)
#    print(f'UUID from starting pubsub: {uuid}')

    # we are done with our setup, lets start this bot up!
    chat.start()
#    pubsub.start()

    # lets run till we press enter in the console
    try:
        input('press ENTER to stop\n')
    finally:
        # now we can close the chat bot and the twitch api client
#        pubsub.stop()
        chat.stop()
        await twitch.close()


# lets run our setup
asyncio.run(run())
