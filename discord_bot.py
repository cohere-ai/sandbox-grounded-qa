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
import asyncio

from qa.bot import GroundedQaBot

parser = argparse.ArgumentParser(description="A grounded QA bot with cohere and google search")
parser.add_argument("--cohere_api_key", type=str, help="api key for cohere", required=True)
parser.add_argument("--serp_api_key", type=str, help="api key for serpAPI", required=True)
parser.add_argument("--discord_key", type=str, help="api key for discord bot", required=True)
parser.add_argument("--feedback_tag", type=str, help="tag for cohere feedback", required=True)
parser.add_argument("--verbosity", type=int, default=0, help="verbosity level")
args = parser.parse_args()

bot = GroundedQaBot(args.cohere_api_key, args.serp_api_key)


class Fix(discord.ui.Modal):

    def __init__(self, id, button, view):
        super().__init__(title="desired output")  # Modal title
        self.id = id
        self.button = button
        self.view = view

        # Create a text input and add it to the modal
        self.text = discord.ui.InputText(
            label="Desired Output:",
            style=discord.InputTextStyle.paragraph,
        )
        self.add_item(self.text)

    async def callback(self, interaction: discord.Interaction) -> None:
        print(self.id)
        print(self.text)
        self.button.disabled = True
        self.button.emoji = "🖊️"
        bot.feedback(self.id, False, tag=str(self.text))
        await interaction.response.edit_message(view=self.view)


class FeedbackButtons(discord.ui.View):

    def __init__(self, id, *, timeout=60):
        super().__init__(timeout=timeout)
        self.id = id

    @discord.ui.button(label="Good", style=discord.ButtonStyle.green, custom_id="good")
    async def good_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        bot.feedback(self.id, True)
        [x for x in self.children if x.custom_id == "bad"][0].disabled = True
        button.disabled = True
        button.emoji = "👍"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Bad", style=discord.ButtonStyle.red, custom_id="bad")
    async def bad_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        bot.feedback(self.id, False, tag=args.feedback_tag)
        [x for x in self.children if x.custom_id == "good"][0].disabled = True
        button.disabled = True
        button.emoji = "👎"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Fix", style=discord.ButtonStyle.grey, custom_id="fix")
    async def fix_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(Fix(self.id, button, self))


class FullFeedbackButtons(FeedbackButtons):

    def __init__(self, query, search_results, id, *, timeout=60):
        super().__init__(id, timeout=timeout)
        self.search_query = query
        self.search_results = search_results

    async def get_or_create_thread(self, interaction):
        thread = interaction.guild.get_thread(interaction.message.id)
        if not thread:
            thread = await interaction.message.create_thread(name="Search")
        return thread

    @discord.ui.button(label="Search Results", style=discord.ButtonStyle.blurple, custom_id="search_results")
    async def search_results_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        button.disabled = True
        button.emoji = "📰"
        await interaction.response.edit_message(view=self)

        thread = await self.get_or_create_thread(interaction)

        embed = discord.Embed(title="Search Query:", description=self.search_query.text, color=discord.Colour.blurple())
        await thread.send(embed=embed, view=FeedbackButtons(self.search_query.id))

        text = "\n\n".join([s[1] + "\n" + s[0] for s in self.search_results])[:4096]
        embed = discord.Embed(title="Search Results:", description=text, color=discord.Colour.blurple())
        await thread.send(embed=embed)


class GroundedQAClient(discord.Client):

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

            answer, search_query, search_results = bot.answer(message.clean_content, verbosity=2, n_paragraphs=3)

            await message.channel.send(answer.text, view=FullFeedbackButtons(search_query, search_results, answer.id))

    async def on_message(self, message):
        """Handles query messages triggered by direct messages to the bot"""
        if isinstance(message.channel, discord.channel.DMChannel) and message.author != self.user:
            await self.answer(message)

    async def on_reaction_add(self, reaction, user):
        """Handles query messages triggered by emoji from user."""
        if user != self.user:
            if str(reaction.emoji) == "❓" and reaction.count == 1:
                await self.answer(reaction.message)

    async def on_disconnect(self):
        await self.connect()


async def main():
    intents = discord.Intents.all()
    client = GroundedQAClient(intents=intents)
    try:
        await client.start(args.discord_key)
    except Exception as e:
        print(f"Exception caught: {e}")


if __name__ == "__main__":
    asyncio.run(main())
