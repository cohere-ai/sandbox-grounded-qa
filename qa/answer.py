# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import numpy as np

from qa.model import get_sample_answer
from qa.search import embedding_search, get_results_paragraphs_multi_process
from qa.util import pretty_print


def trim_stop_sequences(s, stop_sequences):
    """Remove stop sequences found at the end of returned generated text."""

    for stop_sequence in stop_sequences:
        if s.endswith(stop_sequence):
            return s[:-len(stop_sequence)]
    return s


def answer(question, context, co, model, chat_history=""):
    """Answer a question given some context."""

    prompt = ("This is an example of question answering based on a text passage:\n "
              f"Context:-{context}\nQuestion:\n-{question}\nAnswer:\n-")
    if chat_history:
        prompt = ("This is an example of factual question answering chat bot. It "
                  "takes the text context and answers related questions:\n "
                  f"Context:-{context}\nChat Log\n{chat_history}\nbot:")

    stop_sequences = ["\n"]

    num_generations = 4
    prompt = "".join(co.tokenize(text=prompt).token_strings[-1900:])
    prediction = co.generate(model=model,
                             prompt=prompt,
                             max_tokens=100,
                             temperature=0.3,
                             stop_sequences=stop_sequences,
                             num_generations=num_generations,
                             return_likelihoods="GENERATION")
    generations = [[
        trim_stop_sequences(prediction.generations[i].text.strip(), stop_sequences),
        prediction.generations[i].likelihood
    ] for i in range(num_generations)]
    generations = list(filter(lambda x: not x[0].isspace(), generations))
    response = generations[np.argmax([g[1] for g in generations])][0]
    return response.strip()


def answer_with_search(question,
                       co,
                       serp_api_token,
                       chat_history="",
                       model="xlarge",
                       embedding_model="small",
                       url=None,
                       n_paragraphs=1,
                       verbosity=0):
    """Generates completion based on search results."""

    paragraphs, paragraph_sources = get_results_paragraphs_multi_process(question, serp_api_token, url=url)
    if not paragraphs:
        return ("", "", "")
    sample_answer = get_sample_answer(question, co)

    results = embedding_search(paragraphs, paragraph_sources, sample_answer, co, model=embedding_model)

    if verbosity > 1:
        pprint_results = "\n".join([r[0] for r in results])
        pretty_print("OKGREEN", f"all search result context: {pprint_results}")

    results = results[-n_paragraphs:]
    context = "\n".join([r[0] for r in results])

    if verbosity:
        pretty_print("OKCYAN", "relevant result context: " + context)

    response = answer(question, context, co, chat_history=chat_history, model=model)

    return (response, [r[1] for r in results], [r[0] for r in results])
