import discord
from discord import app_commands
import json

with open("credentials.json", "r") as f:
    credentials = json.load(f)

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot logged in as {client.user}")

@tree.command(name="send_message", description="let a person send a message")
async def first_command(interaction: discord.Interaction, user: discord.Member, message: str):

    await interaction.response.defer(ephemeral=True)
    response = await interaction.original_response() 

    webhook = await interaction.channel.create_webhook(name="test")
    await webhook.send(content=message, username=user.display_name, avatar_url=user.avatar)

    await response.delete()

    await webhook.delete()

client.run(credentials["discordBotToken"])
