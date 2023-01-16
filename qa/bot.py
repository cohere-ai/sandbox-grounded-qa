# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

from sys import settrace

import cohere

from qa.answer import answer_with_search
from qa.model import get_contextual_search_query
from qa.util import pretty_print


class GroundedQaBot():
    """A class yielding Grounded question-answering conversational agents."""

    def __init__(self, cohere_api_key, serp_api_key):
        self._cohere_api_key = cohere_api_key
        self._serp_api_key = serp_api_key
        self._chat_history = []
        self._co = cohere.Client(self._cohere_api_key)

    @property
    def chat_history(self):
        return self._chat_history

    def set_chat_history(self, chat_history):
        self._chat_history = chat_history

    def answer(self, question, verbosity=0, n_paragraphs=1, url=None):
        """Answer a question, based on recent conversational history."""

        self.chat_history.append("user: " + question)

        history = "\n".join(self.chat_history[-6:])
        question = get_contextual_search_query(history, self._co, verbosity=verbosity)

        answer, search_results = answer_with_search(question.text,
                                                    self._co,
                                                    self._serp_api_key,
                                                    verbosity=verbosity,
                                                    url=url,
                                                    n_paragraphs=n_paragraphs)

        self._chat_history.append("bot: " + answer.text)

        return (answer, question, search_results)

    def feedback(self, id, accepted, tag="grounded-qa-bot"):
        f = self._co.feedback(id=id, feedback=tag, accepted=accepted)
        print(f)
