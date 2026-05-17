import discord
from discord import app_commands
import json
#from petpetgif import petpet
from typing import Literal
import random

import torch
from transformers import pipeline

import asyncio

with open("credentials.json", "r") as f:
    credentials = json.load(f)

with open("config.json", "r") as f:
    config = json.load(f)

intents = discord.Intents.default()
#intents.members = True
client = discord.Client(intents=intents, heartbeat_timeout=180)
tree = app_commands.CommandTree(client)

pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")

async def ai(prompt):
    message = [
        {"role": "user", "content": prompt},
    ]
    prompt = pipe.tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)   
    outputs = await asyncio.to_thread(pipe, prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)

    raw_text = outputs[0]["generated_text"]

    clean_text = raw_text.replace(prompt, "").strip()
    clean_text = clean_text.replace("<|user|>", "").replace("<|assistant|>", "").strip()

    return clean_text

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

@client.event
async def on_message(message):
    if client.user.mentioned_in(message) and message.author != client.user:
        response = await ai(message.content.replace(f"<@{client.user.id}>", "ai"))
        await message.reply(response)

client.run(credentials["discordBotToken"])