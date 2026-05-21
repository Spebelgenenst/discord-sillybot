import discord
from discord import app_commands
import json
from petpetgif import petpet
from typing import Literal
import random

import torch
from transformers import pipeline

import asyncio

from io import BytesIO

with open("credentials.json", "r") as f:
    credentials = json.load(f)

with open("config.json", "r") as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.members = True
intents.messages = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")

async def ai(prompt):
    message = [
        {"role": "user", "content": prompt},
    ]
    ai_prompt = pipe.tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)   
    outputs = await asyncio.to_thread(pipe, ai_prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)

    raw_text = outputs[0]["generated_text"]

    print(raw_text)

    clean_text = raw_text.split("<|assistant|>")[1].replace(prompt, "").strip()

    return clean_text

def pet_pet(image):
    pet_pet_gif = BytesIO()
    petpet.make(BytesIO(image), pet_pet_gif)
    pet_pet_gif.seek(0)
    return pet_pet_gif

@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot logged in as {client.user}")

@tree.command(name="send_message", description="let a person send a message")
async def send_message(interaction: discord.Interaction, user: discord.Member, message: str):
    await interaction.response.defer(ephemeral=True)
    loading_message = await interaction.original_response() 

    webhook = await interaction.channel.create_webhook(name=user.name)
    await webhook.send(content=message, username=user.display_name, avatar_url=user.avatar)

    await loading_message.delete()
    await webhook.delete()

@tree.command(name="random_gif", description="get a random gif of something")
async def get_gif(interaction: discord.Interaction, pic_type: Literal[*list(config["gifs"].keys()), "random"]):
    if pic_type == "random":
        pic_type = random.choice(list(config["gifs"].keys()))
    gif = random.choice(config["gifs"][pic_type])
    await interaction.response.send_message(gif)

@tree.command(name="predict", description="predict what message a user will send")
async def predict_message(interaction: discord.Interaction, user: discord.Member, last_messages: int = 6):
    await interaction.response.defer(ephemeral=True)
    loading_message = await interaction.original_response() 
    messages = []

    async for message in interaction.channel.history(limit=last_messages):
        messages.append(f"{message.author.display_name}: {message.content}")

    messages.reverse()
    prompt = f"one possible next message {user.display_name} will send. previous messages: {messages}"

    raw_response = await ai(prompt)
    #print(raw_response)

    try:
        response = raw_response.split('"')[1]
    except IndexError:
        response = raw_response

    webhook = await interaction.channel.create_webhook(name=user.name)
    await webhook.send(content=response, username=user.display_name, avatar_url=user.avatar)
    await loading_message.delete()
    await webhook.delete()

@tree.command(name="petpet", description="pet a user")
async def petepet_user(interaction: discord.Interaction, user: discord.Member):
    if not user.avatar:
        await interaction.response.send_message("user has no avatar", ephemeral=True)
        return
    
    avatar = await user.avatar.read()
    pet_pet_gif = pet_pet(avatar)
    await interaction.response.send_message(file=discord.File(pet_pet_gif, filename=f"{user.name}_petpet.gif"))

@tree.command()

@client.event
async def on_message(message):
    if not (client.user.mentioned_in(message) and message.author != client.user):
        return

    await message.add_reaction("⌛")
    response = await ai(message.content.replace(f"<@{client.user.id}>", "ai"))
    await message.reply(response)
    await message.remove_reaction("⌛", client.user)

@client.event
async def on_member_join(user):
    channel = await client.fetch_channel(config["joinMessageChannelId"])
    if not user.avatar:
        await interaction.response.send_message("user has no avatar", ephemeral=True)
        return
    
    avatar = await user.avatar.read()
    pet_pet_gif = pet_pet(avatar)

    await channel.send(file=discord.File(pet_pet_gif, filename=f"{user.name}_petpet.gif"))

client.run(credentials["discordBotToken"])