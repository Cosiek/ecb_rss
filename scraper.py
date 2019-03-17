#!/usr/bin/env python3.6
# encoding: utf-8

import asyncio

import aiohttp


async def get_url_content(url, session):
    async with session.get(url) as resp:
        if resp.status == 200:
            txt = await resp.text()
            return resp.status, txt
        return resp.status, ''


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    while True:
        session = aiohttp.ClientSession()
        # get feed data
        loop.run_until_complete(
            get_url_content(
                'https://www.ecb.europa.eu/home/html/rss.en.html', session)
        )
        loop.run_until_complete(session.close())
