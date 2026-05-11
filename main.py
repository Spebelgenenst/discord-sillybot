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
    await tree.sync()#guild=discord.Object(id=1430225351455543418))
    print(f"Ready! {client.user}")

@tree.command(
    name="send_message",
    description="let a person send a message",
    #guild=discord.Object(id=1430225351455543418)
)
async def first_command(interaction: discord.Interaction, user: discord.Member, message: str):
    webhook = await interaction.channel.create_webhook(name="test")
    await webhook.send(content=message, username=user.display_name, avatar_url=user.avatar)

    await webhook.delete()

    await interaction.response.send_message(f"message send :3", ephemeral=True)

client.run(credentials["discordBotToken"])
