# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

# this is a cli demo of you the bot. You can run it and ask questions directly in your terminal

import argparse

from qa.bot import GroundedQaBot

parser = argparse.ArgumentParser(description="A grounded QA bot with cohere and google search")
parser.add_argument("--cohere_api_key", type=str, help="api key for cohere", required=True)
parser.add_argument("--serp_api_key", type=str, help="api key for serpAPI", required=True)
parser.add_argument("--verbosity", type=int, default=0, help="verbosity level (0, 1, 2), whereas 0 is default")
args = parser.parse_args()

bot = GroundedQaBot(args.cohere_api_key, args.serp_api_key)

if __name__ == "__main__":
    while True:
        question = input("question: ")
        reply = bot.answer(question, verbosity=args.verbosity, n_paragraphs=2)
        print("answer: " + reply)
