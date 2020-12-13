#!/usr/bin/env python3.6
# encoding: utf-8

import asyncio
from datetime import datetime, timedelta
import sqlite3
import time
from urllib.parse import urlparse, urlunparse
from xml.etree import ElementTree

import aiohttp
from pyquery import PyQuery as pq

from rest_endpoint.settings import DATABASES


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

    data_dct = {}
    tree = ElementTree.fromstring(txt)
    # There should be a better way to do this
    for item in tree.findall("{http://purl.org/rss/1.0/}item"):
        dct = {}
        for entry in item:
            if entry.tag.endswith('statistics'):
                for stats_entry in entry:
                    if stats_entry.tag.endswith('exchangeRate'):
                        # exchange rate entry - aka ere
                        for ere in stats_entry:
                            if ere.tag.endswith('value'):
                                dct['value'] = ere.text
                            elif ere.tag.endswith('targetCurrency'):
                                dct['targetCurrency'] = ere.text
            elif entry.tag.endswith('date'):
                dct['date'] = parse_date(entry.text)
        if data_dct.get('date') is None or data_dct['date'] < dct['date']:
            data_dct = dct
    return data_dct


def parse_date(date_str):
    # get rid of ":" from time zone part, so that strptime can read it
    dt = datetime.strptime(date_str[:-3] + date_str[-2:], '%Y-%m-%dT%H:%M:%S%z')
    return dt


async def scrap(url):
    # get content of ecb rss page
    async with aiohttp.ClientSession() as session:
        status, txt = await get_url_content(url, session)
        if status != 200:
            # TODO: handle this somehow (maybe keep knocking)
            return
        # get rss links list
        links = get_links(url, txt)
        # read data from rss
        data = await asyncio.gather(*[get_feed_data(l, session) for l in links])
        # filter out failed requests
        return list(filter(None, data))


def write_data_to_db(data):
    # TODO: switch to async once production ready db is in place
    # get db connection and cursor
    conn = sqlite3.connect(DATABASES['default']['NAME'])
    cur = conn.cursor()
    # insert currencies (if there are any new ones)
    sql = ("INSERT OR IGNORE INTO currency_currency (name) "
           "VALUES (:targetCurrency)")
    cur.executemany(sql, data)
    # insert exchange rates (only if updated)
    sql = ("INSERT INTO currency_exchangerate (value_time, value, currency_id) "
           "SELECT :date, :value, currency_currency.id "
           "FROM currency_currency "
           "LEFT JOIN currency_exchangerate "
           "ON currency_currency.id = currency_exchangerate.currency_id "
           "WHERE currency_currency.name=:targetCurrency "
           "GROUP BY currency_currency.id "
           "HAVING (MAX(currency_exchangerate.value_time) < :date "
           "OR COUNT(currency_exchangerate.id) = 0)")
    # hmm - probably could have done it with ORDER BY and LIMIT 1 - och well.
    cur.executemany(sql, data)
    # save (commit) the changes
    conn.commit()
    # close connection
    conn.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    while True:
        start_time = datetime.now()
        # get feed data
        scrapped_data = loop.run_until_complete(
            scrap('https://www.ecb.europa.eu/home/html/rss.en.html')
        )
        # write data to db
        write_data_to_db(scrapped_data)
        # wait till next run
        # TODO: I assume this should run once a day at some given time.
        wait_time = start_time + timedelta(hours=24) - datetime.now()
        time.sleep(wait_time.total_seconds())
