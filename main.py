import discord
from discord import app_commands
import json
#from petpetgif import petpet
from typing import Literal
import random

with open("credentials.json", "r") as f:
    credentials = json.load(f)

with open("config.json", "r") as f:
    config = json.load(f)

print(config["gifs"].keys())

intents = discord.Intents.default()
#intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot logged in as {client.user}")

@tree.command(name="send_message", description="let a person send a message")
async def send_message(interaction: discord.Interaction, user: discord.Member, message: str):

    await interaction.response.defer(ephemeral=True)
    response = await interaction.original_response() 

    webhook = await interaction.channel.create_webhook(name="test")
    await webhook.send(content=message, username=user.display_name, avatar_url=user.avatar)

    await response.delete()

    await webhook.delete()

@tree.command(name="random_gif", description="get a random gif of something")
async def get_gif(interaction: discord.Interaction, pic_type: Literal[*list(config["gifs"].keys()), "random"]):
    if pic_type == "random":
        pic_type = random.choice(list(config["gifs"].keys()))
    gif = random.choice(config["gifs"][pic_type])
    await interaction.response.send_message(gif)

client.run(credentials["discordBotToken"])
