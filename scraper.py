#!/usr/bin/env python3.6
# encoding: utf-8

import asyncio
from urllib.parse import urlparse, urlunparse

import aiohttp
from pyquery import PyQuery as pq


async def get_url_content(url, session):
    async with session.get(url) as resp:
        if resp.status == 200:
            txt = await resp.text()
            return resp.status, txt
        return resp.status, ''


def get_links(url, txt):
    """
    Get a list of exchange reference rates RSS links.
    """
    parsed = urlparse(url)

    d = pq(txt)
    hrefs = []
    for html_element in d('.rss'):
        href = pq(html_element).attr('href')
        if href.startswith('/rss/fxref-'):
            hrefs.append(urlunparse((parsed[0], parsed[1], href, "", "", "")))
    return hrefs


async def scrap(url, session):
    status, txt = await get_url_content(url, session)
    if status != 200:
        # TODO: handle this somehow (maybe keep knocking)
        return
    links = get_links(url, txt)
    print(links)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    while True:
        session = aiohttp.ClientSession()
        # get feed data
        loop.run_until_complete(
            scrap('https://www.ecb.europa.eu/home/html/rss.en.html', session)
        )
        loop.run_until_complete(session.close())
