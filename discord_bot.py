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
from discord.ext import commands
from discord import ActionRow, Button, ButtonStyle

from qa.bot import GroundedQaBot

parser = argparse.ArgumentParser(description="A grounded QA bot with cohere and google search")
parser.add_argument("--cohere_api_key", type=str, help="api key for cohere", required=True)
parser.add_argument("--serp_api_key", type=str, help="api key for serpAPI", required=True)
parser.add_argument("--discord_key", type=str, help="api key for discord bot", required=True)
parser.add_argument("--feedback_tag", type=str, help="tag for cohere feedback", required=True)
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
            reply, source_urls, source_texts, id = bot.answer(message.clean_content, verbosity=2, n_paragraphs=3)

            class Buttons(discord.ui.View):

                def __init__(self, *, timeout=60):
                    super().__init__(timeout=timeout)

                @discord.ui.button(label="Source", style=discord.ButtonStyle.blurple, custom_id="urls")  # or .primary
                async def source_url_button(self, button: discord.ui.Button, interaction: discord.Interaction):
                    button.disabled = True
                    embed = discord.Embed(title="Sources:",
                                          description="\n".join(list(set(source_urls))) + "\n\n" +
                                          "\n".join(source_texts),
                                          color=discord.Colour.blurple())
                    await interaction.response.edit_message(view=self)
                    await interaction.message.reply(embed=embed)

                @discord.ui.button(label="Good", style=discord.ButtonStyle.green, custom_id="good")  # or .success
                async def good_button(self, button: discord.ui.Button, interaction: discord.Interaction):
                    bot.feedback(id, True)
                    [x for x in self.children if x.custom_id == "bad"][0].disabled = True
                    button.disabled = True
                    embed = discord.Embed(title="Feedback", description="saved as good", color=discord.Colour.green())
                    await interaction.response.edit_message(view=self)
                    await interaction.message.reply(embed=embed)

                @discord.ui.button(label="bad", style=discord.ButtonStyle.red, custom_id="bad")  # or .danger
                async def bad_button(self, button: discord.ui.Button, interaction: discord.Interaction):
                    bot.feedback(id, False, tag=args.feedback_tag)
                    [x for x in self.children if x.custom_id == "good"][0].disabled = True
                    button.disabled = True
                    embed = discord.Embed(title="Feedback", description="saved as bad", color=discord.Colour.red())
                    await interaction.response.edit_message(view=self)
                    await interaction.message.reply(embed=embed)

            await message.channel.send(reply, view=Buttons())
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
