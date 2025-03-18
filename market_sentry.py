import requests
import smtplib
import re
import json
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import *
from io import BytesIO
from PyPDF2 import PdfReader
from google import genai

headers = {
'Referer': 'https://www.bseindia.com/',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
}


today = datetime.now().strftime('%Y%m%d')
# today = '20250317'

scrips = {}
if os.path.exists('scrips.json'):
    with open('scrips.json', 'r') as f:
        scrips = json.load(f)

def get_scrip_for_symbol(symbol):
    if symbol in scrips:
        # print(f"Found scrip for {symbol} in cache")
        return scrips[symbol]
    url = f'https://api.bseindia.com/BseIndiaAPI/api/PeerSmartSearch/w?Type=SS&text={symbol}'
    response = requests.request("GET", url, headers=headers)
    results = response.text.split("</li>")
    pattern = "liclick\\('([0-9]+)'"
    for result in results:
        if f"<strong>{symbol}</strong>" not in result:
            continue
        match = re.search(pattern, result)
        scrip = match.group(1)
        scrips[symbol] = scrip
        with open('scrips.json', 'w') as f:
            json.dump(scrips, f)
        return scrip

# Function to fetch PDF documents from BSE's site
def fetch_updates(symbol):
    scrip = get_scrip_for_symbol(symbol)
    # print(f"Scrip for {symbol}: {scrip}")
    # print(f"Collecting updates for {symbol}")
    url = f'https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w?pageno=1&strCat=-1&strPrevDate={today}&strScrip={scrip}&strSearch=P&strToDate={today}&strType=C&subcategory=-1'
    response = requests.request("GET", url, headers=headers)
    url_prefix = "https://www.bseindia.com/xml-data/corpfiling/AttachLive/"
    if response.status_code == 200:
        data = response.json()
        updates = [{"headline":entry.get('HEADLINE'),"url":url_prefix + entry.get('ATTACHMENTNAME')} for entry in data.get('Table', []) if entry.get('NSURL') and entry.get('HEADLINE')]
        return updates
    return []

def get_pdf_text(url):
    fileName = url.split('/')[-1]
    if os.path.exists(f'cache/{today}/{fileName}.txt'):
        # print(f'Found cached text for {url}')
        with open(f'cache/{today}/{fileName}.txt', 'r') as f:
            return f.read()

    # print(f'Fetching PDF from {url}')
    response = requests.request("GET", url, headers=headers)
    if response.status_code == 200:
        pdf_file = BytesIO(response.content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        os.makedirs(f'cache/{today}', exist_ok=True)
        text = text if text else "No text found in PDF"
        with open(f'cache/{today}/{fileName}.txt', 'w') as f:
            f.write(text)
        return text
    else:
        print(f'Failed to fetch PDF from {url} with status code {response.status_code}')
        return None

def get_combined_pdf_text(all_updates):
    combined_text = ""
    for symbol, updates in all_updates.items():
        # print(f'Combining pdf text for {symbol}')
        combined_text += f'ANNOUNCEMENTS FROM {symbol}'.center(100, '-') + '\n\n'
        for update in updates:
            text = get_pdf_text(update['url'])
            if text:
                combined_text += f'''
{"HEADLINE".center(50, '-')}
{update['headline']}
{"CONTENT".center(50, '-')}
{text}
{"END OF CONTENT".center(50, '-')}

'''
        combined_text += '\n\n'
    return combined_text


# Function to summarize PDF documents using Google GenAI
def summarize_updates(updates):
    client = genai.Client(api_key=GOOGLE_GENAI_API_KEY)
    combined_text = get_combined_pdf_text(updates)
    if combined_text.startswith("```html"):
        combined_text = combined_text[7:-3]
    # print(f'Generating summary for:\n{combined_text}')
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            f'''The below are the Announcements from a Listed Company. Summarize the important stuff from an inverstors' perspective.
            Be crisp and clear. Use as few words as possible but make sure you cover the important points. 
            At the end, add a few lines conveying your opinion on the company's future prospects.
            Format text using HTML tags if necessary.
             
              ${combined_text}'''
        ]
    )
    # print(f'Summary response: {response}')
    return response.text

# Function to send email with the summary
def send_email(summary):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = 'Daily Market Summary'
    msg.attach(MIMEText(summary, 'plain'))

    server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
    server.starttls()
    server.login(EMAIL_SMTP_USERNAME, EMAIL_SMTP_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, text)
    server.quit()

# Main function to orchestrate the process
def main():
    all_updates = {}
    for symbol in SYMBOLS:
        updates = fetch_updates(symbol)
        if len(updates) > 0:
            all_updates[symbol] = updates
    
    if len(all_updates) > 0:
        summary = summarize_updates(all_updates)
        print(f'Summary: {summary}')
    send_email(summary)

# Test function to verify the scraped data
def test_fetch_pdfs():
    all_updates = {}
    for symbol in SYMBOLS:
        updates = fetch_updates(symbol)
        # print(f'Updates for {symbol}: {updates}')
        if len(updates) > 0:
            all_updates[symbol] = updates
    # print(f'All updates: {all_updates}')

    if len(all_updates) > 0:
        # print(f'Combined text for {scrip}:\n{get_combined_pdf_text(updates)}')
        summary = get_combined_pdf_text(all_updates)
        with open('summary.txt', 'w') as f:
            f.write(summary)
        # print("Summary written to summary.txt")
    else:
        print(f'No updates found for {SYMBOLS}')

if __name__ == '__main__':
    main()
