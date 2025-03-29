import requests
from PyPDF2 import PdfReader
from io import BytesIO
from datetime import datetime
import json
from typing import Dict
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession

today = datetime.now().strftime('%Y%m%d')
# today = "20250327"
BSE_API_URL = f'https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w?pageno=1&strCat=-1&strPrevDate={today}&strScrip=[scrip]&strSearch=P&strToDate={today}&strType=C&subcategory=-1'
ATTACHMENT_URL_PREFIX = 'https://www.bseindia.com/xml-data/corpfiling/AttachLive/'
HEADERS = {
    'Referer':
    'https://www.bseindia.com/',
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
}


def collect_all_news(watchlist: list[str]) -> Dict[str, list]:
    all_news = {}
    with FuturesSession() as session:
        futures = {
            session.get(BSE_API_URL.replace('[scrip]', str(scrip)), headers=HEADERS) : (scrip, symbol) 
            for scrip, symbol in watchlist.items()
        }
        counter = 1
        total_len = len(futures)
        for future in as_completed(futures.keys()):
            scrip, symbol = futures[future]
            print(f"Collected {symbol} - {counter}/{total_len}")
            counter += 1
            try:
                response = future.result()
                if response.status_code != 200:
                    print(f'Received status code {response.status_code} for {scrip}')
                    continue
                data = response.json()
                news = data.get('Table', [])
                print(f'Fetched news for {symbol} - {len(news)} news items')

                if news and len(news) > 0:
                    all_news[symbol] = news
            except Exception as e:
                print(f'Error in thread: {e}')
        
        # executor.shutdown(wait=False, cancel_futures=True)
        print(f'Fetched news for all scrips in watchlist')
    return fetch_pdf_content(all_news)


def fetch_pdf_content(all_news: dict) -> dict:
    with FuturesSession() as session:
        futures = {
            session.get(ATTACHMENT_URL_PREFIX + news.get('ATTACHMENTNAME'), headers=HEADERS) : (scrip, news)
            for scrip, news_list in all_news.items()
            for news in news_list
        }
        counter = 1
        total_len = len(futures)
        for future in as_completed(futures.keys()):
            scrip, news = futures[future]
            print(f"Fetched PDF content for {scrip} - {counter}/{total_len}")
            counter += 1
            try:
                response = future.result()
                if response.status_code != 200:
                    print(f'Received status code {response.status_code} for {scrip}')
                    continue
                pdf_file = BytesIO(response.content)
                reader = PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                news['pdf_content'] = text
            except Exception as e:
                print(f'Error in thread: {e}')
    return all_news


def fetch_watchlist_updates(watchlist: dict[str, str]) -> Dict[str, str]:
    all_news_for_today = collect_all_news(watchlist)
    with open('news.json', 'w') as f:
        f.write(json.dumps(all_news_for_today))
    news_details = {}
    for stock_symbol, news_list in all_news_for_today.items():
        for news in news_list:
            pdf_content = news.get('pdf_content', 'Unable to fetch PDF content')
            formatted_text = f'''
{"HEADLINE".center(50, '-')}
{news.get('HEADLINE')}
{"CONTENT".center(50, '-')}
{pdf_content}
{"END OF CONTENT".center(50, '-')}

'''
            if stock_symbol not in news_details:
                news_details[stock_symbol] = f'\n{f"ANNOUNCEMENTS FROM {news.get('SLONGNAME')}".center(100, '-')}\n\n{formatted_text}\n'
            else:
                news_details[stock_symbol] = f'\n{news_details[stock_symbol]}\n\n{formatted_text}\n\n'
    return news_details


def download_and_extract_text(file_name: str) -> str:
    url = ATTACHMENT_URL_PREFIX + file_name
    response = requests.get(url, headers={'host': 'www.bseindia.com', 'referer': 'https://www.bseindia.com/'})
    if response.status_code == 200:
        pdf_file = BytesIO(response.content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    return "Unable to fetch PDF content"


def constructWatchlist(symbols: list[str], WATCHLIST) -> dict[str, str]:
    watchlist = {}
    for symbol in symbols:
        if symbol in WATCHLIST:
            watchlist[symbol] = WATCHLIST.get(symbol)
            continue
        watchlist[symbol] = getSCRIP(symbol)
    return watchlist


def getSCRIP(symbol: str) -> str:
    response = requests.get(f'https://api.bseindia.com/BseIndiaAPI/api/GetScripHeaderData/w?Debtflag=&scripcode={symbol}&seriesid=')
    if response.status_code == 200:
        data = response.json()
        return data.get('ScripCode', '')
    return ''