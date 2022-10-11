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

# Grounded Question Answering — A Cohere Sandbox Project

This is a cohere API powered contextualized factual question answering bot! 

It responds to question in discord by understanding the context, google 
searching what it believes to be the appropriate question, finding relevant 
information on the google result pages and then answering the question based on 
what it found.

## Installation
1- Clone the repository.

2- Install all the dependencies:

```pip install -r requirements.txt```

4- Running the streamlit demo
Try the demo by running the cli tool

```python3 cli_demo.py --cohere_api_key <API_KEY> --serp_api_key <API_KEY>```

# License
COHERE-GROUNDED-QA has an MIT license, as found in the LICENSE file.


