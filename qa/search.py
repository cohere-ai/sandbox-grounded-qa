# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import os
import sys
import urllib.request
from functools import lru_cache
from multiprocessing import Pool, TimeoutError

import numpy as np
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

import time
import asyncio
from concurrent.futures import ProcessPoolExecutor
import concurrent.futures

from qa.util import pretty_print


def blockPrint():
    """Calling this function stops the serpAPI from print to stdout."""

    sys.stdout = open(os.devnull, "w")


def enablePrint():
    """This function undos blockPrint, restoring standard stdout behavior."""

    sys.stdout = sys.__stdout__


def cosine_similarity(a, b):
    """Compute the cosine similarity between vectors a and b."""

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


@lru_cache(maxsize=256)
def serp_api_google_search(search_term, serp_api_token, url):
    """Search Google based on a query, a return an object containing results.

    Returns:
        GoogleSearch object with the results of the search.
    """

    q = search_term
    if url:
        q = f"site:{url} {search_term}"
    params = {
        "api_key": serp_api_token,
        "engine": "google",
        "q": q,
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en",
        "num": "5"
    }
    blockPrint()
    results = GoogleSearch(params)
    print("WHAT")
    enablePrint()
    return results


def serp_api_search(search_term, serp_api_token, url):
    """Iterates over organic results and top stories.
    
    Returns: 
        a list of tuples of the form (url, text)
    """

    response = serp_api_google_search(search_term, serp_api_token, url)
    results = response.get_dict()

    response_urls = []
    for key in ["organic_results", "top_stories"]:
        if key in results:
            i = 0
            while i < len(results[key]):
                url = results[key][i]["link"]
                text = ""
                if "snippet" in results[key][i]:
                    text = results[key][i]["snippet"]
                i += 1
                response_urls.append([url, text])
    return response_urls


def open_link(url, timeout):
    """Follow a link and return its contents.

    Returns:
        html of the page
    """

    user_agent = "Mozilla/5.0"

    headers = {
        "User-Agent": user_agent,
    }

    request = urllib.request.Request(url, None, headers)  # The assembled request
    response = urllib.request.urlopen(request, timeout=timeout)
    return response


def paragraphs_from_html(body):
    """Extract a list of paragraphs from the html."""

    soup = BeautifulSoup(body, "html.parser")
    paragraphs = []
    for data in soup.find_all("p"):
        tag = data.get_text()
        if not tag.isspace() and len(tag.split()) > 10:
            paragraphs.append(tag)
    return paragraphs


def get_paragraphs_text_from_url(k):
    """Extract a list of paragraphs from the contents pointed to by an url."""

    i, search_result_url = k
    try:
        html = open_link(search_result_url, 3)
        return paragraphs_from_html(html)
    except Exception as e:
        pretty_print("FAIL", f"ERROR: Page '{search_result_url}' could not be loaded! Exception message: {e}")
        return []


# Retrieve a single page and report the URL and contents
def get_html_from_url(url, timeout):
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        return conn.read()


def get_paragraphs_from_links_threaded(urls):
    # We can use a with statement to ensure threads are cleaned up promptly
    all_url_paragraphs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(open_link, url, 3): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                paragraphs = paragraphs_from_html(data)
                print('%r page is %d paragraphs' % (url, len(paragraphs)))
                print(paragraphs)
                all_url_paragraphs.append([url, paragraphs])
    return all_url_paragraphs


def get_results_paragraphs_multi_process(search_term, serp_api_token, url=None):
    """Given a query, retrieve relevant paragraphs from the search results.
    
    This function will first search for documents matching a query. Then, for
    each document amongst the most relevant documents in that set, it will find
    the paragraph which most closely matches the query, and aggregate those in
    a list, which is returned.
    """

    results = serp_api_search(search_term, serp_api_token, url)

    if not results:
        return [], []

    urls = [r[0] for r in results][:4]

    #pool = Pool(processes=4)
    #multiple_results = [pool.apply_async(get_paragraphs_text_from_url, args=(url,)) for url in indexed_urls]
    #url_paragraphs = [async_handle_timeout(res) for res in multiple_results]
    #pool.terminate()
    all_url_paragraphs = get_paragraphs_from_links_threaded(urls)
    paragraphs = []
    paragraph_sources = []
    for i in range(len(all_url_paragraphs)):
        url, url_paragraphs = all_url_paragraphs[i]
        paragraphs += url_paragraphs
        paragraph_sources += [url] * len(url_paragraphs)
    return paragraphs, paragraph_sources


def embedding_search(paragraphs, paragraph_sources, search_term, co, model="multilingual-22-12"):
    """Embed paragraphs and search for the closest ones to a query."""

    embeddings = co.embed(texts=paragraphs + [search_term], model=model, truncate="LEFT").embeddings
    paragraph_embeddings = embeddings[:-1]
    search_embedding = embeddings[-1]
    distances = [cosine_similarity(x, search_embedding) for x in paragraph_embeddings]
    return sorted(list(zip(paragraphs, paragraph_sources, distances)), key=lambda x: x[2])
