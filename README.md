```
################################################################################
#    ____      _                     ____                  _ _                 #
#   / ___|___ | |__   ___ _ __ ___  / ___|  __ _ _ __   __| | |__   _____  __  #
#  | |   / _ \| '_ \ / _ \ '__/ _ \ \___ \ / _` | '_ \ / _` | '_ \ / _ \ \/ /  #
#  | |__| (_) | | | |  __/ | |  __/  ___) | (_| | | | | (_| | |_) | (_) >  <   #
#   \____\___/|_| |_|\___|_|  \___| |____/ \__,_|_| |_|\__,_|_.__/ \___/_/\_\  #
#                                                                              #
# This project is part of Cohere Sandbox, Cohere's Experimental Open Source    #
# offering. This project provides a library, tooling, or demo making use of    #
# the Cohere Platform. You should expect (self-)documented, high quality code  #
# but be warned that this is EXPERIMENTAL. Therefore, also expect rough edges, #
# non-backwards compatible changes, or potential changes in functionality as   #
# the library, tool, or demo evolves. Please consider referencing a specific   #
# git commit or version if depending upon the project in any mission-critical  #
# code as part of your own projects.                                           #
#                                                                              #
# Please don't hesitate to raise issues or submit pull requests, and thanks    #
# for checking out this project!                                               #
#                                                                              #
################################################################################
```

**Maintainer:** [nickfrosst](https://github.com/nickfrosst) \
**Project maintained until at least (YYYY-MM-DD):** 2023-01-01

# Grounded Question Answering

This is a [Cohere](https://cohere.ai/) API / Serp API powered contextualized factual question answering bot! 

It responds to question in discord or in the cli by understanding the context, google 
searching what it believes to be the appropriate question, finding relevant 
information on the google result pages and then answering the question based on 
what it found.

## Motivation

Language models are very good at creating sensible answers to complex questions. They are not however very good at creating truthful answers. This is because language models don't have a mechanism for determining truth. They are trained on data from the web, and so pick up statistical correlations between words that make them ok at answering simple and static questions (things like "how far away is the moon from the earth", which has a single and unchanging factual answer), but more nuanced questions or that have factual answers which change over time (things like "who is the prime minister of the UK") are difficult or impossible for language models to answer.  

Google search, on the other hand, is very good at retrieving factual information about these time-sensitive questions. Google makes use of a consensus mechanism for determining truth. Google search results are heavily affected by human user behaviour; which links people click, which links they stay on, and which ones they revisit all affect the ordering of the results. In this way, google determines which links are truthful through user consensus. Google however is quite poor at responding to contextual questions, and at responding to complex questions in natural language.  

This project attempts to join the best of both of these methods; It uses Cohere's large language models to contextualize the given questions and create a natural language answer, but it uses google search as a source of truth.  

## Example 
![image](https://user-images.githubusercontent.com/5508538/199503137-5cb0f15b-c4b5-4458-99d0-21918c0194ff.png)

## Overview Video
Here is a quick [video](https://www.youtube.com/watch?v=DpOQpClVgCw&ab_channel=NickFrosst) demoing the project and talking about ways in which it can be improved.

## Installation and Demo Use

To use this library, you will need:
* A Serp API key, which you can obtain by registering at https://serpapi.com/users/welcome.
* A Cohere API key: sign up for a free key at [https://dashboard.cohere.ai/welcome/register](https://dashboard.cohere.ai/welcome/register?utm_source=github&utm_medium=content&utm_campaign=sandbox&utm_content=groundedqa).
* (Optional) A Discord key, which is the Discord bot token obtained when creating and configuring a Discord bot. See [docs](https://discord.com/developers/docs/topics/oauth2) for more info.

1. Clone the repository.
2. Install all the dependencies
```sh
pip install -r requirements.txt
```
3. Try the demo by running the cli tool
```sh
python3 cli_demo.py --cohere_api_key <API_KEY> --serp_api_key <API_KEY>
```
or with increased verbosity
```sh
python3 cli_demo.py --cohere_api_key <API_KEY> --serp_api_key <API_KEY> --verbosity 2
```
4. (Optional) Run the discord bot demo:  
You can create a discord both with this functionality by creating a bot account with message read and write permissions at https://discord.com/developers then running the following command
```sh
python3 discord_bot.py --cohere_api_key <API_KEY> --serp_api_key <API_KEY> --discord_key <DISCORD_KEY>
```

# Get support
If you have any questions or comments, please file an issue or reach out to us on [Discord](https://discord.gg/co-mmunity).

# Contributors
If you would like to contribute to this project, please read `CONTRIBUTORS.md`
in this repository, and sign the Contributor License Agreement before submitting
any pull requests. A link to sign the Cohere CLA will be generated the first time 
you make a pull request to a Cohere repository.

# License
Grounded Question Answering has an MIT license, as found in the LICENSE file.
