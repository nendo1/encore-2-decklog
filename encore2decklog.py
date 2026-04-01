import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from collections import Counter
import json
import sys

async def getEncoreDecks(url):
    print('getEncoreDecks')
    async with async_playwright() as playw:
        browser = await playw.chromium.launch(headless=True)
        page = await browser.new_page()
        async with page.expect_response(lambda r: "/api/deck/" in r.url) as response_info:
            await page.goto(url, wait_until="networkidle")
        response = await response_info.value
        browser.close()
        return await response.json()

    
def convertEncore2Decklog(deck_data):
    print('convertencoredecks')
    print(deck_data)
    #hardcoded attributes if encore deck changes them need to update
    decklog_deck = []
    cards = deck_data['cards']
    for card in cards:
        decklog_deck.append(card['cardcode'].strip())
    
    counts = Counter(decklog_deck)

    cardcodes = list(counts.keys())
    cardquantity = list(counts.values())

    return cardcodes, cardquantity

async def postRequestDecklog(payload):
    print('postdecklog')
    async with async_playwright() as playw:
        browser = await playw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://decklog-en.bushiroad.com/", wait_until="networkidle")
        result = await page.evaluate("""async (payload) => { const res = await fetch("https://decklog-en.bushiroad.com/system/app/api/publish/2", {method: "POST", headers: {"Content-Type": "application/json;charset=utf-8"}, body: JSON.stringify(payload)}); return {status: res.status, body: await res.json()};}""", payload)
        browser.close()
    return result

async def prepRequest(cardcode, cardq):
        title = 'test'
        if sys.argv[2] != "":
            title = str(sys.argv[2])

        setcode = cardcode[0].split("/")[0]
        setcode = "##" + setcode.strip() + "##"
        request = request_template
        request['title'] = title
        request['no'] = cardcode
        request['num'] = cardq
        request['deck_param2'] = str(setcode)
        return request

def main():
    encoredecks = sys.argv[1]
    print(encoredecks)
    if encoredecks != "":
        deck_data = asyncio.run(getEncoreDecks(encoredecks))
        cardcode, cardq = convertEncore2Decklog(deck_data)
        request_template = asyncio.run(prepRequest(cardcode, cardq))
        response = asyncio.run(postRequestDecklog(request_template))
        print(response)
    else:
        print('error')

request_template = {
    "id": "",
    "deck_id": "",
    "title": "",
    "memo": "",
    "deck_param1": "N",
    "deck_param2": "##NIK##",
    "add_param1": "",
    "add_param2": "",
    "no": [],
    "num": [],
    "sub_no": [],
    "sub_num": [],
    "p_no": [],
    "p_num": [],
    "p_slot": [],
    "g_no": [],
    "has_session": False,
    "token_id": "",
    "token": ""
}

main()