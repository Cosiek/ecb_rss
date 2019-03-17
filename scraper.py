#!/usr/bin/env python3.6
# encoding: utf-8

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from urllib.parse import urlparse, urlunparse
from xml.etree import ElementTree

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


async def get_feed_data(url, session):
    status, txt = await get_url_content(url, session)
    if status != 200:
        # TODO: handle this somehow
        return

    data = []
    tree = ElementTree.fromstring(txt)
    # There should be a better way to do this
    for item in tree.findall("{http://purl.org/rss/1.0/}item"):
        data_dct = {}
        for entry in item:
            if entry.tag.endswith('statistics'):
                for stats_entry in entry:
                    if stats_entry.tag.endswith('exchangeRate'):
                        # exchange rate entry - aka ere
                        for ere in stats_entry:
                            if ere.tag.endswith('value'):
                                data_dct['value'] = Decimal(ere.text)
                            elif ere.tag.endswith('targetCurrency'):
                                data_dct['targetCurrency'] = ere.text
            elif entry.tag.endswith('date'):
                data_dct['date'] = parse_date(entry.text)
        data.append(data_dct)
    return data


def parse_date(date_str):
    # get rid of ":" from time zone part, so that strptime can read it
    dt = datetime.strptime(date_str[:-3] + date_str[-2:], '%Y-%m-%dT%H:%M:%S%z')
    return dt


async def scrap(url, session):
    # get content of ecb rss page
    status, txt = await get_url_content(url, session)
    if status != 200:
        # TODO: handle this somehow (maybe keep knocking)
        return
    # get rss links list
    links = get_links(url, txt)
    # read data from rss
    data = await asyncio.gather(*[get_feed_data(l, session) for l in links])
    # filter out failed requests
    data = filter(None, data)
    return data


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    while True:
        start_time = datetime.now()
        session = aiohttp.ClientSession()
        # get feed data
        scrapped_data = loop.run_until_complete(
            scrap('https://www.ecb.europa.eu/home/html/rss.en.html', session)
        )
        loop.run_until_complete(session.close())
        # wait till next run
        # TODO: I assume this should run once a day at some given time.
        wait_time = start_time + timedelta(hours=24) - datetime.now()
        loop.run_until_complete(asyncio.sleep(wait_time.total_seconds()))
