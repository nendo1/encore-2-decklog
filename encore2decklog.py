import asyncio
from playwright.async_api import async_playwright
from collections import Counter
import sys

async def getEncoreDecks(url):
    async with async_playwright() as playw:
        browser = await playw.chromium.launch(headless=True)
        page = await browser.new_page()
        async with page.expect_response(lambda r: "/api/deck/" in r.url) as response_info:
            await page.goto(url, wait_until="networkidle")
        response = await response_info.value
        return await response.json()

    
def convertEncore2Decklog(deck_data):
    #hardcoded attributes if encore deck changes them need to update
    language = -1
    decklog_deck = []
    cards = deck_data['cards']
    for card in cards:
        if language == -1:
            language = card['lang']

        if card['lang'] != language:
            print("Failed!")
            print("Mixed language decks are not supported!")
            exit()

        decklog_deck.append(card['cardcode'].strip())
    
    counts = Counter(decklog_deck)

    cardcodes = list(counts.keys())
    cardquantity = list(counts.values())

    return cardcodes, cardquantity, language

async def postRequestDecklog(payload, language):
    async with async_playwright() as playw:
        browser = await playw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL_dict[language], wait_until="networkidle")
        result = await page.evaluate("""async ({payload, url}) => { const res = await fetch(url, {method: "POST", headers: {"Content-Type": "application/json;charset=utf-8"}, body: JSON.stringify(payload)}); return {status: res.status, body: await res.json()};}""", {"payload": payload, "url": API_dict[language]})
    return result

async def prepRequest(cardcode, cardq, language):
        title = 'test'
        if sys.argv[2]:
            title = str(sys.argv[2])

        setcode = cardcode[0].split("/")[0]
        setcode = "##" + setcode.strip() + "##"
        if language == "EN":
            request = request_template
        else:
            print("Failed!")
            print("JP uploads not yet supported!")
            exit()
            #request = request_template_JP
        request['title'] = title
        request['no'] = cardcode
        request['num'] = cardq
        request['deck_param2'] = str(setcode)
        return request

def main():
    encoredecks = sys.argv[1]
    if encoredecks != "":
        print('Fetching encore decks...  ', end='', flush=True)

        deck_data = asyncio.run(getEncoreDecks(encoredecks))

        print('Success!')
        print('Converting to suitable decklog format...  ', end='')

        cardcode, cardq, language = convertEncore2Decklog(deck_data)
        
        new_request_template = asyncio.run(prepRequest(cardcode, cardq, language))

        print('Success!')
        print('Uploading to decklog...  ', end='')

        response = asyncio.run(postRequestDecklog(new_request_template, language))

        if(response['status'] == 200):
            print('Success!')

            print('Decklist should be available at:')
            print(str(URL_dict[language])+"view/"+str(response['body']['deck_id']))
        else:
            print('Failed!')
            print('Something went wrong uploading')
            print("Response: "+ str(response['status']))

    else:
        print('Something went wrong!!')

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

request_template_JP = {"id":"","deck_id":"","title":"mycopy","post_deckrecipe":1,"memo":"","deck_param1":"N","deck_param2":"##IMS##IAS##","add_param1":"","add_param2":"","no":["IMS/S93-059","IMS/S93-086","IMS/S93-087","IMS/S93-100","IMS/S93-067","IMS/S93-076","IMS/S93-096","IAS/S93-045","IMS/S93-065BNP","IAS/S93-010","IMS/S93-007","IMS/S93-069BNP","IMS/S93-052","IMS/S93-044","IMS/S93-048","IAS/S61-106","IMS/S93-088","IMS/S93-110BNP","IMS/S93-P05","IMS/S93-119","IMS/S93-122"],"num":[1,2,4,1,2,2,1,4,1,3,1,3,1,3,2,2,4,4,1,4,4],"sub_no":[],"sub_num":[],"p_no":[],"p_num":[],"p_slot":[],"has_session":False,"token_id":"","token":""}

URL_dict = {
    "JP": "https://decklog.bushiroad.com/",
    "EN": "https://decklog-en.bushiroad.com/"
}

API_dict = {
    "JP": "https://decklog.bushiroad.com/system/app/api/publish/2",
    "EN": "https://decklog-en.bushiroad.com/system/app/api/publish/2"
}

main()