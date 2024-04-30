import os
import discord
import requests
import json
import random
import replit
from replit import db
from discord.ext import commands
from discord.utils import find
from discord.ext import tasks
from itertools import cycle
from google.cloud import secretmanager

# Create the Secret Manager client.
client = secretmanager.SecretManagerServiceClient()
project_id = os.getenv("743097597361")
secret_id = "TOKEN"

# Access the secret version.
name = f"projects/743097597361/secrets/TOKEN"
response = client.access_secret_version(request={"name": name})

# Your secret data is in response.payload.data.
my_secret = response.payload.data.decode('UTF-8')


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Ensure this is enabled if needed

client = discord.Client(intents=intents)

status_cycle = cycle([
  discord.Activity(type=discord.ActivityType.watching, name="your happiness!"),
  discord.Activity(type=discord.ActivityType.watching, name="you cheer up!")
])

@client.event
async def on_ready():
  print(f"We have logged in as {client.user}")
  change_status.start()  # Start changing statuses after the bot is ready

@tasks.loop(seconds=10)
async def change_status():
  # Get the next activity from the cycle
  next_status = next(status_cycle)
  # Update the bot's presence
  await client.change_presence(activity=next_status)

sad_words = ["sad", "depressed", "unhappy", "angry", "miserable", "mad", "unhapppy"]

starter_encouragements = [
    "Cheer up!",
    "Hang in there.",
    "You are a great person / bot!",
    "You will get through this.",
    "Don't worry, I am here for you.",
    "Keep in mind that there is always a happy little bot thinking about you :).",
    "Go get some hot cocoa. Bet it will cheer you up."
]

if "responding" not in db.keys():
    db["responding"] = True

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]["q"] + " -" + json_data[0]["a"]
    return quote

@client.event
async def on_guild_join(guild):
    user_id = "589603077774901253"
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send('Hello {}!'.format(guild.name))
        await general.send(f"Thank you for adding me! My name is Happy Bot and I was created by <@{user_id}>. Please use $help for a list of my commands. Cheer on!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if msg.startswith("$inspire"):
        quote = get_quote()
        await message.channel.send(quote)

    if db["responding"]:
        options = starter_encouragements

        if any(word in msg for word in sad_words):
            await message.channel.send(random.choice(options))

    if msg.startswith("$list"):
        await message.channel.send('Here are the sad words: sad, depressed, unhappy, angry, miserable, mad, unhappy.')

    if msg.startswith("$responding"):
        value = msg.split("$responding ", 1)[1]

        if value.lower() == "true":
            db["responding"] = True
            await message.channel.send("Responding is on.")
        else:
            db["responding"] = False
            await message.channel.send("Responding is off.")

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$help'):
        await message.channel.send('My commands are: $inspire -- Get inspired by a cool quote!. Saying any of the words on $list (such as sad) -- cheer up!. $list -- all the words that trigger the cheer up command. $hello -- Greetings!. $help -- Being used at this very moment :) Tells you all of the commands available. That is it for now, but more cool commands are yet to come!')

change_status()
client.run(os.getenv('secret_id'))
