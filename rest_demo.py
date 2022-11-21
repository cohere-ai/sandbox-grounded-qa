import time
import logging
import os
import uuid

from flask import abort, Flask, jsonify, request

import argparse

from qa.bot import GroundedQaBot

parser = argparse.ArgumentParser(description="A grounded QA bot with cohere and google search")
parser.add_argument("--cohere_api_key", type=str, help="api key for cohere", required=True)
parser.add_argument("--serp_api_key", type=str, help="api key for serpAPI", required=True)
parser.add_argument("--verbosity", type=int, default=0, help="verbosity level")
args = parser.parse_args()

bot = GroundedQaBot(args.cohere_api_key, args.serp_api_key)

app = Flask(__name__)

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Get answer to question
# curl --request POST --url http://localhost:5007/api/v1/ask --header 'content-type: application/json' --data '{ "question":"When was the fall of Constantinople?" }'
# curl --request POST --url http://localhost:5007/api/v1/ask --header 'content-type: application/json' --data '{ "question":"When was the fall of Constantinople?","site-url":"https://docs.cohere.ai/" }'
# TODO: "site-url":"https://en.wikipedia.org"
@app.route('/api/v1/ask', methods=['POST'])
def getAnswer():
    if not request.json or not 'question' in request.json:
        abort(400)
    question = request.json['question']
    logger.info(f"Get answer to question '{question}' ...")

    site_url = None
    #site_url = "https://en.wikipedia.org"
    if 'site-url' in request.json:
        site_url = request.json['site-url']
    logger.info(f"Provided site URL: {site_url}")

    answer, source_urls, source_texts = bot.answer(question, verbosity=args.verbosity, n_paragraphs=2, url=site_url)

    response = {'answer': answer, 'source_texts': source_texts, 'source_urls': source_urls}
    return jsonify(response), 200

# Health check endpoint
@app.route('/api/v1/health', methods=['GET'])
def checkHealth():
    logger.info("Check health ...")

    response = {'status':'UP','about':'Grounded QA','version':'1.0.0'}
    return jsonify(response), 200
 
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5007)
