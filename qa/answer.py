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


def answer(question, context, co):
    """Answer a question given some context."""

    prompt = (
        f'read the paragraph below and answer the question, if the question cannot be answered based on the context alone, write "sorry i had trouble answering this question, based on the information i found\n'
        f"\n"
        f"Context:\n"
        f"{ context }\n"
        f"\n"
        f"Question: { question }\n"
        "Answer:")
    stop_sequences = []
    prompt = "".join(co.tokenize(text=prompt).token_strings[-1900:])
    prediction = co.generate(model="command-52b-v5-dec22-eeayj60s",
                             prompt=prompt,
                             max_tokens=100,
                             temperature=0.3,
                             end_sequences=stop_sequences,
                             num_generations=1,
                             return_likelihoods="GENERATION")

    return prediction[0]


def answer_with_search(question, co, serp_api_token, url=None, n_paragraphs=1, verbosity=0):
    """Generates completion based on search results."""

    paragraphs, paragraph_sources = get_results_paragraphs_multi_process(question, serp_api_token, url=url)
    if not paragraphs:
        return ("", "")
    sample_answer = get_sample_answer(question, co)

    search_results = embedding_search(paragraphs, paragraph_sources, sample_answer, co, model="multilingual-22-12")

    if verbosity > 1:
        pprint_results = "\n".join([r[0] for r in search_results])
        pretty_print("OKGREEN", f"all search result context: {pprint_results}")

    search_results = search_results[-n_paragraphs:]

    context = "\n".join([r[0] for r in search_results])

    if verbosity:
        pretty_print("OKCYAN", "relevant result context: " + context)

    response = answer(question, context, co)

    return (response, search_results)
