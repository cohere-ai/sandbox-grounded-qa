# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

# this is a demo discord bot. You can make a discord bot token by visiting https://discord.com/developers

import argparse

import discord
from discord import Embed
from discord.ext import commands

from qa.bot import GroundedQaBot

parser = argparse.ArgumentParser(description="A grounded QA bot with cohere and google search")
parser.add_argument("--cohere_api_key", type=str, help="api key for cohere", required=True)
parser.add_argument("--serp_api_key", type=str, help="api key for serpAPI", required=True)
parser.add_argument("--discord_key", type=str, help="api key for discord boat", required=True)
parser.add_argument("--verbosity", type=int, default=0, help="verbosity level")
args = parser.parse_args()

bot = GroundedQaBot(args.cohere_api_key, args.serp_api_key)


class MyClient(discord.Client):

    async def on_ready(self):
        """Initializes bot"""
        print(f"We have logged in as {self.user}")

        for guild in self.guilds:
            print(f"{self.user} is connected to the following guild:\n"
                  f"{guild.name}(id: {guild.id})")

    async def answer(self, message):
        """Answers a question based on the context of the conversation and information from the web"""
        history = []
        async for historic_msg in message.channel.history(limit=6, before=message):
            if historic_msg.content:
                name = "user"
                if historic_msg.author.name == self.user.name:
                    name = "bot"
                history = [f"{name}: {historic_msg.clean_content}"] + history

        print(history)
        bot.set_chat_history(history)

        async with message.channel.typing():
            reply = bot.answer(message.clean_content, verbosity=2, n_paragraphs=3)
            response_msg = await message.channel.send(reply, reference=message)
            await response_msg.edit(suppress=True)
            return

    async def on_message(self, message):
        """Handles query messages triggered by direct messages to the bot"""
        if isinstance(message.channel, discord.channel.DMChannel) and message.author != self.user:
            await self.answer(message)

    async def on_reaction_add(self, reaction, user):
        """Handles query messages triggered by emoji from user."""
        if user != self.user:
            if str(reaction.emoji) == "❓" and reaction.count == 1:
                await self.answer(reaction.message)


if __name__ == "__main__":
    intents = discord.Intents.all()
    client = MyClient(intents=intents)
    client.run(args.discord_key)
